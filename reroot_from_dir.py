#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
from ete3 import Tree

if len(sys.argv) != 4:
    print("Usage: <script> <intrees_folder> <outgroup1,outgroup2..> <outtrees_folder>")
    exit()

# 输入文件夹路径、外群、输出文件夹路径
inroot = sys.argv[1]
outgroup = sys.argv[2]
outroot = sys.argv[3]

# 创建输出文件夹，如果不存在的话
if not os.path.exists(outroot):
    os.makedirs(outroot)

# 获取外群列表
outlist = outgroup.split(",")

# 遍历输入文件夹中的所有文件
for filename in os.listdir(inroot):
    input_path = os.path.join(inroot, filename)

    # 确保是一个文件，并且以 ".tree" 或其他适当扩展名结尾
    if os.path.isfile(input_path) and filename.endswith(".treefile"):  
        try:
            # 读取树文件
            with open(input_path, 'r') as infile:
                tree = Tree(infile.readline().strip())  # 假设每个文件只含有一个树

            leaves = tree.get_leaf_names()  # 获取树的叶子节点

            lst = [i for i in outlist if i in leaves]  # 找到所有出现在树中的外群

            # 定根操作
            if len(lst) == 1:
                root_point = tree.get_leaves_by_name(lst[0])[0]
                tree.set_outgroup(root_point)
            elif len(lst) > 1:
                results = tree.check_monophyly(lst, "name")
                if results[0]:
                    anc = tree.get_common_ancestor(lst)
                    tree.set_outgroup(anc)
                else:
                    print("Warning: Outgroups of tree {} are not monophyly".format(filename))
            else:
                print("Warning: Outgroups are not in tree {}".format(filename))

            # 写入定根后的树到输出文件夹
            output_path = os.path.join(outroot, filename)
            with open(output_path, 'w') as outfile:
                outfile.write(str(tree.write()) + "\n")

            print("Processed tree: {}".format(filename))
        
        except Exception as e:
            print("Error processing {}: {}".format(filename, e))
