from nltk.corpus import wordnet as wnc
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.tokenize import PunktWordTokenizer
from nltk.tokenize import TreebankWordTokenizer
from abstracter.concepts_network import Network
import abstracter.parsers.tokenizer as tok
import abstracter.parsers.concepts_retriever as cr
from abstracter.util import json_stream
from abstracter.conceptnet5_client.api import api as cn5
import json
import os

"""
These methods do not intend to be optimal, 
but have to provide an easy way to create a small conceptnetwork
for our research.

Here, we implement the following :
- reading and tokenizing the text downto words
- tag these words with a POS from nltk
- creating the network from these words by using wordnet data
- we use polysemy to compute concept degree of abstraction
- we use path_similarity to compute approximately similarity between all our nodes :

synset1.path_similarity(synset2): 
Return a score denoting how similar two word senses are, 
based on the shortest path that connects the senses in the is-a
(hypernym/hypnoym) taxonomy. The score is in the range 0 to 1. 
By default, there is now a fake root node added to verbs so for
cases where previously a path could not be found---and None 
was returned---it should return a value. The old behavior can 
be achieved by setting simulate_root to be False. A score of 1 
represents identity i.e. comparing a sense with itself will 
return 1.
(from http://www.nltk.org/howto/wordnet.html)

"""


#sample_corpus_reader=corpus.PlaintextCorpusReader(os.getcwd()+'/sample_corpus','.*\.txt')



DISMISSED_WORDS=[",",";","."]
#use also PunktWordTokenizer() or TreebankWordTokenizer()


def tokenize(text):
	#word_list=TreebankWordTokenizer().tokenize(text);
	#res=[]
	#for word in word_list:
	#	if word.rstrip('.'):
	#		res.append(word.rstrip('.'))
	#		#cause we do not keep the .
	return tok.tokenize(text)


def tag(word_list):
	return pos_tag(word_list)

def read_concepts(filename="data/sample"):
	with open(filename+".txt",'r') as file,open(filename+"_concepts.txt",'w') as conceptsfile:
		print("Reading "+filename+" and calculating concepts...")
		concepts=cr.retrieve_concepts(file.read())
		print("Writing down...")
		json.dump(concepts,conceptsfile)



#######################################################################################
################deprecated ! use only module concepts_retriever
##############################################################

def read_and_tokenize(filename="data/sample"):
	"""
	We read the text and tokenize it, but we don't create the network.
	"""
	with open(filename+".txt",'r') as file,open(filename+"_words.txt",'w') as wordsfile:
		word_list=tokenize(file.read())
		print("Writing words down...")
		json.dump(word_list,wordsfile)
	tagged_list=pos_tag(word_list)
	with open(filename+"_tags.txt",'w') as tagsfile:
		print("Writing POS-tagged words down...")
		json.dump(tagged_list,tagsfile)
	print("All done.")


def read_text(filename="data/sample"):
	"""
	Write down a new file at each state, to see how it progresses
	"""
	with open(filename+".txt",'r') as file,open(filename+"_words.txt",'w') as wordsfile:
		word_list=tokenize(file.read())
		print("Writing words down...")
		json.dump(word_list,wordsfile)	
	tagged_list=pos_tag(word_list)
	with open(filename+"_tags.txt",'w') as tagsfile:
		print("Writing POS-tagged words down...")
		json.dump(tagged_list,tagsfile)
	wordnet_tagged_list=tag_words_for_wordnet(tagged_list)
	with open(filename+"_wordnet_parsed.txt",'w') as wfile:
		print("Writing wordnet-tagged words down...")
		json.dump(wordnet_tagged_list,wfile)
	print("Generating network...")
	conceptnetwork=create_network_from_words(wordnet_tagged_list)
	conceptnetwork.save_to_JSON(filename+"_network.txt")
	


def tag_words_for_wordnet(tagged_list):
	#nltk.pos_tag uses the Penn Treebank project
	#list of tags available at : http://www.ling.upenn.edu/courses/Fall_2007/ling001/penn_treebank_pos.html
	wordnet_tagged_list=[]
	final_list=[]
	
	for w in tagged_list:
		v=w[0]
		tag=w[1]
		if v in DISMISSED_WORDS:
			pass
		elif tag=='FW':#foreign word
			t=wnc.NOUN
			wordnet_tagged_list.append([v,t])
		elif tag in ["JJ","JJR","JJS"]:
			t=wnc.ADJ
			wordnet_tagged_list.append([v,t])
		elif tag in ["MD","NN","NNS"]:
			t=wnc.NOUN
			wordnet_tagged_list.append([v,t])
		elif tag in ["NNP","NNPS"]:#not tag
			t=None
			final_list.append([v,t])
		elif tag in ["RB","RBR","RBS"]:
			t=wnc.ADV
			wordnet_tagged_list.append([v,t])
		elif tag in ["VB","VBD","VBG","VBN","VBP","VBZ"]:
			t=wnc.VERB
			wordnet_tagged_list.append([v,t])
		#we're not interested by other tags (especially small words)

	#the .01 here refers is a lexical id, used by wordnet to make 
	#a difference between different senses of the same word
	#n for nou, v for verb, a for adjective, r for adverb
	
	#correspondance={wnc.NOUN : ".n.01", wnc.ADJ : ".a.01", wnc.ADV : ".r.01", wnc.VERB : ".v.01"}
	for (v,tag) in wordnet_tagged_list:
		vmorphed=wnc.morphy(v,tag)
		if vmorphed and [vmorphed,tag] not in final_list:
			final_list.append([vmorphed,tag])
		elif [v,tag] not in final_list:
			final_list.append([v,tag])
	final_list.sort()
	return final_list
	

def remove_co_occurrences(wordnet_tagged_list):
	"""
	could have been useful, but already done in the method
	tag_words_for_wordnet
	"""
	pass


def create_network_from_words(wordnet_tagged_list):
	"""
	Create network (small one)
	We use wordnet data to approach ic, by using polysemy
	Idea : the more a word is an abstract concept, the more 
	it has different meanings
	First, we create all concepts with this approach
	If it's a proper noun, it has no wordnet tag, thus we only create
	a corresponding concept with high ic


	Then, we create edges.
	We create a dictionary of synsets for each concept.
	We keep only one sens possible, the first, which is not good
	(we could capture the real sense in the text)

	We use a similarity measure in term of path between node, based
	on the shortest path connecting the node in the is-a relationship
	(from 0 to 1, with 1 they are synonyms)


	"""
	concepts=Network()
	for v,tag in wordnet_tagged_list:
		if tag:
			polysemy=len(wnc.synsets(v,pos=tag))
			concepts.add_node(id=v,ic=polysemy)
		else:#no tag, such as a proper noun
			concepts.add_node(id=v,ic=5)
	#at this point, all nodes have been created
	#then, we study edges
	#following code to build edges from wordnet, using isa relations
	wnsynsets={}
	for v,tag in wordnet_tagged_list:
		if tag and wnc.synsets(v,pos=tag):#if it s not empty
			wnsynsets[v]=wnc.synset(wnc.synsets(v,pos=tag)[0].name())
	#not beautiful : only keeping the first sense possible of the word
	for v,tag in wordnet_tagged_list:
		for v2,tag2 in wordnet_tagged_list:
			if v in wnsynsets and v2 in wnsynsets:
				if (not v==v2) and wnsynsets[v] and wnsynsets[v2]:
					tmp=wnsynsets[v].path_similarity(wnsynsets[v2])
					if tmp >0.1:
						concepts.add_edge(fromId=v,toId=v2,w=tmp)
	return concepts


####################################################################

def polysemy(word):
	return len(wnc.synsets(word,pos=None)) 





def expand_concept(concept,network):
	"""
	network : Network object
	"""
	edges=cn5.search_edges_from(concept)
	for e in edges:
		network.add_edge(fromId=e.start,toId=e.end,w=e.weight,r=e.rel)
	return



def expand_network_from_seed(words,max_nodes=10,network=Network(),max=2):
	"""
	Given list of some relevant concepts, we create a conceptnetwork using :
	-conceptnet5 data
	-wordnet polysemy
	Notes :
	- a node can't expand more than a fixed number of edges (see conceptnet5.py)
	- there is a random component when we get the edges from conceptnet5
	"""
	nodenumber=0
	k=0
	list2=[]
	while nodenumber<max_nodes and k<max:
		k+=1
		print(len(words))
		for word in words:
			#print(word)
			conceptic=polysemy(word)
			if conceptic==0:#TODO : check if it's a name
					conceptic=7
			#print(conceptic)
			if not network.has_node(word):
				network.add_node(id=word,ic=conceptic)
				nodenumber+=1
				expand_concept(word,network)
				for word2 in network.successors(word):
					list2.append(word2)
		words=list2


			
SEED=["America","Arsenal","Aston","Barkley","Basel","Brazil","Cahill","Cup","England","Euro","Liverpool","Manchester","Norway","Sterling","wayne_rooney",
"Switzerland","Uruguay","World","apathy","appointment","atmosphere","attacker","back","brilliantly","busy","captain","celebrate", "comprehensively","decisive","defeat","display","eliminate","encouragement","exit","glamorous","imagination","opponent","partnership",
"penalty","performance","play","player","positive","preparation","pressure","prove","public","retire","summer","surreal", "team", "winner","worry","victory", "young"]

SMALL_SEED=["America","Arsenal","Brazil","Cup","England","wayne_rooney","appointment","atmosphere",
"attacker","back","brilliantly","busy","captain","celebrate"]
#,"defeat","eliminate","encouragement","exit",
#"penalty","performance","play","player","positive","preparation","pressure","prove","public",
# "team", "winner","worry","victory", "young"

def test():
	n=Network()
	seed=SMALL_SEED
	with open("data/sample_concepts.txt",'r') as file:
		seed=json.load(file)
	expand_network_from_seed(seed[1:5],max_nodes=10,network=n)
	n.save_to_JSON_stream("network_example/network_example_5")
	n.draw("network_example/network_example_5.png")

#does not work
def clean_cached_data():
	for file in os.listdir("src/cached_data"):
		os.remove(file)


#read_concepts(filename="data/sample")


#print(cn5.get_similarity('sport','wayne_rooney'))

#for e in (cn5.search_edges(start="/c/en/sport",limit=10,toto="bouh")):
#	e.print_edge()

#for e in (cn5.search_edges_from("hockey")):
#	e.print_edge()

#print(cn5.get_similar_concepts('america'))
#for e in cn5.search_edges(start="/c/en/america"):
#	e.print_edge()

#print(cn5.get_similarity(concept1="democracy",concept2="sport"))

def expand_by_similarity(concept,network):
	"""
	network : Network object
	"""
	concepts=cn5.get_similar_concepts(concept)
	for c in concepts:
		if not network.has_node(c[0]):
			conceptic=polysemy(c[0])
			if conceptic==0:#TODO : check if it's a name
				conceptic=7
			network.add_node(id=c[0],ic=conceptic)
		edge=cn5.search_edge(start=concept,end=c[0])
		if edge:
			network.add_edge(fromId=concept,toId=edge.end,w=edge.weight/5,r=edge.rel)
		else:
			network.add_edge(fromId=concept,toId=c[0],w=c[1],r='SimilarTo')

def create_node(concept,network):
	if not network.has_node(concept):
		conceptic=polysemy(concept)
		if conceptic==0:#TODO : check if it's a name
			conceptic=7
		network.add_node(id=concept,ic=conceptic)	

def test2():
	n=Network()
	seed=SMALL_SEED
	with open("data/sample_concepts.txt",'r') as file:
		seed=json.load(file)
	for word in seed[1:4]:
		conceptic=polysemy(word)
		if conceptic==0:#TODO : check if it's a name
			conceptic=7
		if not n.has_node(word):
			n.add_node(id=word,ic=conceptic)
			expand_by_similarity(word,n)
	n.save_to_JSON_stream("network_example/network_example_6")
	n.draw("network_example/network_example_6.png")


MINIMUM_SIMILARITY=0.1

def expand_by_similarity_to(concept,network,filter):
	edges=cn5.search_edges_from(concept)
	for e in edges:
		sim=cn5.get_similarity(e.end,filter)
		if sim>MINIMUM_SIMILARITY and e.end != concept:
			create_node(e.end,network)
			network.add_edge(fromId=concept,toId=e.end,w=e.weight/5,r=e.rel)


def remove_leaves(network):
	tosuppr=[]
	for n in network.network.node:
		has_succ=False
		for s in network.successors(n):
			has_succ=True
			pass
		if not has_succ:
			tosuppr.append(n)
	for n in tosuppr:
		network.remove_node(n)

def test3():
	n=Network()
	seed=SMALL_SEED	
	with open("data/sample_concepts.txt",'r') as file:
		seed=json.load(file)
	for word in seed:
		create_node(word,n)
		expand_by_similarity_to(word,n,filter="sport")
	n.save_to_JSON_stream("network_example/network_example_6")
	n.draw("network_example/network_example_6.png")

def test4():
	n=Network()
	seed=SMALL_SEED	
	with open("data/sample_concepts.txt",'r') as file:
		seed=json.load(file)
	for word in seed[1:10]:
		create_node(word,n)
		expand_by_similarity(word,n)
	n.save_to_JSON_stream("network_example/network_example_6")
	n.draw("network_example/network_example_6.png")

#print(cn5.get_similar_concepts_by_term_list(term_list=["america"]))
test4()
