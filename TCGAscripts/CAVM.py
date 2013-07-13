import string, os, sys

sys.path.insert(0,"../CGDataNew")

from SampleMapNew import *
from CGDataLib import *
import TCGAUtil
def CAVMid (dir, outDir, cancer,log, REALRUN):
    print cancer, __name__

    ignore =1
    bookDic=cgWalk(dir,ignore)

    existMaps = collectSampleMaps(bookDic)
    missingMaps=  collectMissingSampleMaps(bookDic)

    #removeExistMaps
    for map in existMaps:
        if map not in missingMaps:
            missingMaps[map]=existMaps[map]
        
    # all aliquote uuid dic
    aliquote_dic =TCGAUtil.uuid_Aliquot_all()
    sample_dic =TCGAUtil.uuid_Sample_all()

    if not os.path.exists (outDir):
        os.system("mkdir "+outDir)
        
    for map in missingMaps:
        print map
        sMap =SampleMapNew(None,map)
        for name in missingMaps[map]:
            samples =[]
            intDic={}
            obj=bookDic[name]
            if obj['type']=="clinicalMatrix":
                outfile = outDir +os.path.basename(obj['path'])
                os.system("cp "+obj['path']+" "+outfile)
                os.system("cp "+obj['path']+".json "+outfile+".json")
                
            if obj['type']=="genomicMatrix":
                fin =open(obj['path'],'U')
                for sample in string.split(fin.readline()[:-1],"\t")[1:]:
                    if sample =="":
                        print name, "has bad empty sample id"
                        sys.exit()
                    if sample not in samples:
                        samples.append(sample)
                fin.close()
                
                outfile = outDir +os.path.basename(obj['path'])

                os.system("cp "+obj['path']+".json "+outfile+".json")

                if not REALRUN:
                    continue
                          
                for sample in samples:
                    #TCGA uuid handling
                    uuid=sample
                    if sample[0:4]!="TCGA": 
                        if aliquote_dic.has_key(string.lower(sample)):
                            TCGAbarcode = aliquote_dic[string.lower(sample)]
                        else:
                            print sample
                        parent = TCGAbarcode
                        child = sample
                        sMap.addLink(parent,child)
                        sample = parent
                    #do TCGA barcode trick
                    parts= string.split(sample,"-")
                    parent = string.join(parts[0:3],"-")
                    
                    #parts[3]
                    if len(parts)>3 and len(parts[3])==3:
                        child=parent +"-" +parts[3][0:2]
                        sMap.addLink(parent,child)
                        parent=child
                        child=string.join(parts[0:4],"-")
                        sMap.addLink(parent,child)
                        parent=child
                
                    for i in range (4,len(parts)):
                        child = parent +"-" +parts[i]
                        #add parent child
                        sMap.addLink(parent,child)
                        parent = child
                
                    intID= TCGAUtil.barcode_IntegrationId(sample)
                    if intDic.has_key(intID):
                        intDic[intID].append(uuid)
                        print intDic[intID]
                    else:
                        intDic[intID]=[uuid]

                process(obj['path'], outfile, samples, intDic)        
            
def process(file, outfile,samples, intDic):
    print file

    dir = os.path.dirname(file)
    fout=open(outfile,"w")
    sampleDic={}
    for i in range (0,len(samples)):
        sampleDic[samples[i]]= i+1

    #header
    fin =open(file,'r')
    fin.readline()
    fout.write("Sample")
    for intID in intDic.keys():
        fout.write("\t"+intID)
    fout.write("\n")

    #data
    while 1:
        line = fin.readline()
        if line=="":
            break
        data = string.split(line[:-1],"\t")
        fout.write(data[0])
        
        for intID in intDic.keys():
            sample_ids= intDic[intID]
            value = ""
            for sample in sample_ids:
                pos =sampleDic[sample]
                if data[pos]=="":
                    continue
                if value=="":
                    value =0.0
                value =value+float(data[pos])
            if value =="":
                fout.write("\t")
            else:
                value = value/len(sample_ids)
                fout.write("\t"+str(value))
        fout.write("\n")
    fout.close()
    return


cancer="PANCAN"
dir="preFreeze/TCGA/"
outDir="preFreezeCAVM/TCGA/"
log=0

REALRUN=0
#1 include genomic data
CAVMid (dir+cancer+"/", outDir+cancer+"/",cancer, log, REALRUN)

REALRUN=1
TCGASampleMap (dir, outDir, cancer,log, REALRUN):
