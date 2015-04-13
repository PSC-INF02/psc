"""
Small experiment, to see how our knowledge increases with the time.
"""
from abstracter.crawler.parse_crawler import *
import json
import os
import tarfile
import shutil
from re import match
from glob import glob
import datetime as dt
from abstracter.util.json_stream import *




def exp():
    dictn = {}
    dictc = {}
    start_date = dt.datetime(2015, 1, 1)
    end_date = (dt.datetime.now() - dt.timedelta(days=1))# .__str__().replace("-","_")
    total_days = (end_date - start_date).days + 1
    for day_number in range(total_days):
        current_date = (start_date + dt.timedelta(days=day_number)).date().__str__().replace("-","_")
        if os.path.isdir(DEFAULT_DATA_DIRECTORY + current_date):
            filename = CONCEPTS_NAMES_DATA_DIRECTORY + current_date + "_all_names.jsons"
            fileconcept = CONCEPTS_NAMES_DATA_DIRECTORY + current_date + "_all_concepts.jsons"
            try:
                for c in read_json_stream(filename):
                    # avoid bad words
                    if match('^[a-zA-Z\s-]*$', c[0]) and len(c[0]) < 20:
                        if c[0] not in dictn:
                            dictn[c[0]] = c[1]
                        else:
                            dictn[c[0]] += c[1]
                for c in read_json_stream(fileconcept):
                # avoid bad words
                    if match('^[a-zA-Z\s-]*$', c[0]) and len(c[0]) < 20:
                        if c[0] not in dictc:
                            dictc[c[0]] = c[1]
                        else:
                            dictc[c[0]] += c[1]
            except FileNotFoundError:
                pass
            n = 0
            for t in dictn:
                if dictn[t] > 1:
                    n += 1
            c = 0
            for t in dictc:
                if dictc[t] > 1:
                    c += 1
            print(current_date + "  " + len(dictn.keys()).__str__() + "  " + n.__str__() + "  " + len(dictc.keys()).__str__() + "  " + c.__str__())


exp()

#download_and_parse_data("2015_03_14")
#unify_day(subdirectory="2015_03_15")