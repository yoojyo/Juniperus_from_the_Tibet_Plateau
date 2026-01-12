import os
path = "/data/user010/project2/19trimal/"
outpath = "/data/user010/project2/19raxml/"
outfile = open(outpath + "2366raxml.sh","w")
a = os.listdir(path)
for i in a:
	b = i.split(".")[0]
	cmd = "/data/soft/raxml/8.2.12/raxmlHPC-PTHREADS-AVX -T 8 -f a -p 12345 -x 12345 -m GTRGAMMA -N 100 -n %s -s /data/user010/project2/19trimal/%s" % (b, i)
	outfile.write(cmd+"\n")
outfile.close()
