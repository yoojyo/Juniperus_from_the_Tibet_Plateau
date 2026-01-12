#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

gene_folder = "/data/user010/project2/14/gt80newfilter/"
tree_folder = "/data/user010/project2/14/IQTreefile/"
output_folder = "/data/user010/project2/14/3381genes/"

os.makedirs(output_folder, exist_ok=True)

for gene_file in os.listdir(gene_folder):
    if gene_file.endswith(".fasta") or gene_file.endswith(".fa") or gene_file.endswith(".fas"):
        base_name = gene_file.split(".")[0]
        # 使用 .format() 方法替代 f-string
        tree_file_name = "{}.treefile".format(base_name)
        tree_file_path = os.path.join(tree_folder, tree_file_name)

        if os.path.exists(tree_file_path):
            shutil.copy(tree_file_path, os.path.join(output_folder, tree_file_name))
            print("Copied: {}".format(tree_file_name))
        else:
            print("Tree file not found for {}: {}".format(gene_file, tree_file_name))
