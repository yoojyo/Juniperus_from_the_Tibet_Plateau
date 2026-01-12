#!/usr/bin/python
# -*- coding: utf-8 -*-

# 用法: python merge_fna_single_inroot.py inroot genes_with_paralog_warnings.txt outroot

import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_one_gene(gene_key, paths, outroot):
    contents = []
    for p in paths:
        try:
            with open(p, "r") as f:
                c = f.read().strip()
                if c:
                    contents.append(c)
        except IOError as e:
            print(f"Warning: Could not read {p}: {e}")

    if not contents:
        return 0

    contents.sort()  # 与 sorted(contents) 等价，语义不变

    outpath = os.path.join(outroot, f"{gene_key}.fas")
    try:
        with open(outpath, "w") as fout:
            fout.write("\n".join(contents))
            fout.write("\n")
    except IOError as e:
        print(f"Error: Could not write {outpath}: {e}")
        return 0

    return len(contents)


def main():
    if len(sys.argv) < 4:
        print("usage: <script> <inroot> <genes_with_paralog_warnings.txt> <outroot>")
        sys.exit(1)

    inroot = sys.argv[1]  # 现在只处理单个输入文件夹
    paralog_file = sys.argv[2]
    outroot = sys.argv[3]

    # 1) 读 paralog 列表
    try:
        with open(paralog_file) as f:
            para_set = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Error: File {paralog_file} not found")
        sys.exit(1)

    os.makedirs(outroot, exist_ok=True)

    # 2) 收集 gene -> 所有 inroot 下的文件路径
    gene2paths = defaultdict(list)

    # 只处理一个文件夹
    for root, dirs, files in os.walk(inroot):
        if not root.endswith("FNA"):
            continue

        for fn in files:
            if not (fn.startswith("OG") and fn.endswith(".FNA")):
                continue

            gene_key = fn.rsplit(".", 1)[0]
            if gene_key in para_set:
                continue

            gene2paths[gene_key].append(os.path.join(root, fn))

    # 3) 并行处理
    cpu = os.cpu_count() or 4
    workers = min(48, cpu * 4)

    processed = 0
    total_seqs = 0

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(process_one_gene, g, ps, outroot): g
                   for g, ps in gene2paths.items()}

        for fu in as_completed(futures):
            total_seqs += fu.result()
            processed += 1

    print(f"Processing complete. Processed {processed} genes, wrote {total_seqs} sequences.")
    print(f"Threads used: {workers}")


if __name__ == "__main__":
    main()
