"""@file tf-idf.py
@brief Retrieving data, computing a tf-idf-like indice.
"""
import os
from glob import glob
from abstracter.util.json_stream import read_json_stream, JSONStreamWriter
from re import match
import json
import operator
from math import log
import os.path
from abstracter.concepts_network import *
from abstracter.parsers import retriever as ret


############################
# Directories of crawler results (we also may get them from
# a separate settings file)
##############################

DEFAULT_RESULTS_DIRECTORY = "../concepts/"
CONCEPTS_NAMES_DATA_DIRECTORY = "../concepts_names_data/"

############################
# Directory where we store tf-idf databases.
#############################

DIRECTORY = "../tfidf/"

########################
# Default concepts network to load.
########################

NETWORK = "rc3"


def build_database(name="", max_files=100, which="names"):
    """
    TF data is an overall term frequency (may differ from
    the tf-idf applied to only one text).

    Thus, the tf-idf database is static and context-free.
    It should be used differently for summarizing.
    (Use only the idf database and multiply with the tf in the document).

    @param which "names" or "concepts"
    """
    tf_data = dict()
    idf_data = dict()
    if not os.path.isdir(DIRECTORY):
        os.makedirs(DIRECTORY)
    fileconcepts = glob(CONCEPTS_NAMES_DATA_DIRECTORY + "*all_" + which + ".jsons")[0:max_files]
    smallfiles = glob(DEFAULT_RESULTS_DIRECTORY + "/*/*" + which + ".json")[0:30000]
    # building tf database
    print("Builiding tf database...")
    for filename in fileconcepts:
        # print(filename)
        for c in read_json_stream(filename):
            # avoid bad words
            if match('^[a-zA-Z\s-]*$', c[0]) and len(c[0]) < 20:
                if c[0] not in tf_data:
                    tf_data[c[0]] = c[1]
                else:
                    tf_data[c[0]] += c[1]
        # print("successful reading of :"+filename)
    writer = JSONStreamWriter(DIRECTORY + name + "tf_data.jsons")
    for d in tf_data.items():
        writer.write(d)
    writer.close()
    # building idf database
    print("Builiding idf database...")
    for thefile in smallfiles:
        with open(thefile, 'r') as file:
            try:
                temp = json.load(file)
            except ValueError:
                temp = []
        if temp:
            for c in temp:
                if c in tf_data:
                    if c in idf_data:
                        idf_data[c] += 1
                    else:
                        idf_data[c] = 1
    nbdocs = len(list(smallfiles))
    for c in idf_data:
        idf_data[c] = log(nbdocs / idf_data[c])
    writer = JSONStreamWriter(DIRECTORY + name + "idf_data.jsons")
    for d in idf_data.items():
        writer.write(d)
    writer.close()
    print(len(tf_data))
    print(len(idf_data))
    tfidf_data = dict()
    print("Builiding tf-idf database...")
    for c in tf_data:
        if c in idf_data:
            # other possibility
            # tfidf_data[c] = min(tf_data[c] * idf_data[c], 10)
            tfidf_data[c] = tf_data[c] * idf_data[c]
            # 4 = not too much
    sorted_data = sorted(tfidf_data.items(), key=operator.itemgetter(1))
    sorted_data.reverse()
    writer = JSONStreamWriter(DIRECTORY + name + "tfidf_data.jsons")
    for d in sorted_data:
        writer.write(d)
    writer.close()


def clean_database(name="tfidf_data.jsons"):
    """
    @brief Keep names and concepts that appear in the network.

    We have to load a ConceptNetwork : NETWORK.

    @param name The name of the file's database.
    it has to be a json stream, and it has
    to be stored in the directory DIRECTORY.
    """
    cn = ConceptNetwork()
    cn.load(NETWORK)
    tfidf_data = dict()
    print("Cleaning " + name)
    for entry in read_json_stream(DIRECTORY + name):
        if cn.has_node(entry[0].lower().replace(' ', '_')):
            tfidf_data[entry[0]] = entry[1]
    sorted_data = sorted(tfidf_data.items(), key=operator.itemgetter(1))
    sorted_data.reverse()
    writer = JSONStreamWriter(DIRECTORY + "cleared_" + name)
    for d in sorted_data:
        writer.write(d)
    writer.close()
    print("Done.")


def build_databases_example():
    build_database(name="concepts_", which="concepts")
    clean_database("concepts_tfidf_data.jsons")
    clean_database("concepts_tf_data.jsons")
    clean_database("concepts_idf_data.jsons")
    build_database(name="names_", which="names")
    clean_database("names_tfidf_data.jsons")
    clean_database("names_tf_data.jsons")
    clean_database("names_idf_data.jsons")


def sort_sents(filename):
    """
    @brief Sort sentences of a text by decreasing TF-IDF mean.

    Two TF-IDF databases are loaded, "cleared_concepts_tfidf_data.jsons"
    and "cleared_names_tfidf_data.jsons". They have to be stored in
    the directory DIRECTORY.
    A new file named filename_sorted is written.

    @param filename A file.
    """
    ntfidf = dict()
    ctfidf = dict()
    # load data
    for entry in read_json_stream(DIRECTORY + "cleared_concepts_tfidf_data.jsons"):
        ctfidf[entry[0]] = entry[1]
    for entry in read_json_stream(DIRECTORY + "cleared_names_tfidf_data.jsons"):
        ntfidf[entry[0]] = entry[1]

    phrases = dict()
    with open(filename, 'r') as file:
        for line in file:
            doublelist = ret.retrieve_words_names(line)
            nlist = doublelist[1]
            clist = doublelist[0]
            if nlist or clist:
                score = sum([ntfidf[i] if i in ntfidf else 0 for i in nlist] +
                            [ctfidf[i] if i in ctfidf else 0 for i in clist]) / (len(nlist) + len(clist))
                phrases[line] = score

        # sort by score
        sorted_phrases = sorted(phrases.items(), key=operator.itemgetter(1))
        sorted_phrases.reverse()
    with open(filename + "_sorted", 'w') as file:
        for p in sorted_phrases:
            file.write(p.__repr__() + "\n")


def sort_sentences(dir="../parsed_for_systran/"):
    """
    @brief Sort sentences by decreasing TF-IDF mean.

    We use this function on a directory where files are named i_j
    (for example, the result of a pre-parsing of the crawler's files).
    Two TF-IDF databases are loaded, "cleared_concepts_tfidf_data.jsons"
    and "cleared_names_tfidf_data.jsons". They have to be stored in
    the directory DIRECTORY.
    New files named filename_sorted are created.

    @param dir Data directory.
    """
    ntfidf = dict()
    ctfidf = dict()
    # load data
    for entry in read_json_stream(DIRECTORY + "cleared_concepts_tfidf_data.jsons"):
        ctfidf[entry[0]] = entry[1]
    for entry in read_json_stream(DIRECTORY + "cleared_names_tfidf_data.jsons"):
        ntfidf[entry[0]] = entry[1]

    for i in range(7):
        for j in range(30):
            filename = dir + "%i_%i" % (i, j)
            if os.path.exists(filename):
                phrases = dict()
                with open(filename, 'r') as file:
                    for line in file:
                        doublelist = ret.retrieve_words_names(line)
                        nlist = doublelist[1]
                        clist = doublelist[0]
                        if nlist or clist:
                            score = sum([ntfidf[i] if i in ntfidf else 0 for i in nlist] +
                                        [ctfidf[i] if i in ctfidf else 0 for i in clist]) / (len(nlist) + len(clist))
                            phrases[line] = score
                    # sort by score
                    sorted_phrases = sorted(phrases.items(), key=operator.itemgetter(1))
                    sorted_phrases.reverse()
                with open(filename + "_sorted", 'w') as file:
                    file.write("Phrases du texte triées par score.\n\n")
                    for p in sorted_phrases:
                        file.write(p.__repr__() + "\n")


def summarize_all(dir="../parsed_for_systran/", nbphrases=None):
    """
    @brief Summarize.
    We take the first sentence of the
    text and its most scored sentences by TF-IDF, which
    are put in their order of occuring in the text.

    We use this function on a directory where files are named i_j
    (for example, the result of a pre-parsing of the crawler's files).
    Two TF-IDF databases are loaded, "cleared_concepts_tfidf_data.jsons"
    and "cleared_names_tfidf_data.jsons". They have to be stored in
    the directory DIRECTORY.
    New files named "filename_summary2" are created.

    @param dir The directory containing the files.
    @param nbphrases The number of sentences of the summary.
    Default is None, which means we take one quarter of
    the total number of sentences of the text (it adapts
    to the text's length).
    """
    ntfidf = dict()
    ctfidf = dict()
    # load data
    print("Loading...")
    for entry in read_json_stream(DIRECTORY + "cleared_concepts_tfidf_data.jsons"):
        ctfidf[entry[0]] = entry[1]
    for entry in read_json_stream(DIRECTORY + "cleared_names_tfidf_data.jsons"):
        ntfidf[entry[0]] = entry[1]
    print("Done loading.")

    for i in range(8):
        for j in range(30):
            filename = dir + "%i_%i" % (i, j)
            if os.path.exists(filename):
                phrases = dict()
                sents = dict()
                k = 0
                with open(filename, 'r') as file:
                    for line in file:
                        sents[k] = line
                        doublelist = ret.retrieve_words_names(line)
                        nlist = doublelist[1]
                        clist = doublelist[0]
                        if k == 0:
                            phrases[k] = 100000
                        elif len(nlist) + len(clist) > 2:
                            score = sum([ntfidf[i] if i in ntfidf else 0 for i in nlist] + [ctfidf[i] if i in ctfidf else 0 for i in clist]) / (len(nlist) + len(clist))
                            #score = sum([ntfidf[i] if i in ntfidf else 0 for i in nlist] + [ctfidf[i] if i in ctfidf else 0 for i in clist])
                            phrases[k] = score
                        elif nlist or clist:
                            phrases[k] = 0
                        else:
                            phrases[k] = 0
                        k += 1
                    # sort by score
                tot = int(nbphrases if nbphrases else (k / 4))
                sorted_phrases = sorted(phrases.items(), key=operator.itemgetter(1))
                sorted_phrases.reverse()
                if sorted_phrases:
                    temp = sorted_phrases[0:(tot + 1)]
                    temp2 = sorted(temp, key=operator.itemgetter(0))
                    temp3 = [(sents[p[0]], p[1]) for p in temp2]
                with open(filename + "_summary2", 'w') as file:
                    file.write("Summary : First sentence of the text + " + tot.__str__() + " most scored sentences, in the right order.\n\n")
                    # file.write((sents[0], None).__repr__() + "\n")
                    for p in temp3:
                        file.write(p[0] + "\n")


def modify_rc_ics(newname):
    """
    Load default TF-IDF databases and modify ics in the network
    according to them.
    """
    cn = ConceptNetwork()
    cn.load(NETWORK)
    ntfidf = dict()
    ctfidf = dict()
    # load data
    for entry in read_json_stream(DIRECTORY + "cleared_concepts_tfidf_data.jsons"):
        ctfidf[entry[0]] = entry[1]
    for entry in read_json_stream(DIRECTORY + "cleared_names_tfidf_data.jsons"):
        ntfidf[entry[0]] = entry[1]

    for c in ctfidf:
        if cn.has_node(c):
            cn[c]["ic"] = 


