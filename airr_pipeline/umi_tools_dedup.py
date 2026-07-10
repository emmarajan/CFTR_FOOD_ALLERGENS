import argparse
import logging
import pickle
from os import path
from tqdm import tqdm
from collections import Counter
from umi_tools.network import UMIClusterer
from collections import OrderedDict
from Bio import SeqIO
encoding = 'utf-8'

def is_valid_file(parser, arg):
    if not path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return str(arg)


def set_up_logger():
    logger = logging.getLogger('dedup')
    logger.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def main():
    parser = argparse.ArgumentParser(description='Perform clustering with umi_tools.')
    parser.add_argument('--threshold', metavar='T', type=int, required=True,
                     help='The maximum distance two barcodes can be away to be considered to be clustered')
    parser.add_argument('--read-file', metavar='R', type=lambda x: is_valid_file(parser, x), required=True,
                     help='The read file in fastq format')
    parser.add_argument('--cluster-file', metavar='C', type=lambda x: is_valid_file(parser, x), default=None,
                     help='The read file in fastq format')
    
    args = parser.parse_args()
    logger = set_up_logger()
    
    if args.cluster_file is None:
        logger.info("Generating cluster.pickle file")

        umis = []
        for record in tqdm(SeqIO.parse(args.read_file, "fastq")):
        	umis.append(record.description.split("|")[-1].split("=")[-1])
        
        umi_dict = dict(Counter(umis))
        umi_dict_byte = {bytes(key, encoding): val for key, val in zip(umi_dict.keys(), umi_dict.values())}
       
        logger.info("Running UMIClusterer")
        clusterer = UMIClusterer(cluster_method="directional")
        clustered_umis = clusterer(umi_dict_byte, threshold = args.threshold)
        
        dist_freq = dict(Counter([len(umi) for umi in clustered_umis]))
        dist_freq_ordered = dict(OrderedDict(sorted(dist_freq.items())))
        logger.info(dist_freq_ordered)
        
        cluster_mapping = dict()
        cluster_number = 1
        for umi_cluster in clustered_umis:
            for umi in umi_cluster:
                cluster_mapping[umi.decode(encoding)] = cluster_number
            cluster_number += 1
        
        output_directory = path.dirname(path.realpath(args.read_file))
        logger.info(f"Putting the clusters pickle inside {output_directory}")
        clusters_file = path.join(output_directory, "clusters.pickle")
    
        with open(clusters_file, "wb") as f:
            pickle.dump(cluster_mapping, f)
    
    else:
        cluster_file = args.cluster_file
        with open(cluster_file, "rb") as f:
            cluster_mapping = pickle.load(f)
  
    out_fq = path.splitext(path.realpath(args.read_file))[0] + "_cluster-pass.fastq"
    logger.info(f"Dumping new fastq clustering inside {out_fq}")
    clustered_fq = open(out_fq, "w")
    for record in tqdm(SeqIO.parse(args.read_file, "fastq")):
        umi = record.description.split("|")[-1].split("=")[-1]
        cluster_num = str(cluster_mapping[umi])
        new_header = record.description + f"|INDEX_UMI={cluster_num}"
        record.description = new_header

        SeqIO.write(record, clustered_fq, "fastq")
    clustered_fq.close()


if __name__ == "__main__":
	main()
