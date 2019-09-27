import sys, os

def parse(configfile):
	fin = open(configfile, 'r')
	dic ={}
	for line in fin.readlines():
		key, value = line[:-1].split('\t')
		dic[key] = value
	fin.close()
	return dic

if len(sys.argv[:])!= 2:
	print ("python csv_run.py dataDir")
	sys.exit()
    
dir = sys.argv[1]
configfile = dir + '/config'

if not os.path.exists(configfile):
	print ("not config file")
	sys.exit()

metaDic = parse(configfile)
if "version" in metaDic:
	version = metaDic["version"]
else:
	print ("missing version")
	sys.exit()

if "cohort" in metaDic:
	cohort = metaDic["cohort"]
else:
	print ("missing cohort")
	sys.exit()

if "url" in metaDic:
	version = metaDic["url"]
else:
	print ("missing url")
	sys.exit()

if "size" in metaDic:
	version = metaDic["size"]
else:
	print ("missing size")
	sys.exit()

os.system("python cells.csv.json.py " + dir + " " + version + " " + cohort + " " + url)
os.system("python expression.csv.json.py " + dir + " " + version + " " + cohort + " " + url)
os.system("python cells.csv.py " + dir)
os.system("python expression.csv.py " + dir + " " + size)