#!/usr/bin/env python
import sys, os, re

if len(sys.argv) != 3:
    print("usage: <script> <infile> <outfile>")
    exit()

dic = {"2022_CHZZ_NDC_1_5":"J_tibetica2", "2022_CHZZ_GDC_1_4":"J_saltuaria1", "2022_CHZZ_GPC_1_5":"J_convallium3", "2022_CHZZ_CMC_1_4":"J_convallium1", "2022_CHZZ_PGC_1_7":"J_saltuaria2", "2022_CHZZ_SNS_3_6":"J_tibetica3", "2022_CHZZ_DDS_1_10":"J_convallium2", "2022_CHZZ_KSZ_1_10":"J_tibetica1", "MB_05_092_14":"J_indica2", "2022_CHZZ_JLG_2_2":"J_recurva2", "MB_05_081_01":"J_caespitosa2", "2023_ccw_coxii_BZL_1":"J_coxii1", "2023_ccw_coxii_ZBS_1_S":"J_coxii3", "ZYJ_2024_5_1":"J_komarovii3", "C16_4":"J_przewalskii3", "2023_chw_hmg_1_2":"J_squamata2", "2022_CHZZ_LLZ_1_10":"J_pingii", "MaoKS_2017_032B_1":"J_wilsonii1", "2023_chw_GZX_1_2":"J_formosana"} 

infile = open(sys.argv[1])
outfile = open(sys.argv[2], "w")


for line in infile:
    for key in dic:
        key1 = "(%s:" % key
        key2 = ",%s:" % key
        key3 = "(%s[" % key
        key4 = ",%s[" % key
        key5 = "( %s" % key
        val1 = "(%s:" % dic[key]
        val2 = ",%s:" % dic[key]
        val3 = "(%s[" % dic[key]
        val4 = ",%s[" % dic[key]
        val5 = "( %s" % dic[key]
        line = line.replace(key1, val1)
        line = line.replace(key2, val2)
        line = line.replace(key3, val3)
        line = line.replace(key4, val4)
        line = line.replace(key5, val5)
    outfile.write(line)

infile.close()
outfile.close()
