
"""
Retrieving data, computing a tf-idf-like indice.
"""
import os
from glob import glob
from abstracter.util.json_stream import *
from re import match
import json

DEFAULT_RESULTS_DIRECTORY="concepts/"
CONCEPTS_NAMES_DATA_DIRECTORY="concepts_names_data/"
DIRECTORY="tfidf/"

import operator

def build_database(max_files=100):
	tf_data=dict()
	idf_data=dict()
	
	if not os.path.isdir(DIRECTORY):
		os.makedirs(DIRECTORY)
	fileconcepts=glob(CONCEPTS_NAMES_DATA_DIRECTORY+"*all_concepts.jsons")[0:max_files]
	smallfiles=glob(DEFAULT_RESULTS_DIRECTORY+"/*/*concepts.json")[0:10000]
	#building tf database
	for filename in fileconcepts:
		for c in read_json_stream(filename):
			#avoid bad words
			if match('^[a-zA-Z\s-]*$',c[0]) and len(c[0]) < 20:
				if c[0] not in tf_data:
					tf_data[c[0]]=1
				else:
					tf_data[c[0]]+=c[1]
		#print("successful reading of :"+filename)
	writer=JSONStreamWriter(DIRECTORY+"tf_data.jsons")
	for d in tf_data.items():
		writer.write(d)
	writer.close()
	#building idf database
	for thefile in smallfiles:
		with open(thefile,'r') as file:
			temp=json.load(file)
		if temp:
			for c in temp:
				if c in tf_data:
					if c in idf_data:
						idf_data[c]+=1
					else:
						idf_data[c]=1
	writer=JSONStreamWriter(DIRECTORY+"idf_data.jsons")
	for d in idf_data.items():
		writer.write(d)
	writer.close()
	print(len(tf_data))
	print(len(idf_data))
	tfidf_data=dict()
	for c in tf_data:
		if c in idf_data:
			tfidf_data[c]=tf_data[c]/idf_data[c]
	sorted_data=sorted(tfidf_data.items(),key=operator.itemgetter(1))
	sorted_data.reverse()
	writer=JSONStreamWriter(DIRECTORY+"tfidf_data.jsons")
	for d in sorted_data:
		writer.write(d)
	writer.close()	


build_database()