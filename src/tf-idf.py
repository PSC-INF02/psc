"""@file tf-idf.py
@brief Retrieving data, computing a tf-idf-like indice.
"""
import os
from glob import glob
from abstracter.util.json_stream import *
from re import match
import json
import operator

DEFAULT_RESULTS_DIRECTORY = "../concepts/"
CONCEPTS_NAMES_DATA_DIRECTORY = "../concepts_names_data/"
DIRECTORY = "../tfidf/"


def build_database(name="", max_files=100, which="names"):
    """
    @param which "names" or "concepts"
    """
    tf_data = dict()
    idf_data = dict()
    if not os.path.isdir(DIRECTORY):
        os.makedirs(DIRECTORY)
    fileconcepts = glob(CONCEPTS_NAMES_DATA_DIRECTORY + "*all_" + which + ".jsons")[0:max_files]
    smallfiles = glob(DEFAULT_RESULTS_DIRECTORY + "/*/*" + which + ".json")[0:10000]
    # building tf database
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
    for thefile in smallfiles:
        with open(thefile, 'r') as file:
            temp = json.load(file)
        if temp:
            for c in temp:
                if c in tf_data:
                    if c in idf_data:
                        idf_data[c] += 1
                    else:
                        idf_data[c] = 1
    writer = JSONStreamWriter(DIRECTORY + name + "idf_data.jsons")
    for d in idf_data.items():
        writer.write(d)
    writer.close()
    print(len(tf_data))
    print(len(idf_data))
    tfidf_data = dict()
    for c in tf_data:
        if c in idf_data:
            tfidf_data[c] = min(tf_data[c] / idf_data[c], 10)
            #tfidf_data[c] = tf_data[c] / idf_data[c]
            # 4 = not too much
    sorted_data = sorted(tfidf_data.items(), key=operator.itemgetter(1))
    sorted_data.reverse()
    writer = JSONStreamWriter(DIRECTORY + name + "tfidf_data.jsons")
    for d in sorted_data:
        writer.write(d)
    writer.close()


from abstracter.concepts_network import *


def clean_database(name="tfidf_data.jsons"):
    """
    Keep only what's relevant, ie the names and concepts that appear in the network.
    """
    cn = ConceptNetwork()
    cn.load("rc3")
    tfidf_data = dict()
    for entry in read_json_stream(DIRECTORY + name):
        if cn.has_node(entry[0]):
            tfidf_data[entry[0]] = entry[1]
    sorted_data = sorted(tfidf_data.items(), key=operator.itemgetter(1))
    sorted_data.reverse()
    writer = JSONStreamWriter(DIRECTORY + "cleared_" + name)
    for d in sorted_data:
        writer.write(d)
    writer.close()

#build_database(name="concepts_", which="concepts")
#clean_database("concepts_tfidf_data.jsons")
#build_database(name="names_", which="names")
#clean_database("names_tfidf_data.jsons")

from abstracter.parsers import retriever as ret


def summarize(filename):
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
                score = sum([ntfidf[i] if i in ntfidf else 0 for i in nlist] + [ctfidf[i] if i in ctfidf else 0 for i in clist]) / (len(nlist) + len(clist))
                phrases[line] = score
        # sort by score
        sorted_phrases = sorted(phrases.items(), key=operator.itemgetter(1))
        sorted_phrases.reverse()
    with open(filename + "_sorted", 'w') as file:
        for p in sorted_phrases:
            file.write(p.__repr__() + "\n")

#summarize("../parsed_for_systran/0_1")

import os.path

def summarize_all():
    ntfidf = dict()
    ctfidf = dict()
    # load data
    for entry in read_json_stream(DIRECTORY + "cleared_concepts_tfidf_data.jsons"):
        ctfidf[entry[0]] = entry[1]
    for entry in read_json_stream(DIRECTORY + "cleared_names_tfidf_data.jsons"):
        ntfidf[entry[0]] = entry[1]

    for i in range(7):
        for j in range(30):
            filename = "../parsed_for_systran/%i_%i" % (i, j)
            if os.path.exists(filename):
                phrases = dict()
                with open(filename, 'r') as file:
                    for line in file:
                        doublelist = ret.retrieve_words_names(line)
                        nlist = doublelist[1]
                        clist = doublelist[0]
                        if nlist or clist:
                            score = sum([ntfidf[i] if i in ntfidf else 0 for i in nlist] + [ctfidf[i] if i in ctfidf else 0 for i in clist]) / (len(nlist) + len(clist))
                            phrases[line] = score
                    # sort by score
                    sorted_phrases = sorted(phrases.items(), key=operator.itemgetter(1))
                    sorted_phrases.reverse()
                with open(filename + "_sorted", 'w') as file:
                    for p in sorted_phrases:
                        file.write(p.__repr__() + "\n")



summarize_all()