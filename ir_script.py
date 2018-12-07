import os
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import (pairwise_tukeyhsd, MultiComparison)
import matplotlib as mpl
mpl.use('tkagg')
import matplotlib.pyplot as plt


class Measure:
    # initialization of measure
    def __init__(self, topic, ap, rprec, p_10):
        self.topic = topic
        self.ap = ap
        self.rprec = rprec
        self.p_10 = p_10


class Structure:
    # initialization of structure
    def __init__(self, filename, ntopic):
        self.ntopic = ntopic
        self.filename = filename
        self.measure = []


def setup_terrier():
    # setup terrier-core-4.4
    os.system(path+"terrier-core-4.4/bin/trec_setup.sh "+path+"TIPSTER1/")
    os.system("echo ignore.low.idf.terms=true >> "+path+"terrier-core-4.4/etc/terrier.properties")
    os.system("echo trec.topics="+path+"topics.351-400_trec7.txt >> "+path+"terrier-core-4.4/etc/terrier.properties")
    os.system("echo trec.qrels="+path+"qrelstrec7.txt >> "+path+"terrier-core-4.4/etc/terrier.properties")


def copy_all(model, stopword, stemmer, rm):
    # copy all index files and run
    if stopword == 0 and stemmer == 1:
        if model == "BM25":
            os.system("mkdir "+path+"indexes/BM25nostopword")
            os.system("cp "+path+"terrier-core-4.4/var/index/* "+path+"indexes/BM25nostopword/")
            os.system("cp "+path+"terrier-core-4.4/var/results/BM25b0.75_2.res "+path+"indexes/run/BM25_stem.res")
    if stopword == 1 and stemmer == 1:
        if model == "TF_IDF":
            os.system("mkdir "+path+"indexes/TF_IDFall")
            os.system("cp "+path+"terrier-core-4.4/var/index/* "+path+"indexes/TF_IDFall/")
            os.system("cp "+path+"terrier-core-4.4/var/results/TF_IDF_0.res "+path+"indexes/run/TF_IDF.res")
        if model == "BM25":
            os.system("mkdir "+path+"indexes/BM25all")
            os.system("cp "+path+"terrier-core-4.4/var/index/* "+path+"indexes/BM25all/")
            os.system("cp "+path+"terrier-core-4.4/var/results/BM25b0.75_1.res "+path+"indexes/run/BM25.res")
    if stopword == 0 and stemmer == 0:
        if model == "TF_IDF":
            os.system("mkdir "+path+"indexes/TF_IDFnothing")
            os.system("cp "+path+"terrier-core-4.4/var/index/* "+path+"indexes/TF_IDFnothing/")
            os.system("cp "+path+"terrier-core-4.4/var/results/TF_IDF_3.res "+path+"indexes/run/TF_IDF_not.res")
    if rm == 1:
        os.system("rm "+path+"terrier-core-4.4/var/index/*")


def terrier():
    setup_terrier()
    # setup terrier.properties
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -i")
    # rum TF_IDF stoplist, Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=TF_IDF")
    # run BM25 stoplist, Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=BM25")
    copy_all("TF_IDF", 1, 1, 0)
    copy_all("BM25", 1, 1, 1)

    setup_terrier()
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -i -Dtermpipelines=PorterStemmer")
    # run BM25 Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=BM25")
    copy_all("BM25", 0, 1, 1)

    setup_terrier()
    f = open(path+"terrier-core-4.4/etc/terrier.properties", "r").read().split("\n")
    fout = open(path+"terrier-core-4.4/etc/terrier.properties", "w")
    for i in range(len(f)):
        if f[i] != "termpipelines=Stopwords,PorterStemmer" or f[i] != "stopwords.filename=stopword-list.txt":
            fout.write(f[i]+"\n")
    fout.close()
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -i")
    # run TF_IDF no stopword no Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=TF_IDF")
    copy_all("TF_IDF", 0, 0, 1)


def trec_eval():
    # compute evaluation
    files = os.listdir(path+"indexes/")
    if "run" not in files:
        os.system("mkdir " + path + "indexes/run")
    files = os.listdir(path+"indexes/run/")
    if "eval" not in files:
        os.system("mkdir " + path + "indexes/run/eval")
    os.system(path+"trec_eval-master/trec_eval -q -m all_trec "+path+"qrelstrec7.txt "+path+"indexes/run/TF_IDF.res > "+path+"indexes/run/eval/evalTF_IDF.txt")
    os.system(path+"trec_eval-master/trec_eval -q -m all_trec "+path+"qrelstrec7.txt "+path+"indexes/run/BM25.res > "+path+"indexes/run/eval/evalBM25.txt")
    os.system(path+"trec_eval-master/trec_eval -q -m all_trec "+path+"qrelstrec7.txt "+path+"indexes/run/BM25_stem.res > "+path+"indexes/run/eval/evalBM25_stem.txt")
    os.system(path+"trec_eval-master/trec_eval -q -m all_trec "+path+"qrelstrec7.txt "+path+"indexes/run//TF_IDF_not.res > "+path+"indexes/run/eval/evalTF_IDF_not.txt")


def create_file(path):
    # save the positions of evaluation files
    file = []
    file.append(path+"indexes/run/eval/evalTF_IDF.txt")
    file.append(path+"indexes/run/eval/evalBM25.txt")
    file.append(path+"indexes/run/eval/evalBM25_stem.txt")
    file.append(path+"indexes/run/eval/evalTF_IDF_not.txt")
    return file


def data(file):
    # initializzation of structure with all measures
    structure = []
    for j in range(len(file)):
        structure.append(Structure(file[j], 50))
        f = open(file[j], "r").read().split("\n")
        k = 0
        for i in range(len(f)):
            line = f[i].split()
            if len(line) > 1:
                if line[0] == "map":
                    ap = line[2]
                    k = k+1
                elif line[0] == "Rprec":
                    rprec = line[2]
                    k = k+1
                elif line[0] == "P_10":
                    p_10 = line[2]
                    topic = line[1]
                    k = k+1
                if k == 3:
                    # setup the structure
                    structure[j].measure.append(Measure(topic, ap, rprec, p_10))
                    k = 0
    return structure


def create_ap_file(path, structure):
    # create a matrix file with ap
    f = open(path+"indexes/ap.txt", "w")
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].ap)
            if j != len(structure)-1:
                f.write(" ")
            else:
                f.write("\n")
    f.close()


def create_rprec_file(path, structure):
    # create a matrix file with rprec
    f = open(path+"indexes/rprec.txt", "w")
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].rprec)
            if j != len(structure)-1:
                f.write(" ")
            else:
                f.write("\n")
    f.close()


def create_p_10_file(path, structure):
    # create a matrix file with p_10
    f = open(path+"indexes/p_10.txt", "w")
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].p_10)
            if j != len(structure)-1:
                f.write(" ")
            else:
                f.write("\n")
    f.close()


def make_datagroup(structure):
    data = np.zeros(200)
    group = []
    for j in range(len(structure)):
        for i in range(structure[0].ntopic):
            data[j*structure[0].ntopic+i] = float(structure[j].measure[i].ap)
            if j == 0:
                group.append("TF_IDF")
            elif j == 1:
                group.append("BM25")
            elif j == 2:
                group.append("BM25_stem")
            else:
                group.append("TD_IDF_not")
    return data, group


def ap_anova(structure):
    ap = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            data.append(structure[j].measure[i].ap)
        ap.append(data)
    return ap


def anova(structure):
    ap = ap_anova(structure)
    f, p = stats.f_oneway(ap[0], ap[1], ap[2], ap[3])
    return f, p


def print_anova(f, p):
    print('One-way ANOVA')
    print('=============')
    print('F value:', f)
    print('P value:', p, '\n')


def tukey(structure, alpha):
    data, group = make_datagroup(structure)
    tukey = pairwise_tukeyhsd(data, group, alpha)
    tukey.plot_simultaneous()    # Plot group confidence intervals
    plt.show()
    print(tukey.summary())


def tukey1(structure, alpha):
    data, group = make_datagroup(structure)
    mc = MultiComparison(data, group)
    result = mc.tukeyhsd(alpha)
    result.plot_simultaneous()
    plt.show()
    print(result)


def list_rprec(structure):
    rprec = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            data.append(float(structure[j].measure[i].rprec))
        rprec.append(data)
    return rprec


def list_topic(structure):
    topic = []
    for i in range(structure[0].ntopic):
        topic.append(structure[0].measure[i].topic)
    return topic


# create indexes folder
path = "/home/martinidav/Desktop/Homework_1_IR/resources/"
files = os.listdir(path)
if "indexes" not in files:
    os.system("mkdir " + path + "indexes")




'''
terrier()
'''
trec_eval()
file = create_file(path)
structure = data(file)
create_ap_file(path, structure)
create_rprec_file(path, structure)
create_p_10_file(path, structure)
'''
f, p = anova(structure)
print_anova(f, p)
tukey(structure, 0.05)
'''



topic = list_topic(structure)
rprec = list_rprec(structure)

for i in range(len(rprec)):
    plt.bar(topic, rprec[i])
    plt.show()


