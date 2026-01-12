#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, os
from Bio import SeqIO

if len(sys.argv) != 4:
    print("Usage: <Script> <in_root> <out_root> <minimum_sp>")
    exit()

# --------------------
# 可调参数（推荐设置）
# --------------------
MIN_EFFECTIVE_LEN = 400        # 有效长度：非 "-" 位点数 >= 400
MIN_NON_GAP_RATIO = 0.7        # 非缺失比例 >= 0.7 （缺失 <= 30%）
MIN_SPECIES_PROP  = 0.7        # 通过过滤的序列数 / 总序列数 >= 0.7

inroot = sys.argv[1]
outroot = sys.argv[2]
nsp = int(sys.argv[3])

for i in sorted(os.listdir(inroot)):
    inpath = os.path.join(inroot, i)

    if not (i.endswith(".fasta") or i.endswith(".fa") or i.endswith(".fas")):
        continue

    kept_seqs = []
    total_seq = 0   # 该基因家族原始序列总数
    passed_seq = 0  # 通过单条序列过滤的序列数

    for seq_record in SeqIO.parse(inpath, "fasta"):
        total_seq += 1

        sequences = str(seq_record.seq)
        length = len(sequences)
        missing = sequences.count("-")
        n = length - missing  # 非缺失位点数

        # 1）长度与有效长度过滤
        if n < MIN_EFFECTIVE_LEN:
            continue
        if length < MIN_EFFECTIVE_LEN:
            continue

        # 2）缺失比例过滤
        non_gap_ratio = n / float(length)
        if non_gap_ratio < MIN_NON_GAP_RATIO:
            continue

        # 单条序列通过
        passed_seq += 1
        kept_seqs.append(seq_record)

    # 如果没有序列或者全部被过滤掉，跳过
    if total_seq == 0 or passed_seq == 0:
        continue

    # 3）对基因家族整体设置物种数 & 覆盖率过滤
    species_prop = passed_seq / float(total_seq)

    if (passed_seq >= nsp) and (species_prop >= MIN_SPECIES_PROP):
        outname = os.path.splitext(i)[0] + ".filtered.fas"
        outpath = os.path.join(outroot, outname)
        SeqIO.write(kept_seqs, outpath, "fasta")
