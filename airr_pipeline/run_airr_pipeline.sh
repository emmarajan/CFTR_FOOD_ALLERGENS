#!/usr/bin/env bash
#
# AIRR-seq pipeline (p3482): stages 1-3 in one script.
#   Stage 1  pRESTO preprocessing   -> <sample>-C_atleast-2.fastq   [per sample]
#   Stage 2  Change-O / VDJ         -> <sample>_germ-pass.tsv       [per sample]
#   Stage 3  R aggregation          -> RobjectForSummaryReport.Rdata
#
# Usage:
#   ./run_airr_pipeline.sh --method native            # all samples in gstore
#   ./run_airr_pipeline.sh --method umitools B1 CF2    # named samples only
#
#   --method native    ClusterSets barcode + EstimateError (auto threshold), set ident 0.80
#   --method umitools  umi_tools_dedup.py directional clustering,            set ident 0.58

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GSTORE_ROOT="/srv/gstore/projects/p3482/complete_o6905"
ANALYSIS_ROOT="/srv/GT/analysis/p3482/FN.p3482"
IMAGE="immcantation/suite:4.0.0"
PATH_PREP="/data"                 # container mount point
NPROC=8
DIST=0.15                         # clonal assignment distance
UMITOOLS_ENV="umi_tools"
UMITOOLS_DEDUP="$SCRIPT_DIR/umi_tools_dedup.py"
R_DATAGEN="$SCRIPT_DIR/AIRR_seq_data_generation_FN.R"

# In-container primers / references (shipped in the immcantation image)
P_R1_PRIMERS="/usr/local/share/protocols/AbSeq/AbSeq_R1_Human_IG_Primers.fasta"
P_R2_TS="/usr/local/share/protocols/AbSeq/AbSeq_R2_TS.fasta"
P_CREGION="/usr/local/share/protocols/AbSeq/AbSeq_Human_IG_InternalCRegion.fasta"
REF_IGV="/usr/local/share/igblast/fasta/imgt_human_ig_v.fasta"

# --- args ---
METHOD=""
SAMPLES=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --method) METHOD="$2"; shift 2 ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        -*) echo "Unknown option: $1" >&2; exit 1 ;;
        *) SAMPLES+=("$1"); shift ;;
    esac
done

if [[ "$METHOD" != "native" && "$METHOD" != "umitools" ]]; then
    echo "ERROR: --method must be 'native' or 'umitools' (got '${METHOD}')." >&2
    exit 1
fi

if [[ ${#SAMPLES[@]} -eq 0 ]]; then
    mapfile -t SAMPLES < <(cd "$GSTORE_ROOT" && ls -- *.R1.fastq.gz 2>/dev/null \
                           | sed 's/\.R1\.fastq\.gz$//')
fi
if [[ ${#SAMPLES[@]} -eq 0 ]]; then
    echo "ERROR: no samples found in $GSTORE_ROOT (looked for *.R1.fastq.gz)." >&2
    exit 1
fi

echo "Method : $METHOD"
echo "Samples: ${SAMPLES[*]}"

# Run an Immcantation tool in the image with the current sample mounted ($MOUNT_DIR global).
run_ic() {
    sudo docker run --user "$(id -u):$(id -g)" -v "$MOUNT_DIR:$PATH_PREP:z" "$IMAGE" "$@"
}

# Pull a threshold value from an EstimateError *.tab file (drop the header line).
read_threshold() {
    cut -f2 "$1" | grep -v "THRESHOLD"
}

# Stages 1+2 for one sample. set -e (caller subshell) aborts on first failure.
process_sample() {
    local SAMPLE="$1"
    MOUNT_DIR="/scratch/FN.p3482.$SAMPLE"   # global: read by run_ic
    local SP="$PATH_PREP/$SAMPLE"           # sample prefix, container side
    local SPL="$MOUNT_DIR/$SAMPLE"          # sample prefix, host side
    local SET_IDENT THRESHOLD i

    echo "=== [$SAMPLE] mount: $MOUNT_DIR ==="
    mkdir -p "$MOUNT_DIR"
    cd "$MOUNT_DIR"

    for i in 1 2; do
        gunzip -c "$GSTORE_ROOT/$SAMPLE.R$i.fastq.gz" > "$SAMPLE.R$i.fastq"
    done

    # Stage 1: quality filter, primer masking, pairing
    run_ic FilterSeq.py quality -s "$SP.R1.fastq" -q 20 --outname "$SP-R1" --log "$PATH_PREP/FS1.log"
    run_ic FilterSeq.py quality -s "$SP.R2.fastq" -q 20 --outname "$SP-R2" --log "$PATH_PREP/FS2.log"

    run_ic MaskPrimers.py score -s "$SP-R1_quality-pass.fastq" -p "$P_R1_PRIMERS" \
        --start 0 --mode cut --outname "$SP-R1" --log "$PATH_PREP/MP1.log"
    run_ic MaskPrimers.py score -s "$SP-R2_quality-pass.fastq" -p "$P_R2_TS" \
        --start 17 --barcode --mode cut --maxerror 0.5 --outname "$SP-R2" --log "$PATH_PREP/MP2.log"

    run_ic PairSeq.py -1 "$SP-R1_primers-pass.fastq" -2 "$SP-R2_primers-pass.fastq" \
        --2f BARCODE --coord sra

    # Stage 1: barcode (UMI) clustering, method dependent
    if [[ "$METHOD" == "native" ]]; then
        cat "$SPL-R1_primers-pass_pair-pass.fastq" \
            | seqkit sample -s 420 -n 5000 -o "$SPL-R1_primers-pass_pair-pass_sample.fastq"
        run_ic EstimateError.py barcode -s "$SP-R1_primers-pass_pair-pass_sample.fastq" -f BARCODE
        THRESHOLD=$(read_threshold "$SPL-R1_primers-pass_pair-pass_sample_threshold-barcode.tab")
        echo "Barcode threshold for $SAMPLE: $THRESHOLD"
        echo "$THRESHOLD" > "${SAMPLE}_index_umi_threshold.txt"
        run_ic ClusterSets.py barcode \
            -s "$SP-R1_primers-pass_pair-pass.fastq" "$SP-R2_primers-pass_pair-pass.fastq" \
            -f BARCODE -k INDEX_UMI --ident "$THRESHOLD"
        SET_IDENT=0.8
    else
        conda run -n "$UMITOOLS_ENV" python "$UMITOOLS_DEDUP" \
            --threshold 2 --read-file "$SPL-R1_primers-pass_pair-pass.fastq"
        conda run -n "$UMITOOLS_ENV" python "$UMITOOLS_DEDUP" \
            --threshold 2 --read-file "$SPL-R2_primers-pass_pair-pass.fastq" \
            --cluster-file "$MOUNT_DIR/clusters.pickle"
        SET_IDENT=0.58
    fi

    # Stage 1: sub-cluster (sequence) clustering, ident is method dependent
    cat "$SPL-R1_primers-pass_pair-pass_cluster-pass.fastq" \
        | seqkit sample -s 420 -n 50000 -o "$SPL-R1_primers-pass_pair-pass_cluster-pass_sample.fastq"
    run_ic EstimateError.py set -s "$SP-R1_primers-pass_pair-pass_cluster-pass_sample.fastq" -f INDEX_UMI -n 3
    THRESHOLD=$(read_threshold "$SPL-R1_primers-pass_pair-pass_cluster-pass_sample_threshold-set.tab")
    echo "Set threshold for $SAMPLE: $THRESHOLD (using $SET_IDENT for clustering)"
    echo "$THRESHOLD" > "${SAMPLE}_index_seq_threshold.txt"
    run_ic ClusterSets.py set \
        -s "$SP-R1_primers-pass_pair-pass_cluster-pass.fastq" "$SP-R2_primers-pass_pair-pass_cluster-pass.fastq" \
        -f INDEX_UMI -k INDEX_SEQ --ident "$SET_IDENT"

    # Stage 1: consensus, assembly, C-region, collapse
    run_ic ParseHeaders.py merge \
        -s "$SP-R1_primers-pass_pair-pass_cluster-pass_cluster-pass.fastq" \
           "$SP-R2_primers-pass_pair-pass_cluster-pass_cluster-pass.fastq" \
        -f INDEX_UMI INDEX_SEQ -k INDEX_MERGE

    mv "$SPL-R1_primers-pass_pair-pass_cluster-pass_cluster-pass_reheader.fastq" "$SPL-R1_cluster-pass_reheader.fastq"
    mv "$SPL-R2_primers-pass_pair-pass_cluster-pass_cluster-pass_reheader.fastq" "$SPL-R2_cluster-pass_reheader.fastq"

    run_ic BuildConsensus.py -s "$SP-R1_cluster-pass_reheader.fastq" --bf INDEX_MERGE --pf PRIMER \
        --prcons 0.6 --maxerror 0.1 --maxgap 0.5 --outname "$SP-R1" --log "$PATH_PREP/BC1.log"
    run_ic BuildConsensus.py -s "$SP-R2_cluster-pass_reheader.fastq" --bf INDEX_MERGE --pf PRIMER \
        --maxerror 0.1 --maxgap 0.5 --outname "$SP-R2" --log "$PATH_PREP/BC2.log"

    run_ic PairSeq.py -1 "$SP-R1_consensus-pass.fastq" -2 "$SP-R2_consensus-pass.fastq" --coord presto

    run_ic AssemblePairs.py sequential -1 "$SP-R2_consensus-pass_pair-pass.fastq" \
        -2 "$SP-R1_consensus-pass_pair-pass.fastq" -r "$REF_IGV" \
        --coord presto --rc tail --scanrev --1f CONSCOUNT --2f CONSCOUNT PRCONS \
        --aligner blastn --outname "$SP-C" --log "$PATH_PREP/AP.log"

    run_ic MaskPrimers.py align -s "$SP-C_assemble-pass.fastq" \
        -p "$P_CREGION" --maxlen 100 --maxerror 0.3 \
        --mode tag --revpr --skiprc --pf CREGION --outname "$SP-C" --log "$PATH_PREP/MP3.log"

    run_ic ParseHeaders.py collapse -s "$SP-C_primers-pass.fastq" -f CONSCOUNT --act min

    run_ic CollapseSeq.py -s "$SP-C_primers-pass_reheader.fastq" -n 20 --inner \
        --uf CREGION --cf CONSCOUNT --act sum --outname "$SP-C"

    run_ic SplitSeq.py group -s "$SP-C_collapse-unique.fastq" -f CONSCOUNT --num 2 --outname "$SP-C"

    run_ic ParseHeaders.py table -s "$SP-C_atleast-2.fastq" -f ID CREGION CONSCOUNT DUPCOUNT

    run_ic ParseLog.py -l "$PATH_PREP/FS1.log" "$PATH_PREP/FS2.log" -f ID QUALITY
    run_ic ParseLog.py -l "$PATH_PREP/MP1.log" "$PATH_PREP/MP2.log" "$PATH_PREP/MP3.log" -f ID PRIMER BARCODE ERROR
    run_ic ParseLog.py -l "$PATH_PREP/BC1.log" "$PATH_PREP/BC2.log" -f BARCODE SEQCOUNT CONSCOUNT PRCONS PRFREQ ERROR
    run_ic ParseLog.py -l "$PATH_PREP/AP.log" -f ID REFID LENGTH OVERLAP GAP ERROR IDENTITY

    # Stage 2: Change-O — IgBLAST, genotype, threshold, clones
    local READS="$PATH_PREP/${SAMPLE}-C_atleast-2.fastq"
    run_ic changeo-igblast  -s "$READS" -n "$SAMPLE" -o "$SP" -p "$NPROC"        | tee run_igblast.out
    run_ic tigger-genotype  -d "$SP/${SAMPLE}_db-pass.tsv"    -n "$SAMPLE" -o "$SP" -p "$NPROC" -y 150 | tee run_genotype.out
    run_ic shazam-threshold -d "$SP/${SAMPLE}_genotyped.tsv"  -n "$SAMPLE" -o "$SP" -p "$NPROC"        | tee run_threshold.out
    run_ic changeo-clone    -d "$SP/${SAMPLE}_genotyped.tsv"  -x "$DIST" -n "$SAMPLE" -o "$SP" -p "$NPROC" | tee run_clone.out

    # Copy scratch -> analysis dir for stage 3
    mkdir -p "$ANALYSIS_ROOT/FN.p3482.$SAMPLE"
    cp -r "$MOUNT_DIR/$SAMPLE" "$ANALYSIS_ROOT/FN.p3482.$SAMPLE/"
    cd - >/dev/null
}

# --- run stages 1+2 per sample, isolate failures ---
OK=()
FAILED=()
for SAMPLE in "${SAMPLES[@]}"; do
    germ="$ANALYSIS_ROOT/FN.p3482.$SAMPLE/$SAMPLE/${SAMPLE}_germ-pass.tsv"
    if ( set -e; process_sample "$SAMPLE" ) && [[ -f "$germ" ]]; then
        OK+=("$SAMPLE")
        echo "=== [$SAMPLE] done ==="
    else
        FAILED+=("$SAMPLE")
        echo "!!! [$SAMPLE] FAILED — skipping (no germ-pass at $germ) !!!" >&2
    fi
done

echo "Succeeded (${#OK[@]}): ${OK[*]:-none}"
echo "Failed    (${#FAILED[@]}): ${FAILED[*]:-none}"

if [[ ${#OK[@]} -eq 0 ]]; then
    echo "ERROR: no samples produced a germ-pass table; skipping stage 3." >&2
    exit 1
fi

# --- Stage 3: R aggregation over all FN.p3482.* dirs (script run unmodified) ---
echo "=== Stage 3: R aggregation ==="
module load Dev/R/4.5.0
Rscript -e '.libPaths(.libPaths()[length(.libPaths())]); source(commandArgs(TRUE)[1])' "$R_DATAGEN"

echo "Pipeline complete. Output: $ANALYSIS_ROOT/RobjectForSummaryReport.Rdata"
