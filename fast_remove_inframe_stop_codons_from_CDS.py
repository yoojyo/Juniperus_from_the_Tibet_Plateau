#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from Bio import SeqIO
from Bio.Seq import Seq

def load_paralogs(path):
    s = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                s.add(line)
    return s

def strip_internal_stops_from_cds(cds, stop_codons):
    """
    cds: Bio.Seq.Seq 或 str，假设是 CDS（frame=0）
    逻辑：删除内部 stop codon（不处理最后一个 codon；因为很多 CDS 末尾本来就有 stop）
    """
    seq = str(cds).upper()
    n = len(seq)
    if n < 6:
        return Seq(seq)

    last_codon_start = n - (n % 3) - 3  # 最后一个完整codon起点
    if last_codon_start < 0:
        return Seq(seq)

    out_chunks = []
    i = 0
    # 扫描到“倒数第一个codon”之前
    while i <= last_codon_start - 3:
        codon = seq[i:i+3]
        if codon in stop_codons:
            # 跳过这个 stop codon（相当于删掉）
            i += 3
            continue
        out_chunks.append(codon)
        i += 3

    # 把最后一个完整codon + 余下非整除部分原样拼回去
    out_chunks.append(seq[last_codon_start:last_codon_start+3])
    if last_codon_start + 3 < n:
        out_chunks.append(seq[last_codon_start+3:])

    return Seq("".join(out_chunks))

def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_dir> <paralogs.txt> <outroot>")
        sys.exit(1)

    inroot = sys.argv[1]
    paralog_file = sys.argv[2]
    outroot = sys.argv[3]

    if not os.path.exists(outroot):
        os.makedirs(outroot)

    paralogs = load_paralogs(paralog_file)

    # 终止密码子：通常用 TAA/TAG/TGA（适用于绝大多数核基因/多数表）
    stop_codons = set(["TAA", "TAG", "TGA"])

    # 用 scandir 会更快（py2 无 scandir 就退化为 listdir）
    try:
        it = os.scandir(inroot)
        entries = [e for e in it if e.is_file()]
    except Exception:
        entries = [os.path.join(inroot, x) for x in os.listdir(inroot)]

    n_files = 0
    for entry in entries:
        inpath = entry.path if hasattr(entry, "path") else entry
        name = os.path.basename(inpath)

        if not name.endswith(".FNA"):
            continue

        gene = name.split(".")[0]
        if gene in paralogs:
            continue

        out_records = []
        for rec in SeqIO.parse(inpath, "fasta"):
            rec.seq = strip_internal_stops_from_cds(rec.seq, stop_codons)
            rec.description = ""
            out_records.append(rec)

        if out_records:
            SeqIO.write(out_records, os.path.join(outroot, name), "fasta")
            n_files += 1

    print("Done. Processed {} FNA files.".format(n_files))

if __name__ == "__main__":
    main()
