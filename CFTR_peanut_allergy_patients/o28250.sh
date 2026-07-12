#initial variant calling performed is SUSHI

gatk CombineGVCFs -R /srv/GT/reference/Homo_sapiens/GENCODE/GRCh38.p13/Sequence/WholeGenomeFasta/genome.fa \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_01-TSP0001-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_02-TSP0002-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_03-TSP0003-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_04-TSP0004-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_05-TSP0005-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_06-TSP0006-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_07-TSP0007-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_08-TSP0008-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_09-TSP0009-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_10-TSP0010-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_11-TSP0011-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_12-TSP0012-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_13-TSP0013-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_14-TSP0014-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_15-TSP0015-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_16-TSP0016-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_17-TSP0017-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_18-TSP0018-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_19-TSP0019-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_20-TSP0020-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_21-TSP0021-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_22-TSP0022-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_23-TSP0023-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_24-TSP0024-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_25-TSP0025-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_26-TSP0026-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_27-TSP0027-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_28-TSP0028-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_29-TSP0029-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_30-TSP0030-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_31-TSP0031-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_32-TSP0032-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_33-TSP0033-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_34-TSP0034-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_35-TSP0035-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_36-TSP0036-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_37-TSP0037-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_38-TSP0038-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_39-TSP0039-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_40-TSP0040-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_41-TSP0041-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_42-TSP0042-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_43-TSP0043-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_44-TSP0044-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_45-TSP0045-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_46-TSP0046-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_47-TSP0047-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_48-TSP0048-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_49-TSP0049-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_50-TSP0050-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_51-TSP0051-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_52-TSP0052-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_53-TSP0053-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_54-TSP0054-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_55-TSP0055-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_56-TSP0056-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_57-TSP0057-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_58-TSP0058-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_59-TSP0059-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_60-TSP0060-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_61-TSP0061-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_62-TSP0062-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_63-TSP0063-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_64-TSP0064-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_65-TSP0065-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_66-TSP0066-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_67-TSP0067-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_68-TSP0068-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_69-TSP0069-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_70-TSP0070-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_71-TSP0071-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_72-TSP0072-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_73-TSP0073-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_74-TSP0074-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_75-TSP0075-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_76-TSP0076-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_77-TSP0077-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_78-TSP0078-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_79-TSP0079-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_80-TSP0080-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_81-TSP0081-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_82-TSP0082-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_83-TSP0083-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_84-TSP0084-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_85-TSP0085-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_86-TSP0086-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_87-TSP0087-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_88-TSP0088-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_89-TSP0089-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_90-TSP0090-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_91-TSP0091-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_92-TSP0092-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_93-TSP0093-HC_calls.g.vcf.gz \
--variant /srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_1_94-TSP0094-HC_calls.g.vcf.gz \
-O combined.g.vcf.gz

gatk GenotypeGVCFs -R /srv/GT/reference/Homo_sapiens/GENCODE/GRCh38.p13/Sequence/WholeGenomeFasta/genome.fa -V combined.g.vcf.gz -O final.g.vcf.gz
zcat final.g.vcf.gz | java -jar /usr/local/ngseq/packages/Variants/SnpEff/4.3/SnpSift.jar filter "(CHROM == 'chr7') & (DP >= 200)" > final.g.chr7.dp200.vcf
java -jar /usr/local/ngseq/packages/Variants/SnpEff/4.3/snpEff.jar hg38 final.g.chr7.dp200.vcf > final.g.chr7.dp200.ann.vcf
java -jar /usr/local/ngseq/packages/Variants/SnpEff/4.3/SnpSift.jar annotate clinvar.vcf.gz final.g.chr7.dp200.ann.vcf > final.g.chr7.dp200.ann.clinvar.vcf
cat final.g.chr7.dp200.ann.clinvar.vcf | perl /usr/local/ngseq/packages/Variants/SnpEff/4.3/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/ngseq/packages/Variants/SnpEff/4.3/SnpSift.jar extractFields -s "," -e "." - CHROM POS REF ALT AF "ANN[*].EFFECT" "ANN[*].GENE" "ANN[*].HGVS_C" "ANN[*].HGVS_P" GEN[*].GT "CLNSIG[*]"  > table.txt

#get AF only for individuals 1-90
vcftools --vcf final.g.chr7.dp200.ann.clinvar.vcf --out tmp.1.90.vcf --remove-indv o28250_1_91-TSP0091 --remove-indv o28250_1_92-TSP0092 --remove-indv o28250_1_93-TSP0093 --remove-indv o28250_1_94-TSP0094 --recode
bcftools +fill-tags tmp.1.90.vcf.recode.vcf  -- -t AF > tmp.1.90.vcf.recode.AF.vcf
cat tmp.1.90.vcf.recode.vcf | perl /usr/local/ngseq/packages/Variants/SnpEff/4.3/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/ngseq/packages/Variants/SnpEff/4.3/SnpSift.jar extractFields -s "," -e "." - CHROM POS REF ALT AF > tmp_table.txt

##Python
import pandas as pd
from gnomad_db.database import gnomAD_DB
database_location = "/srv/GT/databases/gnomAD_DB"
db = gnomAD_DB(database_location, genome="Grch38")
columns = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'o28250_1_01-TSP0001', 'o28250_1_02-TSP0002', 'o28250_1_03-TSP0003', 'o28250_1_04-TSP0004', 'o28250_1_05-TSP0005', 'o28250_1_06-TSP0006', 'o28250_1_07-TSP0007', 'o28250_1_08-TSP0008', 'o28250_1_09-TSP0009', 'o28250_1_10-TSP0010', 'o28250_1_11-TSP0011', 'o28250_1_12-TSP0012', 'o28250_1_13-TSP0013', 'o28250_1_14-TSP0014', 'o28250_1_15-TSP0015', 'o28250_1_16-TSP0016', 'o28250_1_17-TSP0017', 'o28250_1_18-TSP0018', 'o28250_1_19-TSP0019', 'o28250_1_20-TSP0020', 'o28250_1_21-TSP0021', 'o28250_1_22-TSP0022', 'o28250_1_23-TSP0023', 'o28250_1_24-TSP0024', 'o28250_1_25-TSP0025', 'o28250_1_26-TSP0026', 'o28250_1_27-TSP0027', 'o28250_1_28-TSP0028', 'o28250_1_29-TSP0029', 'o28250_1_30-TSP0030', 'o28250_1_31-TSP0031', 'o28250_1_32-TSP0032', 'o28250_1_33-TSP0033', 'o28250_1_34-TSP0034', 'o28250_1_35-TSP0035', 'o28250_1_36-TSP0036', 'o28250_1_37-TSP0037', 'o28250_1_38-TSP0038', 'o28250_1_39-TSP0039', 'o28250_1_40-TSP0040', 'o28250_1_41-TSP0041', 'o28250_1_42-TSP0042', 'o28250_1_43-TSP0043', 'o28250_1_44-TSP0044', 'o28250_1_45-TSP0045', 'o28250_1_46-TSP0046', 'o28250_1_47-TSP0047', 'o28250_1_48-TSP0048', 'o28250_1_49-TSP0049', 'o28250_1_50-TSP0050', 'o28250_1_51-TSP0051', 'o28250_1_52-TSP0052', 'o28250_1_53-TSP0053', 'o28250_1_54-TSP0054', 'o28250_1_55-TSP0055', 'o28250_1_56-TSP0056', 'o28250_1_57-TSP0057', 'o28250_1_58-TSP0058', 'o28250_1_59-TSP0059', 'o28250_1_60-TSP0060', 'o28250_1_61-TSP0061', 'o28250_1_62-TSP0062', 'o28250_1_63-TSP0063', 'o28250_1_64-TSP0064', 'o28250_1_65-TSP0065', 'o28250_1_66-TSP0066', 'o28250_1_67-TSP0067', 'o28250_1_68-TSP0068', 'o28250_1_69-TSP0069', 'o28250_1_70-TSP0070', 'o28250_1_71-TSP0071', 'o28250_1_72-TSP0072', 'o28250_1_73-TSP0073', 'o28250_1_74-TSP0074', 'o28250_1_75-TSP0075', 'o28250_1_76-TSP0076', 'o28250_1_77-TSP0077', 'o28250_1_78-TSP0078', 'o28250_1_79-TSP0079', 'o28250_1_80-TSP0080', 'o28250_1_81-TSP0081', 'o28250_1_82-TSP0082', 'o28250_1_83-TSP0083', 'o28250_1_84-TSP0084', 'o28250_1_85-TSP0085', 'o28250_1_86-TSP0086', 'o28250_1_87-TSP0087', 'o28250_1_88-TSP0088', 'o28250_1_89-TSP0089', 'o28250_1_90-TSP0090', 'o28250_1_91-TSP0091', 'o28250_1_92-TSP0092', 'o28250_1_93-TSP0093', 'o28250_1_94-TSP0094']
var_df = pd.read_csv("/srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_analysis/final.g.chr7.dp200.ann.clinvar.vcf", sep="\t", names=columns, index_col=False)
var_df = var_df.tail(434)
var_df.rename({"CHROM" : "chrom","POS" : "pos","REF" : "ref","ALT" : "alt"}, axis = 1, inplace = True)
var_df_annotated = db.get_info_from_df(var_df, "*")
var_df_annotated = var_df_annotated.fillna(".")
summary_table = pd.read_csv("/srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_analysis/table.txt" , sep = "\t")
summary_table["CHROM"] = summary_table.CHROM.apply(lambda x: x.split("chr")[1])
var_df_annotated.rename({"chrom" : "CHROM","pos" : "POS","ref" : "REF","alt" : "ALT"}, axis = 1, inplace = True)
final_table = pd.merge(summary_table, var_df_annotated, on = ["CHROM","POS","REF","ALT"], how = "left")
final_table.rename({'AF_x' : 'AF_insample'}, axis = 1, inplace=True)
CFTR_table = pd.read_csv("/srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_analysis/CFTR2_29April2022.txt" , sep = "\t", header = None)
CFTR_table.rename({0 : 'ANN[*].HGVS_C', 1 : 'ANN[*].HGVS_P'}, axis = 1, inplace = True)
final_table = pd.merge(final_table, CFTR_table, on = ['ANN[*].HGVS_C'], how = "left").fillna(".")
final_table = final_table[['CHROM',             'POS',             'REF',             'ALT',     'AF_insample',
         'ANN[*].EFFECT',     'ANN[*].GENE',   'ANN[*].HGVS_C',     'ANN[*].HGVS_P_x',       
             'GEN[*].GT',       'CLNSIG[*]',          'filter',     
                    'AC',              'AN',            'AF_y',
       'InbreedingCoeff',              'MQ',              'QD',
        'ReadPosRankSum',           'VarDP',       'AS_VQSLOD',
             'AC_popmax',       'AN_popmax',       'AF_popmax',
                'AF_eas',          'AF_oth',          'AF_nfe',
                'AF_fin',          'AF_afr',          'AF_asj',
       'ANN[*].HGVS_P_y',                 2,                 3,
                       4,                 5,                 6,
                       7,                 8,                 9]]
final_table.rename({"filter" : "filter_gnomad", "AC" : "AC_gnomad", "AN" : "AN_gnomad", "AF_y" : "AF_gnomad", "InbreedingCoeff" : "InbreedingCoeff_gnomad", "MQ" : "MQ_gnomad", "QD" : "QD_gnomad", "ReadPosRankSum", "ReadPosRankSum_gnomad", "VarDP" : "VarDP_gnomad", "AS_VQSLOD" : "AS_VQSLOD_gnomad", "AC_popmax" : "AC_popmax_gnomad", "AN_popmax": "AN_popmax_gnomad", "AF_popmax" : "AF_popmax_gnomad", "AF_eas" : "AF_eas_gnomad", "AF_oth" : "AF_oth_gnomad", "AF_nfe" : "AF_nfe_gnomad", "AF_fin" : "AF_fin_gnomad", "AF_afr" : "AF_afr_gnomad", "AF_asj" : "AF_asj_gnomad",'ANN[*].HGVS_P_y' : "Variant_protein_name", 2: "Variant_legacy_name", 3 : "rsID" , 4 : "#alleles_in_CFTR2", 5 : "Allele_frequency_in_CFTR2" , 6 : "%_pancreatic_insufficient", 7 :"Variant_final_determination_24.09" , 8 : "Variant_final_determination_29.04", 9 : "change_from_previous_version?"}, axis = 1, inplace = True)
AF_table = pd.read_csv("/srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_analysis/tmp_table.txt" , sep = "\t")
AF_table["CHROM"] = AF_table.CHROM.apply(lambda x: x.split("chr")[1])
table = pd.merge(final_table, AF_table[['CHROM', 'POS', 'REF', 'ALT', "AF"]], on = ['CHROM', 'POS', 'REF', 'ALT'], how = "left").rename({"AF": "AF_inPA"}, axis = 1).drop_duplicates()
table = table[['CHROM', 'POS', 'REF', 'ALT', 'AF_inPA', 'ANN[*].EFFECT',
       'ANN[*].GENE', 'ANN[*].HGVS_C', 'ANN[*].HGVS_P_x', 'GEN[*].GT','CLNSIG[*]',
       'filter_gnomad', 'AC_gnomad', 'AN_gnomad', 'AF_gnomad',
       'InbreedingCoeff_gnomad', 'MQ_gnomad', 'QD_gnomad',
       'ReadPosRankSum_gnomad', 'VarDP_gnomad', 'AS_VQSLOD_gnomad',
       'AC_popmax_gnomad', 'AN_popmax_gnomad', 'AF_popmax_gnomad',
       'AF_eas_gnomad', 'AF_oth_gnomad', 'AF_nfe_gnomad', 'AF_fin_gnomad',
       'AF_afr_gnomad', 'AF_asj_gnomad', 'Variant_protein_name',
       'Variant_legacy_name', 'rsID', '#alleles_in_CFTR2',
       'Allele_frequency_in_CFTR2', '%_pancreatic_insufficient',
       'Variant_final_determination_24.09',
       'Variant_final_determination_29.04', 'change_from_previous_version?']]
table.to_csv("/srv/GT/analysis/zajacn/p3482_MEmmenegger/o28250_analysis/final.summary.table.clinvar.txt", sep = "\t", index = False)
