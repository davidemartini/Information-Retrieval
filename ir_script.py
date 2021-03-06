import os
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import (pairwise_tukeyhsd, MultiComparison)
from timeit import default_timer as timer
import matplotlib as mpl
mpl.use('tkagg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText


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
    os.system(path+"terrier-core-4.4/bin/trec_setup.sh "+path+"TIPSTER/")
    os.system("echo ignore.low.idf.terms=true >> "+path+"terrier-core-4.4/etc/terrier.properties")
    os.system("echo trec.topics="+path+"topics.351-400_trec7.txt >> "+path+"terrier-core-4.4/etc/terrier.properties")
    os.system("echo trec.qrels="+path+"qrelstrec7.txt >> "+path+"terrier-core-4.4/etc/terrier.properties")
    f = open(path+"terrier-core-4.4/etc/terrier.properties", "r").read().split("\n")
    fout = open(path+"terrier-core-4.4/etc/terrier.properties", "w")
    for i in range(len(f)):
        if f[i] == "TrecQueryTags.process=TOP,NUM,TITLE":
            fout.write("TrecQueryTags.process=TITLE,DESC\n")
        elif f[i] == "TrecQueryTags.skip=DESC,NARR":
            fout.write("TrecQueryTags.skip=NARR\n")
        else:
            fout.write(f[i]+"\n")
    fout.close()


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


def terrier(time):
    setup_terrier()
    # setup terrier.properties
    start = timer()
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -i")
    end = timer()
    time.append(end-start)
    time.append(end-start)
    # save in file the stats of indexing
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh --printstats > "+path+"indexes/TF_IDF_stats.txt")
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh --printstats > "+path+"indexes/BM25_stats.txt")
    # rum TF_IDF stoplist, Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=TF_IDF")
    # run BM25 stoplist, Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=BM25")
    copy_all("TF_IDF", 1, 1, 0)
    copy_all("BM25", 1, 1, 1)

    setup_terrier()
    f = open(path+"terrier-core-4.4/etc/terrier.properties", "r").read().split("\n")
    fout = open(path+"terrier-core-4.4/etc/terrier.properties", "w")
    for i in range(len(f)):
        if f[i]=="termpipelines=Stopwords,PorterStemmer":
            fout.write("termpipelines=PorterStemmer\n")
        else:
            fout.write(f[i]+"\n")
    fout.close()
    start = timer()
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -i ")
    end = timer()
    time.append(end-start)
    # save in file the stats of indexing
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh --printstats > "+path+"indexes/BM25_stem_stats.txt")
    # run BM25 Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=BM25")
    copy_all("BM25", 0, 1, 1)

    setup_terrier()
    f = open(path+"terrier-core-4.4/etc/terrier.properties", "r").read().split("\n")
    fout = open(path+"terrier-core-4.4/etc/terrier.properties", "w")
    for i in range(len(f)):
        if f[i] == "termpipelines=Stopwords,PorterStemmer":
            fout.write("termpipelines=\n")
        else:
            fout.write(f[i]+"\n")
    fout.close()
    start = timer()
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -i")
    end = timer()
    time.append(end-start)
    # save in file the stats of indexing
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh --printstats > "+path+"indexes/TF_IDF_not_stats.txt")
    # run TF_IDF no stopword no Porter stemmer
    os.system(path+"terrier-core-4.4/bin/trec_terrier.sh -r -Dtrec.model=TF_IDF")
    copy_all("TF_IDF", 0, 0, 1)


def create_time_file(path, time):
    # create a matrix file with p_10
    f = open(path+"indexes/execution_time.txt", "w")
    f.write('TF_IDF\tBM25\tBM25_stem\tTF_IDF_not\n')
    f.write(str(time[0])+'\t'+str(time[1])+'\t'+str(time[2])+'\t'+str(time[3])+'\n')
    f.close()


def read_time(path):
    return np.loadtxt(path+"indexes/execution_time.txt", skiprows=1, delimiter='\t')


def plot_time(path, time, run):
    files = os.listdir(path+"indexes/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "indexes/run/plot")
    title = "Time of execution of indicizations"
    fileplot = path+"indexes/run/plot/time_exec.svg"
    plt.figure(figsize=(30, 20))
    plt.rcParams.update({'font.size': 22})
    plt.bar(run, time, 0.25)
    plt.xlabel('Model')
    plt.ylabel('Time (sec)')
    plt.suptitle(title, fontsize=40)
    ax = plt.gca()
    text = "TF_IDF = TF_IDF with Stopword and Porter Stemmer\n"
    text = text+ "BM25 = BM25 with Stopword and Porter Stemmer\n"
    text = text+ "BM25_stem = BM25 without Stopword with Porter Stemmer\n"
    text = text + "TF_IDF_not = TF_IDF without Stopword and Porter Stemmer"
    at = AnchoredText(text, loc='lower left', prop=dict(size=18), frameon=True)
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.savefig(fileplot, dpi=300)
    plt.clf()


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
    os.system(path+"trec_eval-master/trec_eval -q -m all_trec "+path+"qrelstrec7.txt "+path+"indexes/run/TF_IDF_not.res > "+path+"indexes/run/eval/evalTF_IDF_not.txt")


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
    f.write('TF_IDF\tBM25\tBM25_stem\tTF_IDF_not\n')
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].ap)
            if j != len(structure)-1:
                f.write('\t')
            else:
                f.write('\n')
    f.close()


def create_rprec_file(path, structure):
    # create a matrix file with rprec
    f = open(path+"indexes/rprec.txt", "w")
    f.write('TF_IDF\tBM25\tBM25_stem\tTF_IDF_not\n')
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].rprec)
            if j != len(structure)-1:
                f.write('\t')
            else:
                f.write('\n')
    f.close()


def create_p_10_file(path, structure):
    # create a matrix file with p_10
    f = open(path+"indexes/p_10.txt", "w")
    f.write('TF_IDF\tBM25\tBM25_stem\tTF_IDF_not\n')
    for i in range(structure[0].ntopic):
        for j in range(len(structure)):
            f.write(structure[j].measure[i].p_10)
            if j != len(structure)-1:
                f.write('\t')
            else:
                f.write('\n')
    f.close()


def make_datagroup(structure, measure):
    data = np.zeros(structure[0].ntopic*len(structure))
    group = []
    for j in range(len(structure)):
        for i in range(structure[0].ntopic):
            if measure == 'ap':
                data[j*structure[0].ntopic+i] = float(structure[j].measure[i].ap)
            elif measure == 'p_10':
                data[j*structure[0].ntopic+i] = float(structure[j].measure[i].p_10)
            else:
                data[j*structure[0].ntopic+i] = float(structure[j].measure[i].rprec)
            if j == 0:
                group.append("TF_IDF")
            elif j == 1:
                group.append("BM25")
            elif j == 2:
                group.append("BM25_stem")
            elif j == 3:
                group.append("TF_IDF_not")
    return data, group


def m_anova(structure, measure):
    m = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            if measure == 'ap':
                data.append(structure[j].measure[i].ap)
            elif measure == 'p_10':
                data.append(structure[j].measure[i].p_10)
            else:
                data.append(structure[j].measure[i].rprec)
        m.append(data)
    return m


def anova(structure, measure):
    m = m_anova(structure, measure)
    f, p = stats.f_oneway(m[0], m[1], m[2], m[3])
    return f, p


def print_anova(f, p, measure):
    if measure == 'ap':
        fw = open(path+"indexes/run/plot/anovaAP.txt", "w")
    elif measure == 'p_10':
        fw = open(path+"indexes/run/plot/anovaP_10.txt", "w")
    else:
        fw = open(path+"indexes/run/plot/anovaRprec.txt", "w")
    anova = ['One-way ANOVA', '=============', 'F value: '+str(f), 'P value: '+str(p)]
    for i in range(len(anova)):
        print(anova[i])
        fw.write(anova[i]+'\n')
    fw.close()


def tukey(structure, alpha, measure):
    if measure == 'ap':
        data, group = make_datagroup(structure, measure)
        tukey = pairwise_tukeyhsd(data, group, alpha)
        fig = tukey.plot_simultaneous()    # Plot group confidence intervals
        fig.set_figwidth(30)
        fig.set_figheight(20)
        axes = fig.gca()
        fig.suptitle('TukeyHSD test', fontsize=40)
        axes.set_xlabel("Average Precision (AP)", fontsize=30)
        axes.tick_params(labelsize=30)
        fileplot = path+"indexes/run/plot/TukeyHSDtestAP.svg"
        text = "TF_IDF = TF_IDF with stop list and Porter Stemmer\n"
        text = text + "BM25 = BM25 with stop list and Porter Stemmer\n"
        text = text + "BM25_stem = BM25 without stop list with Porter Stemmer\n"
        text = text + "TF_IDF_not = TF_IDF without stop list and Porter Stemmer"
        at = AnchoredText(text, loc='lower left', prop=dict(size=18), frameon=True)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        axes.add_artist(at)
        fig.savefig(fileplot, dpi=300)
        fw = open(path+"indexes/run/plot/tukeyHSDAP.txt", "w")
        fw.write(str(tukey.summary()))
        print(tukey.summary())
        fw.close()
    elif measure == 'p_10':
        data, group = make_datagroup(structure, measure)
        tukey = pairwise_tukeyhsd(data, group, alpha)
        fig = tukey.plot_simultaneous()    # Plot group confidence intervals
        fig.set_figwidth(30)
        fig.set_figheight(20)
        axes = fig.gca()
        fig.suptitle('TukeyHSD test', fontsize=40)
        axes.set_xlabel("P(10)", fontsize=30)
        axes.tick_params(labelsize=30)
        fileplot = path+"indexes/run/plot/TukeyHSDtestP_10.svg"
        text = "TF_IDF = TF_IDF with stop list and Porter Stemmer\n"
        text = text + "BM25 = BM25 with stop list and Porter Stemmer\n"
        text = text + "BM25_stem = BM25 without stop list with Porter Stemmer\n"
        text = text + "TF_IDF_not = TF_IDF without stop list and Porter Stemmer"
        at = AnchoredText(text, loc='lower left', prop=dict(size=18), frameon=True)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        axes.add_artist(at)
        fig.savefig(fileplot, dpi=300)
        fw = open(path+"indexes/run/plot/tukeyHSDP_10.txt", "w")
        fw.write(str(tukey.summary()))
        print(tukey.summary())
        fw.close()
    else:
        data, group = make_datagroup(structure, measure)
        tukey = pairwise_tukeyhsd(data, group, alpha)
        fig = tukey.plot_simultaneous()    # Plot group confidence intervals
        fig.set_figwidth(30)
        fig.set_figheight(20)
        axes = fig.gca()
        fig.suptitle('TukeyHSD test', fontsize=40)
        axes.set_xlabel("Rprec", fontsize=30)
        axes.tick_params(labelsize=30)
        fileplot = path+"indexes/run/plot/TukeyHSDtestRprec.svg"
        text = "TF_IDF = TF_IDF with stop list and Porter Stemmer\n"
        text = text + "BM25 = BM25 with stop list and Porter Stemmer\n"
        text = text + "BM25_stem = BM25 without stop list with Porter Stemmer\n"
        text = text + "TF_IDF_not = TF_IDF without stop list and Porter Stemmer"
        at = AnchoredText(text, loc='lower left', prop=dict(size=18), frameon=True)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        axes.add_artist(at)
        fig.savefig(fileplot, dpi=300)
        fw = open(path+"indexes/run/plot/tukeyHSDRprec.txt", "w")
        fw.write(str(tukey.summary()))
        print(tukey.summary())
        fw.close()

def list_rprec(structure):
    rprec = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            data.append(float(structure[j].measure[i].rprec))
        rprec.append(data)
    return rprec


def list_p_10(structure):
    p_10 = []
    for j in range(len(structure)):
        data = []
        for i in range(structure[0].ntopic):
            data.append(float(structure[j].measure[i].p_10))
        p_10.append(data)
    return p_10


def list_topic(structure):
    topic = []
    for i in range(structure[0].ntopic):
        topic.append(structure[0].measure[i].topic)
    return topic


def plot_rprec(topic, rprec):
    files = os.listdir(path+"indexes/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "indexes/run/plot")
    for i in range(len(rprec)):
        if i == 0:
            title = "TF_IDF with stop list and Porter Stemmer"
            fileplot = path+"indexes/run/plot/RprecTF_IDF.svg"
        elif i == 1:
            title = "BM25 with stop list and Porter Stemmer"
            fileplot = path+"indexes/run/plot/RprecBM25.svg"
        elif i == 2:
            title = "BM25 without stop list with Porter Stemmer"
            fileplot = path+"indexes/run/plot/RprecBM25_stem.svg"
        elif i == 3:
            title = "TF_IDF without stop list and Porter Stemmer"
            fileplot = path+"indexes/run/plot/RprecTF_IDF_not.svg"
        plt.figure(figsize=(30, 20))
        plt.rcParams.update({'font.size': 22})
        plt.bar(topic, rprec[i])
        plt.xticks(rotation=90)
        plt.xlabel('Topics')
        plt.ylabel('Rprec')
        plt.suptitle(title, fontsize=40)
        plt.savefig(fileplot, dpi=300)
        plt.clf()


def plot_p_10(topic, p_10):
    files = os.listdir(path+"indexes/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "indexes/run/plot")
    for i in range(len(rprec)):
        if i == 0:
            title = "TF_IDF with stop list and Porter Stemmer"
            fileplot = path+"indexes/run/plot/P_10TF_IDF.svg"
        elif i == 1:
            title = "BM25 with stop list and Porter Stemmer"
            fileplot = path+"indexes/run/plot/P_10BM25.svg"
        elif i == 2:
            title = "BM25 without stop list with Porter Stemmer"
            fileplot = path+"indexes/run/plot/P_10BM25_stem.svg"
        elif i == 3:
            title = "TF_IDF without stop list and Porter Stemmer"
            fileplot = path+"indexes/run/plot/P_10TF_IDF_not.svg"
        plt.figure(figsize=(30, 20))
        plt.rcParams.update({'font.size': 22})
        plt.bar(topic, p_10[i])
        plt.xticks(rotation=90)
        plt.xlabel('Topics')
        plt.ylabel('P(10)')
        plt.suptitle(title, fontsize=40)
        plt.savefig(fileplot, dpi=300)
        plt.clf()


def list_run():
    run = []
    run.append("TF_IDF")
    run.append("BM25")
    run.append("BM25_stem")
    run.append("TF_IDF_not")
    return run


def list_map(structure):
    map = []
    for j in range(len(structure)):
        index = structure[j].ntopic
        map.append(float(structure[j].measure[index].ap))
    return map


def plot_map(run, map):
    files = os.listdir(path+"indexes/run/")
    if "plot" not in files:
        os.system("mkdir " + path + "indexes/run/plot")
    title = "MAP for all runs"
    fileplot = path+"indexes/run/plot/MAPall.svg"
    plt.figure(figsize=(30, 20))
    plt.rcParams.update({'font.size': 22})
    plt.bar(run, map, 0.25)
    plt.xlabel('Runs')
    plt.ylabel('MAP')
    plt.suptitle(title, fontsize=40)
    ax = plt.gca()
    text = "TF_IDF = TF_IDF with stop list and Porter Stemmer\n"
    text = text + "BM25 = BM25 with stop list and Porter Stemmer\n"
    text = text + "BM25_stem = BM25 without stop list with Porter Stemmer\n"
    text = text + "TF_IDF_not = TF_IDF without stop list and Porter Stemmer"
    at = AnchoredText(text, loc='lower left', prop=dict(size=18), frameon=True)
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)
    plt.savefig(fileplot, dpi=300)
    plt.clf()


# create indexes folder
path = "/home/martinidav/Desktop/Homework_1_IR/resources/"
files = os.listdir(path)
if "indexes" not in files:
    os.system("mkdir " + path + "indexes")
    os.system("mkdir " + path + "indexes/run")
    os.system("mkdir " + path + "indexes/run/plot")
time = []
# execute the indexing for each model
#terrier(time)
# collected time of executions is write
#create_time_file(path, time)
# execute the evaluation of runs
#trec_eval()
# read and memorize on file all measures
file = create_file(path)
structure = data(file)
create_ap_file(path, structure)
create_rprec_file(path, structure)
create_p_10_file(path, structure)
# compute ANOVA 1-way test
f, p = anova(structure, 'ap')
print_anova(f, p, 'ap')
f, p = anova(structure, 'p_10')
print_anova(f, p, 'p_10')
f, p = anova(structure, 'rprec')
print_anova(f, p, 'rprec')
# compute Tukey HSD pairwise test and Tukey HSD multiple comparisons
tukey(structure, 0.05, 'ap')
tukey(structure, 0.05, 'p_10')
tukey(structure, 0.05, 'rprec')
# prepare data for plot
topic = list_topic(structure)
rprec = list_rprec(structure)
# plot Rprec for each run on every topic
plot_rprec(topic, rprec)
# plot P(10) for each run on every topic
p_10 = list_p_10(structure)
plot_p_10(topic, p_10)
run = list_run()
map = list_map(structure)
# plot MAP for each run
plot_map(run, map)
# plot execution time for each model
time = read_time(path)
plot_time(path, time, run)
