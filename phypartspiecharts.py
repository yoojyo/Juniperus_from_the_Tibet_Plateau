#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
phypartspiecharts.py

Generate "Pie Chart" representation of gene tree conflict from the output of PhyParts.

Inputs:
  1) species tree (Newick)
  2) PhyParts output prefix (root name)
  3) total number of gene trees

Example:
  python3 phypartspiecharts.py species.tre phyparts_root 3223

Requirements:
  Python 3
  ete3
  matplotlib
"""

import sys, argparse, re, json
import matplotlib
matplotlib.use("Agg")  # safe on headless servers
from ete3 import Tree, TreeStyle, TextFace, NodeStyle, faces


helptext = """
Generate pie charts for PhyParts results.
"""


def get_phyparts_nodes(sptree_fn, phyparts_root):
    """
    Read species tree, make it ultrametric, then name internal nodes according
    to PhyParts node.key topology IDs.
    """
    sptree = Tree(sptree_fn)
    sptree.convert_to_ultrametric()

    # read phyparts node.key
    phyparts_node_key = [line.strip() for line in open(phyparts_root + ".node.key") if line.strip()]
    subtrees_dict = {n.split()[0]: Tree(n.split()[1] + ";") for n in phyparts_node_key}

    subtrees_topids = {k: subtrees_dict[k].get_topology_id() for k in subtrees_dict}

    # match each species-tree internal node to phyparts node id
    for node in sptree.traverse():
        node_topid = node.get_topology_id()
        for subtree in subtrees_dict:
            if node_topid == subtrees_topids[subtree]:
                node.name = subtree

    return sptree, subtrees_dict, subtrees_topids


def get_concord_and_conflict(phyparts_root, subtrees_dict, subtrees_topids):
    """
    Read *.concon.tre (two lines: concordance tree, conflict tree),
    return dicts of support values by phyparts node id.
    """
    with open(phyparts_root + ".concon.tre") as phyparts_trees:
        concon_tree = Tree(phyparts_trees.readline().strip())
        conflict_tree = Tree(phyparts_trees.readline().strip())

    concord_dict = {}
    conflict_dict = {}

    for node in concon_tree.traverse():
        node_topid = node.get_topology_id()
        for subtree in subtrees_dict:
            if node_topid == subtrees_topids[subtree]:
                concord_dict[subtree] = node.support

    for node in conflict_tree.traverse():
        node_topid = node.get_topology_id()
        for subtree in subtrees_dict:
            if node_topid == subtrees_topids[subtree]:
                conflict_dict[subtree] = node.support

    return concord_dict, conflict_dict


def get_pie_chart_data(phyparts_root, total_genes, concord_dict, conflict_dict):
    """
    Parse *.hist to get per-node concordant and conflicting counts,
    then convert to percentages for pie charts.
    """
    phyparts_hist = [line.strip() for line in open(phyparts_root + ".hist") if line.strip()]
    phyparts_pies = {}
    phyparts_dict = {}

    for n in phyparts_hist:
        parts = n.split(",")

        tot_genes_in_row = float(parts.pop(-1))
        node_name = parts.pop(0)[4:]  # strip "node"
        _concord_from_hist = float(parts.pop(0))

        concord = float(concord_dict.get(node_name, _concord_from_hist))
        all_conflict = float(conflict_dict.get(node_name, 0.0))

        if len(parts) > 0:
            most_conflict = max([float(x) for x in parts])
        else:
            most_conflict = 0.0

        adj_concord = (concord / total_genes) * 100.0
        adj_most_conflict = (most_conflict / total_genes) * 100.0
        other_conflict = ((all_conflict - most_conflict) / total_genes) * 100.0
        the_rest = ((total_genes - concord - all_conflict) / total_genes) * 100.0

        pie_list = [adj_concord, adj_most_conflict, other_conflict, the_rest]

        phyparts_pies[node_name] = pie_list
        phyparts_dict[node_name] = [int(round(concord, 0)), int(round(tot_genes_in_row - concord, 0))]

    return phyparts_dict, phyparts_pies


def node_text_layout(mynode):
    F = faces.TextFace(mynode.name, fsize=14)
    faces.add_face_to_node(F, mynode, 0, position="branch-right")


def pie_data_to_csv(phyparts_dist, phyparts_pies):
    """
    Export internal data to csv (optional).
    """
    phyparts_dist_bin = json.dumps(phyparts_dist)
    phyparts_pies_bin = json.dumps(phyparts_pies)

    dist_replaced = re.sub(r'{', r'node,concord,genes-concord\n', phyparts_dist_bin)
    dist_replaced = re.sub(r'"(\d+)":\s*\[(\d+),\s*(\d+)\],\s*', r'\1,\2,\3\n', dist_replaced)
    dist_replaced = re.sub(r'"(\d+)":\s*\[(\d+),\s*(\d+)\]}', r'\1,\2,\3', dist_replaced)

    pies_replaced = re.sub(r'{', r'node,adj_concord,adj_most_conflict,other_conflict,the_rest\n', phyparts_pies_bin)
    pies_replaced = re.sub(r'"(\d+)":\s*\[(\d*\.?\d+),\s*(\d*\.?\d+),\s*(\d*\.?\d+),\s*(\d*\.?\d+)\],\s*',
                           r'\1,\2,\3,\4,\5\n', pies_replaced)
    pies_replaced = re.sub(r'"(\d+)":\s*\[(\d*\.?\d+),\s*(\d*\.?\d+),\s*(\d*\.?\d+),\s*(\d*\.?\d+)\]}',
                           r'\1,\2,\3,\4,\5', pies_replaced)

    with open('phyparts_dist.csv', 'w') as f:
        f.write(dist_replaced)

    with open('phyparts_pies.csv', 'w') as f:
        f.write(pies_replaced)


def add_pies_to_tree(plot_tree, phyparts_pies, colors):
    """
    Attach pie charts to nodes.
    """
    for node in plot_tree.traverse():
        if node.is_leaf():
            continue
        if node.name in phyparts_pies:
            pie_vals = phyparts_pies[node.name]
            pie_face = faces.PieChartFace(pie_vals, width=25, height=25, colors=colors)
            faces.add_face_to_node(pie_face, node, 0, position="branch-top")


def main():
    parser = argparse.ArgumentParser(description=helptext, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('species_tree', help="Newick formatted species tree topology.")
    parser.add_argument('phyparts_root', help="File root name used for PhyParts.")
    parser.add_argument('num_genes', type=int, help="Total number of gene trees.")
    parser.add_argument('--taxon_subst', help="Comma-delimited file to translate tip names.")
    parser.add_argument("--svg_name", default="pies.svg", help="Output SVG name.")
    parser.add_argument("--show_nodes", action="store_true", default=False,
                        help="Show internal node labels (PhyParts ids).")
    parser.add_argument("--colors", nargs="+", default=["blue", "green", "red", "darkgray"],
                        help="Colors: concordance, top conflict, other conflict, no signal.")
    parser.add_argument("--no_ladderize", action="store_true", default=False,
                        help="Do not ladderize the tree.")
    parser.add_argument("--to_csv", action="store_true", default=False,
                        help="Export csv for ggtree.")
    args = parser.parse_args()

    plot_tree, subtrees_dict, subtrees_topids = get_phyparts_nodes(args.species_tree, args.phyparts_root)
    concord_dict, conflict_dict = get_concord_and_conflict(args.phyparts_root, subtrees_dict, subtrees_topids)
    phyparts_dist, phyparts_pies = get_pie_chart_data(args.phyparts_root, args.num_genes,
                                                      concord_dict, conflict_dict)

    # optional tip name substitution
    if args.taxon_subst:
        taxon_subst = {line.split(",")[0]: line.split(",")[1].strip()
                       for line in open(args.taxon_subst) if line.strip()}
        for leaf in plot_tree.get_leaves():
            if leaf.name in taxon_subst:
                leaf.name = taxon_subst[leaf.name]

    if not args.no_ladderize:
        plot_tree.ladderize()

    # tree style
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.scale = 120
    if args.show_nodes:
        ts.layout_fn = node_text_layout

    # add pie charts
    add_pies_to_tree(plot_tree, phyparts_pies, args.colors)

    # render
    plot_tree.render(args.svg_name, tree_style=ts)
    sys.stderr.write("[Info] SVG written to {}\n".format(args.svg_name))

    if args.to_csv:
        pie_data_to_csv(phyparts_dist, phyparts_pies)
        sys.stderr.write("[Info] CSV files written.\n")


if __name__ == "__main__":
    main()
