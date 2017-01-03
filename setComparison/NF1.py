import string, sys, os
import scipy.stats
import numpy
import math

sys.path.insert(0, "../Nof1Analysis/")
import Nof1_functions
import NF1mut
import NF1wt

samples_mut = NF1mut.samples_mut
samples_wt = NF1wt.samples_wt

hub = "https://tcgapancan.xenahubs.net"

#chiq_contigency
def chi2_contingency_by_probes (hub, dataset, probes, samples1, samples2, output, kp = None):
    fout = open(output,'w')
    o_list =["probe", "chi2_stat", "Gtest_p", "Mutual_information"]
    if kp:
        o_list.append("observed")
        o_list.append("expected")
        
    fout.write(string.join(o_list, '\t') +'\n')

    N = 100
    for i in range (0, len(probes), N):
        pList = probes[i:i+N]
        values1 = Nof1_functions.Probes_values (hub, dataset, samples1, pList)
        values2 = Nof1_functions.Probes_values (hub, dataset, samples2, pList)

        for j in range(0, len(pList)):
            probe = pList[j]
            v1 = values1[j]
            v1 = [x for x in v1 if x != 'NaN']

            v2 = values2[j]
            v2 = [x for x in v2 if x != 'NaN']

            codes = numpy.unique(v1 +v2)
            if len(codes) == 1:
                continue

            array1 = map(lambda code : len([x for x in v1 if x == code]), codes)
            array2 = map(lambda code : len([x for x in v2 if x == code]), codes)
            observed = [[array1, array2]]
            try:
                chi2, p, dof, expected = scipy.stats.chi2_contingency(observed, lambda_="log-likelihood")
                o_list = []
                if len(array1) == 2 and len(array2) ==2: #only makes sense for 2 by 2 table, key parameter: 0,1
                    MI = chi2 / (2*len(v1) + len(v2)) 
                    o_list = [probe, str(chi2), str(p), str(MI)]  
                else:
                    o_list = [probe, str(chi2), str(p), '']
                if kp:
                    o_list.append(str(observed[0][kp[0]][kp[1]]))
                    o_list.append(str(expected[0][kp[0]][kp[1]]))
                fout.write(string.join(o_list,'\t')+'\n')
                #print probe, codes, chi2, p, MI, observed, expected
            except:
                print probe, "bad"

    fout.close()

#ttest
def ttest_by_probes (hub, dataset, probes, samples1, samples2, output):
    fout = open(output,'w')
    N = 100
    for i in range (0, len(probes), N):
        pList = probes[i:i+N]
        values1 = Nof1_functions.Probes_values (hub, dataset, samples1, pList)
        values2 = Nof1_functions.Probes_values (hub, dataset, samples2, pList)

        for j in range(0, len(pList)):
            probe = pList[j]
            v1 = values1[j]
            v1 = map(lambda x: float(x), v1)
            v1 = [x for x in v1 if math.isnan(x) == 0]

            v2 = values2[j]
            v2 = map(lambda x: float(x), v2)
            v2 = [x for x in v2 if math.isnan(x) == 0]

            try:
                tStat, p = scipy.stats.ttest_ind(v1, v2, equal_var=False)
                fout.write(probe + '\t' + str(tStat) + '\t' + str(p) + '\n')
            except:
                print probe
    fout.close()

"""
dataset_cnv = "broad.mit.edu_PANCAN_Genome_Wide_SNP_6_whitelisted.gene.xena"
cnv_genes = Nof1_functions.dataset_fields(hub, dataset_cnv)
output = 'ttest_cnv'
ttest_by_probes (hub, dataset_cnv, cnv_genes, samples_mut, samples_wt, output)
"""

dataset_mut = "mc3.v0.2.8.PUBLIC.nonsilentGene.xena"
mut_genes = Nof1_functions.dataset_fields(hub, dataset_mut)
output = 'chisqure_mut'
key_parameter = [0,1]  #mutants, value =1
chi2_contingency_by_probes (hub, dataset_mut, mut_genes, samples_mut, samples_wt, output, key_parameter)



