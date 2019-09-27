import sys, json

if len(sys.argv[:])!= 5:
    print "python cells.csv.json.py dataDir version cohort url"
    sys.exit()

dir = sys.argv[1]
version = sys.argv[2]
cohort = sys.argv[3]
url = sys.argv[4]

outfile = dir + '/cells.tsv.json'
fout = open(outfile,'w')

J ={}
J["type"] = "clinicalMatrix"
J["version"] = version
J["cohort"] = cohort
J["label"] = "cell metadata"
J["dataSubtype"] = "phenotype"
J["url"] = url

json.dump(J, fout, indent =4)
fout.close()