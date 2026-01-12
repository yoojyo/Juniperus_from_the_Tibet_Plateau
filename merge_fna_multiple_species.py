#!/usr/bin/python
# -*- coding: utf-8 -*-

# Usage: python merge_fas_by_gene.py input_folders.txt output_folder
# input_folders.txt contains paths of all folders to be merged, one per line

import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_fasta_file(file_path):
    """Read fasta file and return list of sequences (header, sequence)"""
    sequences = []
    with open(file_path, 'r') as f:
        header = None
        seq_lines = []
        for line in f:
            line = line.rstrip()
            if line.startswith('>'):
                # Save previous sequence
                if header is not None and seq_lines:
                    sequences.append((header, ''.join(seq_lines)))
                # Start new sequence
                header = line[1:]  # Remove '>'
                seq_lines = []
            elif line:
                seq_lines.append(line)
        
        # Save last sequence
        if header is not None and seq_lines:
            sequences.append((header, ''.join(seq_lines)))
    
    return sequences

def process_one_gene(gene_name, file_paths, output_folder):
    """Merge all files for a single gene"""
    all_sequences = []
    
    for file_path in file_paths:
        try:
            # Read all sequences from the fasta file
            sequences = process_fasta_file(file_path)
            
            # Add sequences to the total list
            for header, sequence in sequences:
                # Sequence headers already contain species info, use as is
                all_sequences.append((header, sequence))
                
        except Exception as e:
            print(f"Warning: Error processing file {file_path}: {e}")
            continue
    
    if not all_sequences:
        return 0
    
    # Write merged file
    output_file = os.path.join(output_folder, f"{gene_name}.fas")
    try:
        with open(output_file, 'w') as f:
            for header, sequence in all_sequences:
                f.write(f">{header}\n")
                # Format sequence, 80 characters per line
                for i in range(0, len(sequence), 80):
                    f.write(f"{sequence[i:i+80]}\n")
    except Exception as e:
        print(f"Error: Failed to write file {output_file}: {e}")
        return 0
    
    return len(all_sequences)

def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_fas_by_gene.py <input_folders.txt> <output_folder>")
        print("input_folders.txt contains paths of all folders to be merged, one per line")
        sys.exit(1)
    
    input_folders_file = sys.argv[1]
    output_folder = sys.argv[2]
    
    # Read input folder list
    try:
        with open(input_folders_file, 'r') as f:
            input_folders = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {input_folders_file} not found")
        sys.exit(1)
    
    if not input_folders:
        print("Error: Input folder list is empty")
        sys.exit(1)
    
    # Verify all input folders exist
    valid_folders = []
    for folder in input_folders:
        if os.path.exists(folder):
            valid_folders.append(folder)
        else:
            print(f"Warning: Folder {folder} does not exist, skipping")
    
    if not valid_folders:
        print("Error: No valid input folders")
        sys.exit(1)
    
    print(f"Found {len(valid_folders)} valid input folders")
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Collect all .fas files, group by gene name
    gene_files = defaultdict(list)
    all_fasta_files = []
    
    for folder in valid_folders:
        print(f"Scanning folder: {folder}")
        
        # Traverse all .fas files in the folder
        for root, dirs, files in os.walk(folder):
            for file in files:
                # Support multiple fasta file extensions
                if file.lower().endswith(('.fas', '.fasta', '.fa', '.fna')):
                    file_path = os.path.join(root, file)
                    all_fasta_files.append(file_path)
                    
                    # Extract gene name (remove extension)
                    gene_name = os.path.splitext(file)[0]
                    
                    # Add to dictionary
                    gene_files[gene_name].append(file_path)
    
    print(f"Found {len(all_fasta_files)} fasta files in total")
    print(f"Found {len(gene_files)} different genes")
    
    # Display some statistics
    print("\nGene file statistics:")
    gene_count = 0
    for gene_name, files in sorted(gene_files.items()):
        gene_count += 1
        print(f"  {gene_name}: {len(files)} files")
        if gene_count >= 20 and len(gene_files) > 20:
            print(f"  ... and {len(gene_files) - 20} more genes")
            break
    
    # Use multi-threading
    cpu_count = os.cpu_count() or 4
    workers = min(32, cpu_count * 2)
    
    print(f"\nStarting merge, using {workers} threads...")
    
    total_genes = len(gene_files)
    processed_genes = 0
    total_sequences = 0
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_gene = {}
        for gene_name, file_paths in gene_files.items():
            future = executor.submit(process_one_gene, gene_name, file_paths, output_folder)
            future_to_gene[future] = gene_name
        
        # Process completed tasks
        for future in as_completed(future_to_gene):
            gene_name = future_to_gene[future]
            try:
                seq_count = future.result()
                total_sequences += seq_count
                processed_genes += 1
                
                if processed_genes % 100 == 0:
                    print(f"Processed {processed_genes}/{total_genes} genes")
            except Exception as e:
                print(f"Error processing gene {gene_name}: {e}")
    
    print("\nMerge completed!")
    print(f"Total: Processed {processed_genes} genes")
    print(f"Total: Merged {total_sequences} sequences")
    print(f"Output folder: {output_folder}")
    
    # Output statistics for each gene
    print("\nSequence count per gene:")
    output_files = [f for f in os.listdir(output_folder) if f.endswith('.fas')]
    for output_file in sorted(output_files)[:20]:  # Show only first 20
        gene_name = os.path.splitext(output_file)[0]
        with open(os.path.join(output_folder, output_file), 'r') as f:
            seq_count = sum(1 for line in f if line.startswith('>'))
        print(f"  {gene_name}: {seq_count} sequences")
    
    if len(output_files) > 20:
        print(f"  ... and {len(output_files) - 20} more gene files")

if __name__ == "__main__":
    main()