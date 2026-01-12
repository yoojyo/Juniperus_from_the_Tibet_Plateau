#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil

def move_files(baitfile, fna_dir, faa_dir, filter_fna_dir, filter_faa_dir):
    # Step 1: 读取基因名字列表
    with open(baitfile, 'r') as f:
        gene_names = set(line.strip() for line in f if line.strip())  # 基因名存入集合，避免重复

    print(f"Found {len(gene_names)} genes to filter.")
    
    # Step 2: 创建新的文件夹（如果不存在）
    os.makedirs(filter_fna_dir, exist_ok=True)
    os.makedirs(filter_faa_dir, exist_ok=True)

    # Step 3: 遍历 FNA 文件夹并移动符合条件的文件
    for root, dirs, files in os.walk(fna_dir):
        for file in files:
            if file.endswith(".FNA"):
                gene_id = file.split(".")[0]  # 获取基因ID部分
                if gene_id in gene_names:
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(filter_fna_dir, file)
                    try:
                        shutil.move(src_path, dest_path)  # 移动文件
                        print(f"Moved: {src_path} -> {dest_path}")
                    except Exception as e:
                        print(f"Error moving {src_path}: {e}")
    
    # Step 4: 遍历 FAA 文件夹并移动符合条件的文件
    for root, dirs, files in os.walk(faa_dir):
        for file in files:
            if file.endswith(".FAA"):
                gene_id = file.split(".")[0]  # 获取基因ID部分
                if gene_id in gene_names:
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(filter_faa_dir, file)
                    try:
                        shutil.move(src_path, dest_path)  # 移动文件
                        print(f"Moved: {src_path} -> {dest_path}")
                    except Exception as e:
                        print(f"Error moving {src_path}: {e}")

if __name__ == "__main__":
    # 输入文件路径
    baitfile = "/data/user010/project2/script/allgenes_with_paralog_warnings_clean.txt"  # 你可以替换成你的文件路径
    fna_dir = "/data/user010/project2/FNA/"  # 你可以替换成你的 FNA 文件夹路径
    faa_dir = "/data/user010/project2/FAA/"  # 你可以替换成你的 FAA 文件夹路径
    filter_fna_dir = "/data/user010/project2/filterFNA/"  # 你可以替换成新的 FNA 文件夹路径
    filter_faa_dir = "/data/user010/project2/filterFAA/"  # 你可以替换成新的 FAA 文件夹路径
    
    # 调用移动函数
    move_files(baitfile, fna_dir, faa_dir, filter_fna_dir, filter_faa_dir)
