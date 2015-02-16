"""@file parse_crawler

Utils for downloading and parsing crawler data.
"""
from abstracter.parsers.retriever import retrieve_words_names
from abstracter.util.json_stream import *
from abstracter.util.http import make_http_request
import json
import os
import tarfile,sys
import shutil
from re import match
from glob import glob


DEFAULT_DATA_DIRECTORY="crawlerpsc/"
DEFAULT_RESULTS_DIRECTORY="concepts/"
CONCEPTS_NAMES_DATA_DIRECTORY="concepts_names_data/"
CRAWLER_URL='http://nadrieril.fr/dropbox/crawlerpsc/'
#default location of the data directory when it is downloaded and uncompressed
DEFAULT_LOCATION="srv/ftp/crawlerpsc/"


def download_crawler_data(date):
	"""
	Download raw data for a day.

	@param Date : Formatted date AAAA_MM_JJ, such as 2015_01_03 (str).
	"""
	full_url=CRAWLER_URL+date+".tar.gz"
	print("downloading : "+full_url)
	r = make_http_request(full_url)#requests.get(full_url,proxies=PROXY)
	#print(len(r.content))
	if not os.path.isdir(DEFAULT_DATA_DIRECTORY):
		os.makedirs(DEFAULT_DATA_DIRECTORY)
	with open(DEFAULT_DATA_DIRECTORY+date+".tar.gz",'wb') as f:
		#f.write(r.content)
		f.write(r.content)
	#untar and extract in the same directory
	tar=tarfile.open(DEFAULT_DATA_DIRECTORY+date+".tar.gz","r:gz")
	tar.extractall(DEFAULT_DATA_DIRECTORY)
	tar.close()
	#move the directory
	try:
		shutil.move(os.path.join(DEFAULT_DATA_DIRECTORY,DEFAULT_LOCATION+date),DEFAULT_DATA_DIRECTORY)
	except shutil.Error:
		print("Error, maybe the directory "+date+" already exists")
	os.remove(DEFAULT_DATA_DIRECTORY+date+".tar.gz")
	#works but not useful
	#shutil.rmtree(os.path.join(DEFAULT_DATA_DIRECTORY,"srv"))
	print("Success with : "+date)





def parse_article(filename):
	"""
	Parse an article from the crawler, retrieve words and names.

	@param filename Name of the file to parse.
	@return A tuple of two lists : [words,names].
	"""
	with open(filename,'r') as file:
		text=file.read() 
		return retrieve_words_names(text)
	return []


def _parse_directory(max_subdirectories=10,max_files=1000,data_directory=DEFAULT_DATA_DIRECTORY,
	results_directory=DEFAULT_RESULTS_DIRECTORY,subdirectory="2014_12_04"):
	"""
	Parse a directory from the crawler.

	@param max_subdirectories Maximum number of subdirectories to consider.
	@param max_files Maximum number of files to analyze in a subdirectory.
	@param subdirectory The subdirectory to consider (formatted date AAAA_MM_JJ).
	"""
	if not os.path.isdir(results_directory+subdirectory+"/"):
		os.makedirs(results_directory+subdirectory+"/")
	i=0
	j=0
	while(os.path.exists(data_directory+"%s/%i/%i" % (subdirectory,i,j)) and i<max_subdirectories):
		while(os.path.exists(data_directory+"%s/%i/%i" % (subdirectory,i,j)) and j<max_files):
			temp=parse_article(data_directory+"%s/%i/%i" % (subdirectory,i,j))
			if temp:
				with open(results_directory+"%s/%i_%i_concepts.json" % (subdirectory,i,j),'w') as file:
					json.dump(temp[0],file)
				with open(results_directory+"%s/%i_%i_names.json" % (subdirectory,i,j),'w') as file:
					json.dump(temp[1],file)
					print("successful with : "+data_directory+"%s/%i/%i" % (subdirectory,i,j))
			j+=1
		j=0
		i+=1



def unify_day(directory=DEFAULT_RESULTS_DIRECTORY,max_files=1000,subdirectory="2014_12_04",
	names_file=None,concepts_file=None):
	"""
	Unify concepts and names files for a day.

	The result, two dict objects, is written as JSON streams in two separated files. 
	The value associated with each name counts the number of occurrences.
	"""
	if not os.path.isdir(CONCEPTS_NAMES_DATA_DIRECTORY):
		os.makedirs(CONCEPTS_NAMES_DATA_DIRECTORY)
	i=0
	j=0
	all_names={}
	k=0
	while(os.path.exists(directory+"%s/%i_%i_names.json" % (subdirectory,i,j)) and k<max_files):
		while(os.path.exists(directory+"%s/%i_%i_names.json" % (subdirectory,i,j)) and k<max_files):
			k+=1
			temp=[]
			with open(directory+"%s/%i_%i_names.json" % (subdirectory,i,j),'r') as file:
				temp=json.load(file)
				#print("successful loading of "+directory+"%i/%i" % (i,j))
			if temp:
				for c in temp:
					if c in all_names:
						all_names[c]+=temp[c]
					else:
						all_names[c]=temp[c]
			j+=1
		j=0
		i+=1	
	if not names_file:
		names_file=CONCEPTS_NAMES_DATA_DIRECTORY+subdirectory+"_all_names.jsons"
	writer=JSONStreamWriter(names_file)
	for d in all_names.items():
		writer.write(d)
	writer.close()
	i=0
	j=0
	all_concepts={}
	k=0
	while(os.path.exists(directory+"%s/%i_%i_concepts.json" % (subdirectory,i,j)) and k<max_files):
		while(os.path.exists(directory+"%s/%i_%i_concepts.json" % (subdirectory,i,j)) and k<max_files):
			k+=1
			temp=[]
			with open(directory+"%s/%i_%i_concepts.json" % (subdirectory,i,j),'r') as file:
				temp=json.load(file)
				#print("successful loading of "+directory+"%i/%i" % (i,j))
			if temp:
				for c in temp:
					if c in all_concepts:
						all_concepts[c]+=temp[c]
					else:
						all_concepts[c]=temp[c]
			j+=1
		j=0
		i+=1	
	if not concepts_file:
		concepts_file=CONCEPTS_NAMES_DATA_DIRECTORY+subdirectory+"_all_concepts.jsons"	
	writer=JSONStreamWriter(concepts_file)
	for d in all_concepts.items():
		writer.write(d)
	writer.close()



def unify(directory=CONCEPTS_NAMES_DATA_DIRECTORY,max_files=1000,names_file="names.jsons",concepts_file="concepts.jsons"):
	"""
	Unifies all dicts of concepts and list of names into two single files.
	Retrieves all data from the default directory, with a maximum number of files.
	Suppress bad characters.

	@param names_file Name of the file where names will be written.
	@param concepts_file Name of the file where concepts will be written.
	@param directory Name of the directory where to read and write files.
	"""
	#(_, _, filenames) = os.walk(directory).next()
	filenames=glob(directory+"*names.jsons")[0:max_files]
	fileconcepts=glob(directory+"*concepts.jsons")[0:max_files]
	thedict={}
	for name in filenames:
		for c in read_json_stream(name):
			#avoid bad words
			if match('^[a-zA-Z\s-]*$',c[0]) and len(c[0]) < 20:
				if c[0] not in thedict:
					thedict[c[0]]=1
				else:
					thedict[c[0]]+=c[1]
		print("successful reading of :"+name)
	writer=JSONStreamWriter(names_file)
	for d in thedict.items():
		writer.write(d)
	writer.close()
	thedict={}
	for name in fileconcepts:
		for c in read_json_stream(name):
			#avoid bad words
			if match('^[a-zA-Z\s-]*$',c[0]) and len(c[0]) < 20:
				if c[0] not in thedict:
					thedict[c[0]]=1
				else:
					thedict[c[0]]+=c[1]
		print("successful reading of :"+name)
	writer=JSONStreamWriter(concepts_file)
	for d in thedict.items():
		writer.write(d)
	writer.close()


def download_and_parse_data(date="2015_01_05"):
	"""
	Download data for a day, parse it, unify the dicts of names and concepts and
	write them in the default directory.
	"""
	download_crawler_data(date)
	_parse_directory(max_subdirectories=10,max_files=1000,subdirectory=date)
	unify_day(subdirectory=date)


def demo():
	download_and_parse_data("2014_12_30")
	unify()

if __name__=="__main__":
	demo()