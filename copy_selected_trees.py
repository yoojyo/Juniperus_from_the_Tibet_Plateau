#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys

def get_prefix(filename):
    # Take text before first dot as OG name
    return filename.split('.')[0]

def main(tree_dir, gene_dir, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # collect OG names from gene_dir
    selected_ogs = set()
    for fn in os.listdir(gene_dir):
        if fn.startswith("."):
            continue
        og = get_prefix(fn)
        if og:
            selected_ogs.add(og)

    if not selected_ogs:
        print("ERROR: no OG names found in gene_dir")
        return

    copied = 0
    missing = []

    for og in sorted(selected_ogs):
        tree_file = os.path.join(tree_dir, og + ".treefile")
        if os.path.exists(tree_file):
            shutil.copy2(tree_file, out_dir)
            copied += 1
        else:
            missing.append(og)

    print("========== Done ==========")
    print("Selected OGs :", len(selected_ogs))
    print("Trees copied :", copied)
    print("Trees missing:", len(missing))

    if missing:
        missing_txt = os.path.join(out_dir, "missing_ogs.txt")
        with open(missing_txt, "w") as f:
            for og in missing:
                f.write(og + "\n")
        print("Missing list saved to:", missing_txt)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python copy_selected_trees.py <tree_dir> <gene_dir> <out_dir>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
