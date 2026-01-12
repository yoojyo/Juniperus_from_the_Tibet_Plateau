#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert rooted NEXUS trees to Newick format
指定外类群定根并输出 newick 格式
"""

from Bio import Phylo
import sys, os, glob

# ========== 用户参数 ==========
# 外类群名称
OUTGROUP = "2023_chw_GZX_1_2"

# 输入路径：可为单个文件或文件夹
input_path = sys.argv[1] if len(sys.argv) > 1 else "./"

# 输出路径（默认为输入路径）
output_path = input_path

# ========== 主程序部分 ==========

def convert_nexus_to_newick(file_path, outgroup):
    try:
        tree = Phylo.read(file_path, "nexus")

        # 检查外类群是否在树中
        taxa = [t.name for t in tree.get_terminals()]
        if outgroup not in taxa:
            print(f"[WARN] Outgroup {outgroup} not found in {file_path}, skipping rooting.")
        else:
            tree.root_with_outgroup(outgroup)
            print(f"? 已为 {file_path} 定根：{outgroup}")

        # 输出 newick
        newick_file = os.path.splitext(file_path)[0] + "_rooted.nwk"
        Phylo.write(tree, newick_file, "newick")
        print(f"?? 输出文件：{newick_file}\n")

    except Exception as e:
        print(f"? 处理 {file_path} 出错：{e}")


if os.path.isdir(input_path):
    files = glob.glob(os.path.join(input_path, "*.nexus"))
else:
    files = [input_path]

for f in files:
    convert_nexus_to_newick(f, OUTGROUP)
