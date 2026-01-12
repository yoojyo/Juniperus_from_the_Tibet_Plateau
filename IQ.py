import os
path = "/data/user010/project2/14/gt80newfilter/"
outpath = "/data/user010/project2/14/IQTree"
outfile = open(outpath + "3388iqtree.sh","w")
a = os.listdir(path)
for i in a:
	b = i.split(".fas")[0]
	cmd = "/data/soft/iqtree/iqtree-2.0.4-Linux/bin/iqtree2 -s /data/user010/project2/14/gt80newfilter/%s.fas -pre %s.iqtree.fas -st DNA -nt 5 -B 1000 -m MFP -quiet -redo" % (b, i)
	outfile.write(cmd+"\n")
outfile.close()
