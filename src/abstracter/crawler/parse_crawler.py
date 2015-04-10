"""@file parse_crawler

Utils for downloading and parsing crawler data.
"""
from abstracter.parsers.retriever import retrieve_words_names
from abstracter.parsers.tokenizer import refactor_crawler
from abstracter.util.json_stream import *
from abstracter.util.http import make_http_request
import json
import os
import tarfile
import shutil
from re import match
from glob import glob
import datetime as dt

DEFAULT_DATA_DIRECTORY = "../crawlerpsc/"
DEFAULT_RESULTS_DIRECTORY = "../concepts/"
CONCEPTS_NAMES_DATA_DIRECTORY = "../concepts_names_data/"
BIG_FILES_DIRECTORY = "../concepts_names_dicts/"
CRAWLER_URL = 'http://nadrieril.fr/dropbox/crawlerpsc/'
# default location of the data directory when it is downloaded and uncompressed
DEFAULT_LOCATION = "srv/ftp/crawlerpsc/"


def download_crawler_data(date):
    """
    Download raw data for a day.

    @param Date : Formatted date AAAA_MM_JJ, such as 2015_01_03 (str).
    """
    full_url = CRAWLER_URL + date + ".tar.gz"
    print("downloading : " + full_url)
    r = make_http_request(full_url)
    if not os.path.isdir(DEFAULT_DATA_DIRECTORY):
        os.makedirs(DEFAULT_DATA_DIRECTORY)
    with open(DEFAULT_DATA_DIRECTORY + date + ".tar.gz", 'wb') as f:
        f.write(r.content)
    # Untar and extract in the same directory.
    tar = tarfile.open(DEFAULT_DATA_DIRECTORY + date + ".tar.gz", "r:gz")
    tar.extractall(DEFAULT_DATA_DIRECTORY)
    tar.close()
    # Move the directory.
    try:
        shutil.move(os.path.join(DEFAULT_DATA_DIRECTORY,
                    DEFAULT_LOCATION + date),
                    DEFAULT_DATA_DIRECTORY)
    except shutil.Error:
        print("Error, maybe the directory " + date + " already exists")
    os.remove(DEFAULT_DATA_DIRECTORY + date + ".tar.gz")
    # works but not useful :
    # shutil.rmtree(os.path.join(DEFAULT_DATA_DIRECTORY,"srv"))
    print("Success with : " + date)


def parse_article(filename):
    """
    Parse an article from the crawler, retrieve words and names.

    @param filename Name of the file to parse.
    @return A tuple of two lists : [words,names].
    """
    with open(filename, 'r') as file:
        text = file.read()
        return retrieve_words_names(text)
    return []


def _parse_directory(max_subdirectories=10,
                     max_files=1000,
                     data_directory=DEFAULT_DATA_DIRECTORY,
                     results_directory=DEFAULT_RESULTS_DIRECTORY,
                     subdirectory="2014_12_04"):
    """
    Parse a directory from the crawler.

    @param max_subdirectories Maximum number of subdirectories to consider.
    @param max_files Maximum number of files to analyze in a subdirectory.
    @param subdirectory The subdirectory to consider 
    (formatted date AAAA_MM_JJ).
    """
    if not os.path.isdir(results_directory + subdirectory + "/"):
        os.makedirs(results_directory + subdirectory + "/")
    i = 0
    j = 0
    while(os.path.exists(data_directory + "%s/%i/%i" % (subdirectory, i, j)) and i < max_subdirectories):
        while(os.path.exists(data_directory + "%s/%i/%i" % (subdirectory, i, j)) and j < max_files):
            temp = parse_article(data_directory + "%s/%i/%i" % (subdirectory, i, j))
            if temp:
                with open(results_directory + "%s/%i_%i_concepts.json" % (subdirectory, i, j), 'w') as file:
                    json.dump(temp[0], file)
                with open(results_directory + "%s/%i_%i_names.json" % (subdirectory, i, j),'w') as file:
                    json.dump(temp[1], file)
                    print("successful with : " + data_directory + "%s/%i/%i" % (subdirectory, i, j))
            j += 1
        j = 0
        i += 1


def unify_day(directory=DEFAULT_RESULTS_DIRECTORY,
              max_files=1000,
              subdirectory="2014_12_04"):
    """
    Unify concepts and names files for a day.

    The result, two dict objects, is written as JSON streams in two separated files.
    The value associated with each name counts the number of occurrences.
    """
    if not os.path.isdir(CONCEPTS_NAMES_DATA_DIRECTORY):
        os.makedirs(CONCEPTS_NAMES_DATA_DIRECTORY)

    for pattern in ["names", "concepts"]:
        i = 0
        j = 0
        dict_pattern = dict()
        k = 0
        while(os.path.exists(directory + "%s/%i_%i_%s.json" % (subdirectory, i, j, pattern)) and k<max_files):
            while(os.path.exists(directory + "%s/%i_%i_%s.json" % (subdirectory, i, j, pattern)) and k<max_files):
                k += 1
                temp = dict()
                with open(directory + "%s/%i_%i_%s.json" % (subdirectory, i, j, pattern), 'r') as file:
                    temp = json.load(file)
                    # print("successful loading of "+directory+"%i/%i" % (i,j))
                if temp:
                    for c in temp:
                        if c in dict_pattern:
                            dict_pattern[c] += temp[c]
                        else:
                            dict_pattern[c] = temp[c]
                j += 1
            j = 0
            i += 1
        pattern_file = CONCEPTS_NAMES_DATA_DIRECTORY + subdirectory + "_all_%s.jsons" % (pattern)
        writer = JSONStreamWriter(pattern_file)
        for d in dict_pattern.items():
            writer.write(d)
        writer.close()


def unify(directory=CONCEPTS_NAMES_DATA_DIRECTORY, max_files=1000,
          names_file="names.jsons", concepts_file="concepts.jsons"):
    """
    Unifies all dicts of concepts and list of names into two single files.
    Retrieves all data from the default directory, with a maximum number
    of max_files files. Suppress bad characters.

    @param names_file Name of the file where names will be written.
    @param concepts_file Name of the file where concepts will be written.
    @param directory Name of the directory where to read and write files.
    """
    filenames = glob(directory + "*names.jsons")[0:max_files]
    fileconcepts = glob(directory + "*concepts.jsons")[0:max_files]
    thedict = {}
    for name in filenames:
        for c in read_json_stream(name):
            # avoid bad words
            if match('^[a-zA-Z\s-]*$', c[0]) and len(c[0]) < 20:
                if c[0] not in thedict:
                    thedict[c[0]] = 1
                else:
                    thedict[c[0]] += c[1]
        # print("successful reading of :"+name)
    writer = JSONStreamWriter(names_file)
    for d in sorted(thedict.items()):
        writer.write(d)
    writer.close()
    thedict = {}
    for name in fileconcepts:
        for c in read_json_stream(name):
            # avoid bad words
            if match('^[a-zA-Z\s-]*$', c[0]) and len(c[0]) < 20:
                if c[0] not in thedict:
                    thedict[c[0]] = 1
                else:
                    thedict[c[0]] += c[1]
        # print("successful reading of :"+name)
    writer = JSONStreamWriter(concepts_file)
    for d in sorted(thedict.items()):
        writer.write(d)
    writer.close()


def download_and_parse_data(date="2015_01_05"):
    """
    Download data for a day, parse it, unify the dicts of names and concepts
    and write them in the default directory.
    """
    download_crawler_data(date)
    _parse_directory(max_subdirectories=10, max_files=1000, subdirectory=date)
    unify_day(subdirectory=date)


def _parse_for_systran_directory(data_directory=DEFAULT_DATA_DIRECTORY,
                                 results_directory="../parsed_for_systran/",
                                 subdirectory="2014_12_04"):
    """
    """
    if not os.path.isdir(results_directory + subdirectory + "/"):
        os.makedirs(results_directory + subdirectory + "/")
    i = 0
    j = 0
    while(os.path.exists(data_directory + "%s/%i/%i" % (subdirectory, i, j))):
        while(os.path.exists(data_directory + "%s/%i/%i" % (subdirectory, i, j))):
            with open(data_directory + "%s/%i/%i" % (subdirectory, i, j), 'r') as to_parse:
                temp = refactor_crawler(to_parse.read())
            if temp:
                # erase the contents
                with open(results_directory + "%s/%i_%i" % (subdirectory, i, j), 'w') as file:
                    pass
                # write the sentences
                with open(results_directory + "%s/%i_%i" % (subdirectory, i, j), 'a') as file:
                    for s in temp:
                        file.write(s + "\n")
                    print("successful with : " + data_directory + "%s/%i/%i" % (subdirectory, i, j))
            j += 1
        j = 0
        i += 1


def parse_for_systran(date="2015_01_05"):
    # download_crawler_data(date)
    _parse_for_systran_directory(subdirectory=date)


def update():
    start_date = dt.datetime(2015, 1, 1)
    end_date = (dt.datetime.now() - dt.timedelta(days=1))# .__str__().replace("-","_")
    total_days = (end_date - start_date).days + 1
    for day_number in range(total_days):
        current_date = (start_date + dt.timedelta(days=day_number)).date().__str__().replace("-","_")
        if not os.path.isdir(DEFAULT_DATA_DIRECTORY + current_date):
            print("updating : " + current_date)
            download_and_parse_data(current_date)
    unify(names_file=BIG_FILES_DIRECTORY + "names_" + end_date.date().__str__().replace("-", "_") + ".jsons",
          concepts_file=BIG_FILES_DIRECTORY + "concepts_" + end_date.date().__str__().replace("-","_") + ".jsons")


if __name__ == "__main__":
    pass