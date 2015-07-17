repoMeta = {
    "specimen":{
        "dataSubType":"phenotype",
        "type":"clinicalMatrix",
        ":clinicalFeature":"clinicalFeature",
        "label":"Phenotype specimen",
        },
    "donor":{
        "dataSubType":"phenotype",
        "type":"clinicalMatrix",
        ":clinicalFeature":"clinicalFeature",
        "label":"Phenotype donor",
        },
    "donor_family":{
        "dataSubType":"phenotype",
        "type":"clinicalMatrix",
        ":clinicalFeature":"clinicalFeature",
        "label":"Phenotype donor family history",
        },
    "donor_therapy":{
        "dataSubType":"phenotype",
        "type":"clinicalMatrix",
        ":clinicalFeature":"clinicalFeature",
        "label":"Phenotype donor therapy",
        },
    "donor_exposure":{
        "dataSubType":"phenotype",
        "type":"clinicalMatrix",
        ":clinicalFeature":"clinicalFeature",
        "label":"Phenotype donor exposure",
        },
    "simple_somatic_mutation.open":{
        "dataSubType":"somatic mutation (SNPs and small INDELs)",
        "type":"mutationVector",
        "assembly":"hg19",
        "label":"Somatic mutation (SNPs and small INDELs)",
        },
    "mutGene":{
        "dataSubType":"somatic non-silent mutation (gene-level)",
        "type":"genomicMatrix",
        ":probeMap":"hugo_hg18",
        "label":"Somatic gene-level non-silent mutation",
        "colNormalization":False,
        },
    "exp_array":{
        "dataSubType":"gene expression Array",
        "type":"genomicMatrix",
        "label":"Gene expression array",
        "colNormalization":True,
        },
    "exp_seq":{
        "dataSubType":"gene expression RNAseq",
        "type":"genomicMatrix",
        "label":"Gene expression RNAseq",
        ":probeMap":"ensembleGene_hg19",
        "colNormalization":True,
        },
    "meth_array":{
        "dataSubType":"DNA methylation",
        "type":"genomicMatrix",
        "label":"DNA methylation",
        ":probeMap":"illuminaMethyl450_hg19_GPL16304",
        "min":0,
        "max":1,
        "colNormalization":False,
        },

    "mirna_seq":{
        "dataSubType":"miRNA expression",
        "type":"genomicMatrix",
        "label":"miRNA expression RNAseq",
        ":probeMap":"miRBase_primary_transcript_hg19",
        "colNormalization":True,
        },
}
