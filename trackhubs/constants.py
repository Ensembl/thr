"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

FILE_TYPES = [
    'altGraphX', 'bam', 'bed', 'bed5FloatScore', 'bedGraph', 'bedRnaElements', 'bigBarChart', 'bigBed',
    'bigInteract', 'bigLolly', 'bigPsl', 'bigChain', 'bigMaf', 'bigWig', 'broadPeak', 'chain', 'clonePos',
    'coloredExon', 'ctgPos', 'downloadsOnly', 'encodeFiveC', 'expRatio', 'factorSource', 'genePred', 'gvf',
    'hic', 'ld2', 'narrowPeak', 'netAlign', 'peptideMapping', 'psl', 'rmsk', 'snake', 'vcfTabix', 'wig', 'wigMaf'
]

DATA_TYPES = ['genomics', 'proteomics', 'epigenomics', 'transcriptomics']  # default: 'genomics'

VISIBILITY = ['hide', 'dense', 'squish', 'pack', 'full']  # default: 'hide'

# These mappings have been derived from the list of UCSC genome releases at:
# https://genome.ucsc.edu/FAQ/FAQreleases.html#release1

UCSC_TO_INSDC = {
    'hg38': 'GCA_000001405.15',  # 'GRCh38',
    'hg19': 'GCA_000001405.1',  # 'GRCh37',
    'hg18': 'GCF_000001405.12',  # 'NCBI36',
    'hg17': 'GCF_000001405.11',  # 'NCBI35',
    'hg16': 'GCF_000001405.10',  # 'NCBI34',
    # alpaca
    'vicpac2': 'GCA_000164845.2',  # 'Vicugna_pacos-2.0.1'
    'vicpac1': 'GCA_000164845.1',  # 'VicPac1.0', # no NCBI syn
    # armadillo
    'dasnov3': 'GCA_000208655.2',  # 'Dasnov3.0',
    # bushbaby
    'otogar3': 'GCA_000181295.3',  # 'OtoGar3',
    # baboon
    # 'papham1': 'Pham_1.0', # not found on NCBI
    'papanu2': 'GCA_000264685.1',  # 'Panu_2.0',
    # cat
    'felcat5': 'GCA_000181335.2',  # 'Felis_catus-6.2',
    'felcat4': 'GCA_000003115.1',  # 'catChrV17e',
    # 'felcat3': '', # no name found
    # chimp
    'pantro4': 'GCA_000001515.4',  # 'Pan_troglodytes-2.1.4',
    'pantro3': 'GCA_000001515.3',  # 'Pan_troglodytes-2.1.3',
    'pantro2': 'GCF_000001515.3',  # 'Pan_troglodytes-2.1', # no syn on NCBI
    # 'pantro1': '', # not found
    # chinese hamster
    'crigri1': 'GCA_000419365.1',  # 'C_griseus_v1.0', # no syn on NCBI
    # cow
    'bostau8': 'GCA_000003055.5',  # 'Bos_taurus_UMD_3.1.1', # no syn on NCBI
    'bostau7': 'GCA_000003205.4',  # 'Btau_4.6.1',
    'bostau6': 'GCA_000003055.3',  # 'Bos_taurus_UMD_3.1', # no synonym reported by NCBI and E, E
    'bostau4': 'GCF_000003205.2',  # 'Btau_4.0',
    'bostau3': 'GCF_000003205.1',  # 'Btau_3.1', # no synonym reported by NCBI
    # 'bostau2': 'Btau_2.0', # no Btau_2.0 entry in NCBI
    # 'bostau1': 'Btau_1.0', # no Btau_1.0 entry in NCBI
    # dog
    'canFam3': 'GCA_000002285.2',  # 'CanFam3.1',
    'canFam2': 'GCA_000002285.1',  # 'CanFam2.0',
    # 'canFam1': '', # not found on NCBI
    # dolphin
    'turtru2': 'GCA_000151865.2',  # 'Ttru_1.4'
    # elephant
    'loxafr3': 'GCA_000001905.1',  # 'Loxafr3.0',
    # ferret
    'musfur1': 'GCA_000215625.1',  # 'MusPutFur1.0',
    # gibbon
    'nomleu3': 'GCA_000146795.3',  # 'Nleu_3.0',
    'nomleu2': 'GCA_000146795.2',  # 'Nleu1.1',
    'nomleu1': 'GCA_000146795.1',  # 'Nleu1.0',
    # gorilla
    'gorgor3': 'GCA_000151905.1',  # 'gorGor3.1',
    # guinea pig
    'cavpor3': 'GCA_000151735.1',  # 'Cavpor3.0',
    # hedgehog
    'erieur2': 'GCA_000296755.1',  # 'EriEur2.0', # no syn on NCBI
    'erieur1': 'GCA_000181395.1',  # ASM18139v1 (no Draft_v1 entry in NCBI)
    # horse
    'equcab2': 'GCA_000002305.1',  # 'EquCab2.0',
    # 'equcab1': 'EquCab1.0', # no EquCab1.0 entry on NCBI
    # kangaroo rat (Dipodomys merriami not found, refer to Dipodomys ordii instead
    'dipord1': 'GCA_000151885.1',  # DipOrd1.0
    # manatee
    'triman1': 'GCA_000243295.1',  # 'TriManLat1.0',
    # marmoset
    'caljac3': 'GCA_000004665.1',  # 'Callithrix_jacchus-v3.2',
    # 'caljac1': 'Callithrix_jacchus-v2.0.2', # no Callithrix_jacchus-v2.0.2 entry on NCBI
    # megabat
    'ptevam1': 'GCA_000151845.1',  # 'Ptevap1.0',
    # microbat
    'myoluc2': 'GCA_000147115.1',  # 'Myoluc2.0',
    # minke whale
    'balacu1': 'GCA_000493695.1',  # 'BalAcu1.0', # no synonym in NCBI
    # mouse
    'mm10': 'GCA_000001635.2',  # 'GRCm38',
    'mm9': 'GCA_000001635.1',  # 'MGSCv37',
    'mm8': 'GCF_000001635.15',  # 'MGSCv36',
    'mm7': 'GCF_000001635.14',  # 'MGSCv35',
    'mm39': 'GCA_000001635.9',  # 'GRCm39',
    # mm6': ''MGSCv34', # no MGSCv34 entry
    # mm5': ''MGSCv33', # no MGSCv33 entry
    # mm4': ''MGSCv32', # no MGSCv32 entry
    # mm3': ''MGSCv30', # no MGSCv30 entry
    # mm2': ''MGSCv3', # no MGSCv3 entry
    # mm1': ''MGSCv2', # no MGSCv2 entry
    # mouse lemur
    'micmur1': 'GCA_000165445.1',  # 'ASM16544v1', # no MicMur1.0 entry on NCBI
    # naked mole rat
    'hetgla2': 'GCA_000247695.1',  # 'HetGla_female_1.0',
    'hetgla1': 'GCA_000230445.1',  # 'HetGla_1.0', # no synonym on NCBI
    # opossum
    'mondom5': 'GCF_000002295.2',  # 'MonDom5',
    # 'mondom4': 'MonDom4', # no MonDom4 entry
    # 'mondom1': 'MonDom1', # no MonDom1 entry
    # orangutan
    # 'ponabe2': 'Pongo_albelii-2.0.2', # NCBI reports instead
    'ponabe2': 'GCA_000001545.3',  # 'P_pygmaeus_2.0.2',
    # panda
    'ailmel1': 'GCA_000004335.1',  # 'AilMel_1.0',
    # pig
    'susscr3': 'GCA_000003025.4',  # 'Sscrofa10.2',
    'susscr2': 'GCA_000003025.2',  # 'Sscrofa9.2', # no syn on NCBI
    # pika
    'ochpri3': 'GCA_000292845.1',  # 'OchPri3.0', # no syn on NCBI
    'ochpri2': 'GCA_000164825.1',  # 'OchPri2'
    # 'ochpri2': 'GCA_000164825.1', # 'ASM16482v1',
    # platypus
    'ornana1': 'GCF_000002275.2',  # 'Ornithorhynchus_anatinus-5.0.1', # no syn on NCBI
    # rabbit
    'orycun2': 'GCA_000003625.1',  # 'OryCun2.0',
    # rat
    'rn6': 'GCA_000001895.4',  # 'Rnor_6.0',
    'rn5': 'GCA_000001895.3',  # 'Rnor_5.0',
    'rn4': 'GCF_000001895.3',  # 'RGSC_v3.4', # no syn on NCBI
    # rn3': ''RGSC_v3.1', # not found
    # rn2': ''RGSC_v2.1', # not found
    # rn1': ''RGSC_v1.0', # not found
    # rhesus (Macaca mulatta)
    'rheMac3': 'GCA_000230795.1',  # 'CR_1.0',
    'rheMac2': 'GCA_000002255.1',  # 'Mmul_051212',
    # 'rheMac1': 'Mmul_0.1', # not found
    'rheMac8': 'GCA_000772875.3',  # 'Mmul_8.0.1',
    # rock hyrax
    'procap1': 'GCA_000152225.1',  # 'Procap1.0',
    # sheep
    'oviari3': 'GCA_000298735.1',  # 'Oar_v3.1',
    # 'oviari1': '', # not found
    # shrew
    'sorara2': 'GCA_000181275.2',  # 'SorAra2.0',
    'sorara1': 'GCA_000181275.1',  # ASM18127v1, 'SorAra1.0' not found
    # sloth
    'chohof1': 'GCA_000164785.1',  # 'ChoHof1.0',
    # squirrel
    'spetri2': 'GCA_000236235.1',  # 'SpeTri2.0',
    # squirrel monkey
    'saibol1': 'GCA_000235385.1',  # 'SaiBol1.0',
    # tarsier
    'tarsyr1': 'GCA_000164805.1',  # 'Tarsyr1.0',
    # tasmanian devil
    'sarhar1': 'GCA_000189315.1',  # 'Devil_ref v7.0',
    # tenrec
    'echtel2': 'GCA_000313985.1',  # 'EchTel2.0',
    # 'echtel1': 'echTel1', # not found
    # tree shrew
    # 'tupbel1': 'Tupbel1.0', # no Tupebel1.0 found
    # wallaby
    'maceug2': 'GCA_000004035.1',  # 'Meug_1.1', # no syn on NCBI
    # white rhinoceros
    'cersim1': 'GCA_000283155.1',  # 'CerSimSim1.0',
    #
    # Vertebrates
    #
    # american alligator
    'allmis1': 'GCA_000281125.1',  # 'allMis0.2',
    # atlantic cod
    'gadmor1': 'GCA_000231765.1',  # 'GadMor_May2010',
    # budgerigar
    'melund1': 'GCA_000238935.1',  # 'Melopsittacus_undulatus_6.3',
    # chicken
    'galgal4': 'GCA_000002315.2',  # 'Gallus_gallus-4.0',
    'galgal3': 'GCA_000002315.1',  # 'Gallus_gallus-2.1',
    # 'galgal2': 'Gallus-gallus-1.0', # no Gallus-gallus-1.0 on NCBI
    'galGal5': 'GCA_000002315.3',  # 'Gallus_gallus-5.0',
    # coelacanth
    'latcha1': 'GCA_000225785.1',  # 'LatCha1',
    # elephant shark
    'calmil1': 'GCA_000165045.2',  # 'Callorhinchus_milli-6.1.3', # no syn on NCBI
    # fugu
    'fr3': 'GCA_000180615.2',  # 'FUGU5',
    # 'fr2': '', # not found
    # 'fr1': '', # not found
    # lamprey
    'petmar2': 'GCA_000148955.1',  # 'Petromyzon_marinus-7.0',
    # 'petmar1': '', # not found
    # lizard (Anolis carolinensis)
    'anocar2': 'GCA_000090745.1',  # 'AnoCar2.0', E
    # 'anocar1': 'AnoCar1', # not found
    # medaka
    # 'orylat2': '', # not found
    # medium ground finch
    'geofor1': 'GCA_000277835.1',  # 'GeoFor_1.0', # no syn on NCBI
    # nile tilapia
    'orenil2': 'GCA_000188235.2',  # 'Orenil1.1',
    # painted turtle
    'chrpic1': 'GCA_000241765.1',  # 'Chrysemys_picta_bellii-3.0.1',
    # stickleback
    'gasacu1': 'GCA_000180675.1',  # ASM18067v1
    # tetraodon
    # 'tetnig2': '',
    'tetnig1': 'GCA_000180735.1',  # 'ASM18073v1',
    # turkey
    'melgal1': 'GCA_000146605.2',  # 'Turkey_2.01',
    # xenopus tropicalis
    'xentro3': 'GCA_000004195.1',  # 'v4.2',
    # 'xentro2': 'v4.1', # not found
    # 'xentro2': 'v3.0', # not found
    # zebra finch
    # 'taegut2': '', # not found
    'taegut1': 'GCA_000151805.2',  # 'Taeniopygia_guttata-3.2.4',
    # zebrafish
    'danrer11': 'GCA_000002035.4',  # GRCz11
    'danrer10': 'GCA_000002035.3',  # 'GRCz10', no syn on on NCBI
    'danrer7': 'GCA_000002035.2',  # 'Zv9'
    'danrer6': 'GCA_000002035.1',  # 'Zv8', no syn on on NCBI
    'danrer5': 'GCF_000002035.1',  # 'Zv7',
    # 'danrer4': 'Zv6', # not found on NCBI
    # 'danrer3': 'Zv5', # not found on NCBI
    # 'danrer2': 'Zv4', # not found on NCBI
    # 'danrer1': 'Zv3', # not found on NCBI
    #
    # Deuterostomes
    #
    # C. intestinalis
    'ci2': 'GCA_000224145.1',  # derived from ensembl meta
    'ci1': 'GCA_000183065.1',  # 'v1.0',
    # lancelet, not found
    # 'braflo1': '',
    # Strongylocentrotus purpuratus
    'strpur2': 'GCF_000002235.2',  # 'Spur_v2.1',
    'strpur1': 'GCF_000002235.1',  # 'Spur_0.5', # no syn on NCBI
    #
    # Insects
    #
    # Apis mellifera
    'apimel2': 'GCF_000002195.1',  # 'Amel_2.0', # no syn on NCBI
    # 'apimel1': 'v.Amel_1.2', # no v.Amel_1.2 entry on NCBI
    'amel5': 'GCA_000002195.1',  # 'Amel_4.5' , # no syn on NCBI
    # Anopheles gambiae
    # 'anogam1': 'v.MOZ2', # not found
    # Drosophila ananassae
    'droana3': 'GCA_000005115.1',  # 'dana_caf1', # no droAna3 UCSC syn
    # 'droana2': '', # not found
    # 'droana1': '', # not found
    # Drosophila erecta
    'droere2': 'GCA_000005135.1',  # 'dere_caf1', # no droEre2 UCSC syn
    # 'droere1': '', # not found
    # Drosophila grimshawi
    'drogri2': 'GCA_000005155.1',  # 'dgri_caf1', # no droGri2 UCSC syn
    # 'drogri1': '', # not found
    # Drosophila melanogaster
    'dm6': 'GCA_000001215.4',  # 'Release 6 plus ISO1 MT',
    'dm3': 'GCA_000001215.2',  # 'Release 5',
    # dm2': ''Release 4', # no Release 4
    # dm1': ''Release 3', # no Release 3
    # Drosophila mojavensis
    'dromoj3': 'GCA_000005175.1',  # 'dmoj_caf1', # no droMoj3 UCSC syn
    # 'dromoj2': '', # not found
    # 'dromoj1': '', # not found
    # Drosophila persimilis
    'droper1': 'GCA_000005195.1',  # 'dper_caf1',
    # Drosophila pseudoobscura, not found
    # 'dp3': '',
    # 'dp2': '',
    # Drosophila sechellia
    'drosec1': 'GCA_000005215.1',  # 'dsec_caf1',
    # Drosophila simulans
    'drosim1': 'GCA_000259055.1',  # 'dsim_caf1', # not sure, several v1 for different strains on NCBI
    # Drosophila virilis
    'drovir3': 'GCA_000005245.1',  # 'dvir_caf1', # no droVir3 UCSC syn
    # 'drovir2': '', # not found
    # 'drovir1': '', # not found
    # Drosophila yakuba
    # 'droyak2': '', # not found
    # 'droyak1': '', # not found
    #
    # Nematodes
    #
    # Caenorhabditis brenneri
    'caepb2': 'GCA_000143925.1',  # 'C_brenneri-6.0.1', # not sure (not 2008)
    # 'caepb1': '', # not found
    # Caenorhabditis briggsae
    'cb3': 'GCA_000004555.2',  # 'Cb3',
    # 'cb1': '', # not found
    # Caenorhabditis elegans
    'ce10': 'GCA_000002985.2',  # 'WBcel215',
    # ce6/WS190 doesn't have GenBank Assembly Accession
    # 'WS190' has RefSeq Assembly Accession 'GCF_000002985.1'
    # we decided to assign 'GCA_000002985.1' to it
    # See History section here: https://www.ncbi.nlm.nih.gov/assembly/GCF_000002985.1
    'ce6': 'GCA_000002985.1',
    # ce4 ': '',
    # ce2 ': '',
    # ce1 ': '',
    # Caenorhabditis japonica
    # 'caejap1': '', # not found
    # Caenorhabditis remanei
    # 'caerem3': '', # not found
    # 'caerem2': '',
    # Pristionchus pacificus
    # 'pripac1': '', # not found
    #
    # Other
    #
    # sea hare
    'aplcal1': 'GCA_000002075.1',  # 'Aplcal2.0',
    # Yeast
    'sacCer3': 'GCA_000146045.2',  # 'R64-1-1',
    # 'sacCer2': '', # not found
    # 'sacCer1': '', # not found
    # https://epd.expasy.org/epd/ucsc/epdHub/spo2/description.html
    'spo2': 'GCA_000002945.2',  # ASM294v2
    # malaria (plasmodium)
    # https://epd.expasy.org/epd/ucsc/epdHub/pfa2/description.html
    'pfa2': 'GCA_000002765.2',  # ASM276v2
    # maize
    # https://epd.expasy.org/epd/ucsc/epdHub/zm3/description.html
    'zm3': 'GCA_000005005.5',
    # common water flea (daphnia pulex)
    # https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_021134715.1
    'dpu2': 'GCA_021134715.1',  # ASM2113471v1
    # ebola virus
    # 'ebovir3': '', # not found
    #
    # And the following mappings have been derived by looking
    # the UCSC synonyms for the assemblies in the public hubs at:
    # http://genome.ucsc.edu/cgi-bin/hgHubConnect
    #
    # http://smithlab.usc.edu/trackdata/methylation/hub.txt
    #
    # Arabidopsis thaliana
    # 'tair10': 'GCA_000001735.1', # TAIR10
    # 'tair9 ': 'GCA_000001735.1', # TAIR9
    #
    # http://genome-test.gi.ucsc.edu/~hiram/hubs/Plants/hub.txt
    #
    # Arabidopsis thaliana
    'araTha1': 'GCA_000001735.1',  # TAIR10
    # Ricinus communis
    'riccom1': 'GCA_000151685.2',  # JCVI_RCG_1.1
    # brassica rapa
    'brarap1': 'GCA_000309985.1',  # Brapa_1.0
    #
    # http://genome-test.gi.ucsc.edu/~nknguyen/ecoli/publicHubs/pangenome/hub.txt
    # http://genome-test.gi.ucsc.edu/~nknguyen/ecoli/publicHubs/pangenomeWithDups/hub.txt
    #
    # Escherichia coli 042
    'escherichiaColi042Uid161985': 'GCA_000027125.1',  # ASM2712v1
    # Escherichia coli 536
    'escherichiaColi536Uid58531': 'GCA_000013305.1',  # ASM1330v1
    # Escherichia coli 55989
    'escherichiaColi55989Uid59383': 'GCA_000026245.1',  # ASM2624v1
    # Escherichia coli ABU 83972
    'escherichiaColiAbu83972Uid161975': 'GCA_000148365.1',  # ASM14836v1
    # Escherichia coli APEC O1
    'escherichiaColiApecO1Uid58623': 'GCA_000014845.1',  # ASM1484v1
    # Escherichia coli ATCC 8739
    'escherichiaColiAtcc8739Uid58783': 'GCA_000019385.1',  # ASM1938v1
    # Escherichia coli BL21 DE3
    'escherichiaColiBl21De3Uid161947': 'GCA_000022665.2',  # ASM2266v1
    'escherichiaColiBl21De3Uid161949': 'GCA_000009565.2',  # ASM956v1
    # Escherichia coli BL21 Gold DE3 pLysS AG
    'escherichiaColiBl21GoldDe3PlyssAgUid59245': 'GCA_000023665.1',  # ASM2366v1
    # Escherichia coli BW2952
    'escherichiaColiBw2952Uid59391': 'GCA_000022345.1',  # ASM2234v1
    'escherichiaColiBRel606Uid58803': 'GCA_000017985.1',  # ASM1798v1
    'escherichiaColiCft073Uid57915': 'GCA_000007445.1',  # ASM744v1
    'escherichiaColiDh1Uid161951': 'GCA_000023365.1',  # ASM2336v1
    'escherichiaColiDh1Uid162051': 'GCA_000023365.1',  # ASM2336v1
    'escherichiaColiCloneDI14Uid162049': 'GCA_000233895.1',  # ASM23389v1
    'escherichiaColiCloneDI2Uid162047': 'GCA_000233875.1',  # ASM23387v1
    'escherichiaColiE24377aUid58395': 'GCA_000017745.1',  # ASM1774v1
    'escherichiaColiEd1aUid59379': 'GCA_000026305.1',  # ASM2630v1
    'escherichiaColiEtecH10407Uid161993': 'GCA_000210475.1',  # ASM21047v1
    'escherichiaColiHsUid58393': 'GCA_000017765.1',  # ASM1776v1
    'escherichiaColiIai1Uid59377': 'GCA_000026265.1',  # ASM2626v1
    'escherichiaColiIai39Uid59381': 'GCA_000026345.1',  # ASM2634v1
    'escherichiaColiIhe3034Uid162007': 'GCA_000025745.1',  # ASM2574v1
    'escherichiaColiK12SubstrDh10bUid58979': 'GCA_000019425.1',  # ASM1942v1
    'escherichiaColiK12SubstrMg1655Uid57779': 'GCA_000005845.1',  # ASM584v1
    'escherichiaColiK12SubstrW3110Uid161931': 'GCA_000010245.1',  # ASM1024v1
    'escherichiaColiKo11flUid162099': 'GCA_000147855.2',  # EKO11
    'escherichiaColiKo11flUid52593': 'GCA_000147855.2',  # EKO11
    'escherichiaColiLf82Uid161965': 'GCA_000284495.1',  # ASM28449v1
    'escherichiaColiNa114Uid162139': 'GCA_000214765.2',  # ASM21476v2
    'escherichiaColiO103H212009Uid41013': 'GCA_000010745.1',  # ASM1074v1
    'escherichiaColiO104H42009el2050Uid175905': 'GCA_000299255.1',  # ASM29925v1
    'escherichiaColiO104H42009el2071Uid176128': 'GCA_000299475.1',  # ASM29947v1
    'escherichiaColiO104H42011c3493Uid176127': 'GCA_000299455.1',  # ASM29945v1
    'escherichiaColiO111H11128Uid41023': 'GCA_000010765.1',  # ASM1076v1
    'escherichiaColiO127H6E234869Uid59343': 'GCA_000026545.1',  # ASM2654v1
    'escherichiaColiO157H7Ec4115Uid59091': 'GCA_000021125.1',  # ASM2112v1
    'escherichiaColiO157H7Edl933Uid57831': 'GCA_000006665.1',  # ASM666v1
    'escherichiaColiO157H7SakaiUid57781': 'GCA_000008865.1',  # ASM886v1
    'escherichiaColiO157H7Tw14359Uid59235': 'GCA_000022225.1',  # ASM2222v1
    'escherichiaColiO26H1111368Uid41021': 'GCA_000091005.1',  # ASM9100v1
    'escherichiaColiO55H7Cb9615Uid46655': 'GCA_000025165.1',  # ASM2516v1
    'escherichiaColiO55H7Rm12579Uid162153': 'GCA_000245515.1',  # ASM24551v1
    'escherichiaColiO7K1Ce10Uid162115': 'GCA_000227625.1',  # ASM22762v1
    'escherichiaColiO83H1Nrg857cUid161987': 'GCA_000183345.1',  # ASM18334v1
    'escherichiaColiP12bUid162061': 'GCA_000257275.1',  # ASM25727v1
    'escherichiaColiS88Uid62979': 'GCA_000026285.1',  # ASM2628v1
    'escherichiaColiSe11Uid59425': 'GCA_000010385.1',  # ASM1038v1
    'escherichiaColiSe15Uid161939': 'GCA_000010485.1',  # ASM1048v1
    'escherichiaColiSms35Uid58919': 'GCA_000019645.1',  # ASM1964v1
    'shigellaBoydiiSb227Uid58215': 'GCA_000012025.1',  # ASM1202v1
    'shigellaBoydiiCdc308394Uid58415': 'GCA_000020185.1',  # ASM2018v1
    'shigellaDysenteriaeSd197Uid58213': 'GCA_000012005.1',  # ASM1200v1
    'shigellaFlexneri2002017Uid159233': 'GCA_000022245.1',  # ASM2224v1
    'shigellaFlexneri2a2457tUid57991': 'GCA_000183785.2',  # ASM18378v2
    'shigellaFlexneri2a301Uid62907': 'GCA_000006925.2',  # ASM692v2
    'shigellaFlexneri58401Uid58583': 'GCA_000013585.1',  # ASM1358v1
    'shigellaSonneiSs046Uid58217': 'GCA_000092525.1',  # ASM9252v1
    'shigellaSonnei53gUid84383': 'GCA_000188795.2',  # ASM18879v2
    'escherichiaColiUm146Uid162043': 'GCA_000148605.1',  # ASM14860v1
    'escherichiaColiUmn026Uid62981': 'GCA_000026325.1',  # ASM2632v1
    'escherichiaColiUmnk88Uid161991': 'GCA_000212715.2',  # ASM21271v2
    'escherichiaColiUti89Uid58541': 'GCA_000013265.1',  # ASM1326v1
    'escherichiaColiWUid162011': 'GCA_000147755.2',  # ASM14775v1
    'escherichiaColiWUid162101': 'GCA_000147755.2',  # ASM14775v1
    'escherichiaColiXuzhou21Uid163995': 'GCA_000262125.1',  # ASM26212v1
    #
    # http://hgwdev.cse.ucsc.edu/~jcarmstr/crocBrowserRC2/hub.txt
    #
    # American alligator
    'allmis2': 'GCA_000281125.1',  # Couldn't find NCBI entry, mapped to same as allMis1
    # 'anc00': '', # No public assembly
    # ..
    # 'anc21': '',
    # Melopsittacus undulatus (entry already exist)
    # 'melund1': 'GCA_000238935.1', # Melopsittacus_undulatus_6.3
    # Ficedula albicollis
    'ficalb2': 'GCA_000247815.2',  # FicAlb1.5
    # Crocodile
    'cropor2': 'GCA_000768395.1',  # Cpor_2.0
    # Gavialis gangeticus
    'ghagan1': 'GCA_000775435.1',  # ggan_v0.2
    # Chelonia mydas
    'chemyd1': 'GCA_000344595.1',  # CheMyd_1.0
    # Lizard (anoCar2, entry already exist)
    # Anas platyrynchos
    'anapla1': 'GCA_000355885.1',  # BGI_duck_1.0
    # Medium ground finch (geoFor1, entry already exist)
    # Ostrich
    'strcam0': 'GCA_000698965.1',  # ASM69896v1
    # Painted turtle (chrPic1, entry already exist)
    # Amazona vittata
    'amavit1': 'GCA_000332375.1',  # AV1
    # Falco peregrinus
    'falper1': 'GCA_000337955.1',  # F_peregrinus_v1.0
    # Columba livia
    'colliv1': 'GCA_000337935.1',  # Cliv_1.0
    # Falco cherrug
    'falche1': 'GCA_000337975.1',  # F_cherrug_v1.0
    # Ara macao
    'aramac1': 'GCA_000400695.1',  # SMACv1.1
    # Soft cell turtle
    'pelsin1': 'GCA_000230535.1',  # PelSin_1.0
    # Spiny soft cell turtle
    'apaspi1': 'GCA_000385615.1',  # ASM38561v1
    # Tibetan ground jay
    'psehum1': 'GCA_000331425.1',  # PseHum1.0
    # Turkey (melGal1 , entry already present)
    # White throated sparrow
    'zonalb1': 'GCA_000385455.1',  # Zonotrichia_albicollis-1.0.1
    # Taeniopygia guttata
    'taegut2': 'GCA_000151805.2',  # Taeniopygia_guttata-3.2.4 (same as taeGut1)
    #
    # http://devlaeminck.bio.uci.edu/RogersUCSC/hub.txt
    #
    # Drosophila simulans w501
    'dsim-w501': 'GCA_000754195.2',  # ASM75419v2
}

# Swap the above dictionary
INSDC_TO_UCSC = {v: k for k, v in UCSC_TO_INSDC.items()}
