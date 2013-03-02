import sys,os,string,copy,json
from SampleMapNew import *
from CGDataLib import *
from ClinicalMatrixNew  import *
from ClinicalFeatureNew  import *
from IntegrationId  import *
from CGDataUtil import *

def runFlatten(inDir, outDir,REALRUN, SMAPNAME=None):
    dir = inDir
    bookDic={}
    sampleMaps={}
    ignore=0
    bookDic=cgWalk(dir,ignore)
    if not bookDic :
        print "repo has problem"
        return 0
    sampleMaps = collectSampleMaps(bookDic)
    missingMaps= collectMissingSampleMaps(bookDic)

    allMaps = sampleMaps.keys()
    allMaps.extend(missingMaps.keys())

    for sampleMap in allMaps:
        if SMAPNAME and SMAPNAME!=sampleMap:
            print "skip", sampleMap
            continue
        print sampleMap
        if sampleMap in missingMaps:
            #construct an empty sampleMap
            sMap = SampleMapNew(None,sampleMap)
            #fill sMap with individual nodes, no connection
            changed = checkIdsAllIn(sMap, bookDic)
            #build connection
        else:
            path = bookDic[sampleMap]['path']
            name = bookDic[sampleMap]['name']
            fin = open(path,'r')
            sMap = SampleMapNew(fin,name)
            if not sMap.getName():
                print "Fail to initiate", name
                return 0
            fin.close()
        
        r = flattenEachSampleMap(sMap,bookDic)
        if r== False:
            return 0
        finalClinicalMatrix,finalClinicalMatrixJSON,finalClinFeature,finalClinFeatureJSON= r
        if finalClinicalMatrix.getROWnum()!=0:
            outputEachSampleMapRelated(outDir, bookDic, sMap,
                                       finalClinicalMatrix,finalClinicalMatrixJSON,
                                       finalClinFeature,finalClinFeatureJSON,REALRUN)
            cpGenomicEachSample(REALRUN, outDir, bookDic, sMap)

            cpProbeMaps(REALRUN,outDir,bookDic,sMap)
    return 1

def flattenEachSampleMap(sMap, bookDic):
    sampleMap = sMap.getName()

    jsonName= trackName_fix(sampleMapBaseName(sMap)+"_clinicalMatrix")
    finalClinMatrix= ClinicalMatrixNew(None,jsonName)
    finalClinMatrixJSON={}
    finalClinMatrixJSON["name"]=jsonName
    finalClinMatrixJSON["type"]="clinicalMatrix"
    finalClinMatrixJSON["path"]=""
    finalClinMatrixJSON[":sampleMap"]=sampleMap

    clinFeatures=[]
    finalClinFeatureJSON=None
    finalClinFeature=None

    # add all ids to sMap
    sMapChanged= checkIdsAllIn(sMap, bookDic)

    #build initial clinical Matrix with sampleMap ids, all with empty data
    emptyData={}
    success = finalClinMatrix.addNewRows(sMap.getNodes(),emptyData)
    if not success:
        print "fail to add all initial ids from sampleMap"

    datasets = collectNamesBelongToSampleMap(bookDic, sampleMap)
    datasetsOrdered =[] #only the ClinicalMatrix ordered list
    for name in datasets:  
        obj= bookDic[name]
        if obj['type']=="clinicalMatrix":
            if obj.has_key('outOfDate') and obj['outOfDate'] in ["yes", "Yes","YES"]:
                datasetsOrdered.append(name)
            elif not obj.has_key('outOfDate') and  not obj.has_key('upToDate'):
                datasetsOrdered.insert(0,name)

    for name in datasets:  
        obj= bookDic[name]
        if obj['type']=="clinicalMatrix":
            if obj.has_key('upToDate') and obj['upToDate'] in ["yes", "Yes","YES"]:
                datasetsOrdered.insert(0,name)

    for name in datasetsOrdered:  
        obj= bookDic[name]
        if obj['type']=="clinicalMatrix":
            clinFeature=None
            #clinFeature obj
            if obj.has_key(':clinicalFeature'):
                path=  bookDic[obj[':clinicalFeature']]['path']
                neme = bookDic[obj[':clinicalFeature']]['name']
                clinFeature = ClinicalFeatureNew(path, name)

            #get matrix obj
            path = obj['path']
            name = obj['name']

            cMatrix = ClinicalMatrixNew(path,name,False, clinFeature)
            
            if finalClinMatrix==None:
                finalClinMatrix= cMatrix
                
            if finalClinMatrixJSON==None:
                finalClinMatrixJSON= obj

            #merge final and cMatrix
            if finalClinMatrix != cMatrix:
                r = finalClinMatrix.addNewCols(cMatrix,validation=True)
                if r!=True:
                    print "Fail to merge"
                    return False

            #add clinFeature
            if clinFeature:
                clinFeatures.append(clinFeature)
            
            #merge finalClinMatrixJSON with new json
            if finalClinMatrixJSON != obj:
                jsonName= trackName_fix(sampleMapBaseName(sMap)+"_clinicalMatrix")
                finalClinMatrixJSON= cgDataMergeJSON(finalClinMatrixJSON, obj, jsonName)

            # final ClinFeature json
            if clinFeature:
                clinFeatureJSON = bookDic[obj[':clinicalFeature']]
                if finalClinFeatureJSON==None:
                    finalClinFeatureJSON= clinFeatureJSON
                else:
                    jsonName=  trackName_fix(sampleMapBaseName(sMap)+"_clinicalFeature")
                    finalClinFeatureJSON["version"]=datetime.date.today().isoformat() 
                    finalClinFeatureJSON["type"]="clinicalFeature"
                    finalClinFeatureJSON["name"]=jsonName
                    finalClinFeatureJSON["cgDataVersion"]=1

    #final clinicalFeature
    if finalClinFeatureJSON:
        fout = open(".tmp",'w')
        fout.close()
        for clinF in clinFeatures:
            fout = open(".tmptmp",'w')
            clinF.store(fout)
            fout.close()
            os.system("cat .tmptmp >> .tmp")
        fin = open(".tmp",'r')
        finalClinFeature =ClinicalFeatureNew(fin,finalClinFeatureJSON['name'])
        if not finalClinFeature.isValid():
            print "final clinFeature file .tmp is invalid"
            return 0
        fin.close()

    #SURVIVAL analysis data
    foundE=0
    foundT=0
    if finalClinFeature:
        features= finalClinFeature.getFeatures()
        for feature in features:
            sameAs = finalClinFeature.getFeatureSameAs(feature)
            if sameAs =="_TIME_TO_EVENT":
                #check there is only one parameter is set to be _TIME_TO_EVENT
                if foundT==1:
                    print "ERROR there is already _TIME_TO_EVENT"
                    continue
                #check matrix does not have _TIME_TO_EVNET
                if sameAs in finalClinMatrix.getCOLs():
                    print "ERROR there is already _TIME_TO_EVENT in matrix"
                    continue
                #data check need to check these are floats or "" in both clinFeature and clinMatrix 
                GOOD=1
                if finalClinMatrix.isTypeFloat(feature)!= True:
                    print "ERROR _TIME_TO_EVENT parent feature values are not correct", finalClinMatrix.getColStates(feature)
                    GOOD=0
                if GOOD:
                    foundT=1
                    finalClinMatrix.addNewColfromOld(sameAs, feature)
                    finalClinFeature.setFeatureValueType(sameAs,"float")
                    
            if sameAs =="_EVENT":
                #check there is only one parameter is set to be _EVENT
                if foundE==1:
                    print "ERROR there is already _EVENT"
                    continue
                #check matrix does not have _EVNET
                if sameAs in finalClinMatrix.getCOLs():
                    print "ERROR there is already _EVENT in matrix"
                    continue
                #data check
                GOOD=1
                states= finalClinMatrix.getColStates(feature)
                """
                for state in states:
                    if state not in [0,1,"0","1",""]:
                        print "ERROR _EVENT values are not correct", state
                        GOOD=0
                        break
                """
                if len(states) not in [2,3]:
                    GOOD=0
                if len(states)==3 and states.count('')!=1:
                    GOOD=0

                if GOOD:
                    foundE=1
                    finalClinMatrix.addNewColfromOld(sameAs, feature)
                    finalClinFeature.setFeatureValueType(sameAs,"category")
                    #finalClinFeature.setFeatureStates(sameAs,["0","1"])
                    #finalClinFeature.setFeatureStateOrder(sameAs,["0","1"])

    #clinical data push down
    roots = sMap.allRoots()
    for root in roots:
        r = finalClinMatrix.pushToChildren (root,sMap)
        if r != True:
            print "Fail to push down"
            return 0
    print "after clinical push down", sampleMap,finalClinMatrix.getROWnum()

    # collect all genomic data
    keepSamples  = getAllGenomicIds(sMap, bookDic)

    # removing rows without genomic data from  clinical data matrix due to mysql enum limitation
    # should remove this step after the display functionality is done better, currently cgb clinical data range in feature control panel shows the full range of clinical data without checking if the specific track/dataset has the full value range.
    print "genomic sample count", len(keepSamples)
    success= finalClinMatrix.onlyKeepRows(keepSamples)
    if not success:
        print "fail to remove extra rows"
    else:
        print "after keeping sample with genomic data", finalClinMatrix.getROWnum()
        
    #add to the clinical matrix any samples with genomic data but no clinical data
    emptyData={}
    for col in finalClinMatrix.getCOLs():
        emptyData[col]=""
    success = finalClinMatrix.addNewRows(keepSamples,emptyData)
    if not success:
        print "fail to add new roows"
    else:
        print "after adding all genomic data", finalClinMatrix.getROWnum()

    if finalClinMatrix.validate() != True:
        print "Fail to validate"
        cMatrix = oldCMatrix
        return 0

    #identify empty features
    badFeatures= finalClinMatrix.badCols()
    if badFeatures:
        print "remove features", badFeatures

    # add _PATIENT col
    if finalClinMatrix.addColRoot(sMap) == None:
        print "Fail to addColRoot"
        return 0
            
    # add _INTEGRATION col
    intList=[]
    if bookDic[sampleMap].has_key(":integrationId"):
        intName=bookDic[sampleMap][":integrationId"]
        fin= open(bookDic[intName]["path"],"r")
        intId = IntegrationId(intName,fin)
        intList = intId.getList()
    finalClinMatrix.addColIntegration(sMap,intList)
            
    #final clinicalFeature
    if finalClinFeature:
        finalClinFeature.removeFeatures(badFeatures)
        
        finalClinFeature.cleanState()
        finalClinFeature.checkFeatureWithMatrix(finalClinMatrix)
        #clinicalFeature fillin ValueType
        finalClinFeature.fillInValueTypeWithMatrix(finalClinMatrix)
        #clinicalFeature fillin missing features
        finalClinFeature.fillInFeaturesWithMatrix(finalClinMatrix)
        #clinicalFeature fillin short and long titles
        finalClinFeature.fillInTitles()
        #clinicalFeature fillin priority visibility
        finalClinFeature.fillInPriorityVisibility()

        finalClinFeature.setFeatureShortTitle("_PATIENT","_PATIENT_ID")
        finalClinFeature.setFeatureLongTitle("_PATIENT","_PATIENT_ID")
        finalClinFeature.setFeatureShortTitle("_INTEGRATION","_SAMPLE_ID")
        finalClinFeature.setFeatureLongTitle("_INTEGRATION","_SAMPLE_ID")

    print sampleMap,finalClinMatrix.getROWnum()
    return finalClinMatrix,finalClinMatrixJSON, finalClinFeature, finalClinFeatureJSON


def outputEachSampleMapRelated(outDir, bookDic, sMap,
                               finalClinMatrix,finalClinMatrixJSON,
                               finalClinFeature,finalClinFeatureJSON,REALRUN):
    sampleMap = sMap.getName()
    if not os.path.exists( outDir ):
        os.makedirs( outDir )
    dataPackageDir = outDir + sampleMapBaseName(sMap)
    if not os.path.exists( dataPackageDir ):
        os.makedirs( dataPackageDir )
    else:  #clean out the existing dataPackageDir to remove all old datafiles if realrun
        if REALRUN:
            os.system("rm -rf "+dataPackageDir+"/*")
        
    #copy sampleMap and .json
    path = bookDic[sampleMap]['path']
    os.system("cp "+path+".json "+dataPackageDir+"/")
    fout = open(dataPackageDir+"/"+os.path.basename(path),'w')
    sMap.store(fout)
    fout.close()

    #copy integratiionId and .json, ignore it for now
    """
    if bookDic[sampleMap].has_key(":integrationId"):
        intName=bookDic[sampleMap][":integrationId"]
        path = bookDic[intName]['path']
        os.system("cp "+path+" "+dataPackageDir+"/")
        os.system("cp "+path+".json "+dataPackageDir+"/")
    """
        
    #output clinicalMatrix data
    fout = open(dataPackageDir+"/"+sampleMapBaseName(sMap)+"_clinicalMatrix",'w')
    finalClinMatrix.store(fout)
    fout.close()
        
    #copy clincalMatrix json
    finalClinMatrixJSON.pop('path')
    fout = open(dataPackageDir+"/"+sampleMapBaseName(sMap)+"_clinicalMatrix.json",'w')
    if finalClinFeatureJSON != None:
        finalClinMatrixJSON[':clinicalFeature']= finalClinFeatureJSON["name"]
    if not finalClinMatrixJSON.has_key("version"):
        finalClinMatrixJSON["version"]= bookDic[sampleMap]["version"]
    fout.write(json.dumps(finalClinMatrixJSON, indent=-1))
    fout.close()

    #output clinicalFeature data by concatenation
    if finalClinFeatureJSON != None:
        targetfile = dataPackageDir+"/"+sampleMapBaseName(sMap)+"_clinicalFeature"
        fout = open(targetfile,'w')
        finalClinFeature.store(fout)

    #output clinicalFeatureJSON
    if finalClinFeatureJSON != None:
        finalClinFeatureJSON.pop('path')
        fout = open(dataPackageDir+"/"+sampleMapBaseName(sMap)+"_clinicalFeature.json",'w')
        fout.write(json.dumps(finalClinFeatureJSON, indent=-1))
        fout.close()

def cpGenomicEachSample(REALRUN, outDir, bookDic, sMap):
    dataPackageDir = outDir + sampleMapBaseName(sMap)
    for name in  collectNamesBelongToSampleMap(bookDic, sMap.getName()):    
        J = bookDic[name]
        if J['type'] not in [ "clinicalMatrix","sampleMap"]:
            path = J['path']
            if J['type']=="genomicMatrix":
                # check redistribution tag, if it is false (any forms) convert to python False, if not present, set to python True
                if not J.has_key("redistribution"):
                    J["redistribution"]=True
                elif J["redistribution"] in ["false","FALSE","False", False,"0", 0 ,"no","NO","No"]:
                    J["redistribution"]=False
                elif J["redistribution"] in ["true","TRUE","True", True,"1", 1 ,"yes","YES","Yes"]:
                    J["redistribution"]=True

                # check security tag, if it is private (any forms) set to "private", if not present, set to "public"
                if not J.has_key("security"):
                    J["security"]="public"
                elif J["security"] in ["private","PRIVATE","Private","controlled-access"]:
                    J["security"]="private"
                
            outfile = dataPackageDir+"/"+os.path.basename(path+".json")
            oHandle=open(outfile,"w")
            oHandle.write( json.dumps( J, indent=-1 ) )
            oHandle.close()
            
            if REALRUN:
                os.system("cp "+path+" "+dataPackageDir+"/")
    return


def cpProbeMaps(REALRUN,outDir,bookDic, sMap):
    dataPackageDir = outDir + sampleMapBaseName(sMap)
    for name in collectProbeMapBelongToSampleMap(bookDic, sMap.getName()):
        J = bookDic[name]
        if J['type'] != "probeMap":
            return False
        path = J['path']
        os.system("cp "+path+".json "+dataPackageDir+"/")
        if REALRUN:
            os.system("cp "+path+" "+dataPackageDir+"/")
    return

def sampleMapBaseName(sMap):
    baseName = sMap.getName()
    baseName = string.replace(baseName,".sampleMap","")
    baseName = string.replace(baseName,"_sampleMap","")
    baseName = string.replace(baseName,"sampleMap","")
    baseName = string.replace(baseName,"TCGA.","")
    return baseName
