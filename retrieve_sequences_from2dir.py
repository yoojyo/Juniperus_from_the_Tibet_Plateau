#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
from Bio import SeqIO
import multiprocessing

helptext = '''Usage:
    python retrieve_sequences.py baitfile.fasta dir1,dir2 aa/dna/intron/supercontig num_cores

You can now provide MULTIPLE sequence directories separated by commas,
e.g., "seqdir1,seqdir2".
The script will search all directories for the requested sequences.
'''

def retrieve_sequences(gene):
    gene_seqs = []

    for seq_root in seq_dirs:  # 遍历每个目录
        for sample in sample_names_per_dir[seq_root]:
            if seq_dir == 'intron':
                sample_path = os.path.join(
                    seq_root, sample, gene, sample, 'sequences',
                    seq_dir, "{}_{}.fasta".format(gene, filename)
                )
            else:
                sample_path = os.path.join(
                    seq_root, sample, gene, sample, 'sequences',
                    seq_dir, gene + '.' + seq_dir
                )

            if os.path.isfile(sample_path):
                rec = SeqIO.read(sample_path, 'fasta')
                rec.id = rec.id.split("-")[0]
                rec.description = ''
                gene_seqs.append(rec)

    print("Found {} sequences for {}.".format(len(gene_seqs), gene))

    if not gene_seqs:
        return

    if seq_dir == 'intron':
        outfilename = "{}_{}.fasta".format(gene, filename)
    else:
        outfilename = gene + '.' + seq_dir

    SeqIO.write(gene_seqs, open(outfilename, 'w'), 'fasta')


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print(helptext)
        sys.exit(1)

    # 指定序列类型
    if sys.argv[3] == 'dna':
        seq_dir = "FNA"
    elif sys.argv[3] == 'aa':
        seq_dir = "FAA"
    elif sys.argv[3] == 'intron':
        seq_dir = 'intron'
        filename = 'introns'
    elif sys.argv[3] == 'supercontig':
        seq_dir = 'intron'
        filename = 'supercontig'
    else:
        print(helptext)
        sys.exit(1)

    # 读取 bait file
    baitfile = sys.argv[1]
    target_genes = list(set(
        [x.id.split('-')[-1] for x in SeqIO.parse(baitfile, 'fasta')]
    ))

    # 解析多个目录（用逗号分隔）
    seq_dirs = [d.strip() for d in sys.argv[2].split(",")]

    # 从每个目录分别收集样本名称
    sample_names_per_dir = {}

    for sd in seq_dirs:
        samples = [
            x for x in os.listdir(sd)
            if os.path.isdir(os.path.join(sd, x)) and not x.startswith('.')
        ]
        sample_names_per_dir[sd] = samples

    total_samples = sum(len(v) for v in sample_names_per_dir.values())
    print("Retrieving {} genes from {} samples across {} directories".format(
        len(target_genes), total_samples, len(seq_dirs)
    ))

    # 核心处理部分
    if len(sys.argv) == 5:
        num_cores = int(sys.argv[4])
    else:
        num_cores = 6

    p = multiprocessing.Pool(num_cores)
    p.map(retrieve_sequences, target_genes)
    p.close()
    p.join()
