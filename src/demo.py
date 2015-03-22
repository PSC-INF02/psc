from abstracter.crawler.parse_crawler import *  #download_and_parse_data,download_crawler_data,unify

#download_and_parse fait tout pour une date : télécharger sur le crawler, 
#stocker localement les données, parser les articles 
#et faire des listes de concepts + de noms
#il crée aussi de nouveaux fichiers dans concepts_names_data

#download_crawler_data("2015_02_01")#without parsing this one
#download_and_parse_data("2015_01_31")
#download_and_parse_data("2015_02_15")
#unify_day(subdirectory="2015_02_15")
#unify()
#download_and_parse_data("2015_02_06")

#from abstracter.parsers import retriever as ret

#text="Peyton Manning was in a bad mood yesterday because I don't know yet."
#print(ret.retrieve_words_names(text))

#unify()
#update()

#from abstracter.workspace.entities_recognition import *
#from abstracter import *

#import networkx as nx

#from nltk.sem.logic import ParseException

from abstracter.util.crego_to_json import crego_to_json
from abstracter.parsers.tokenizer import *
from abstracter.util.anaphora_resolution import *

#with open("../systran/3",'r') as file:
#    text = file.read()
#with open("../systran/refactored",'a') as file:
#    for s in refactor_crawler(text):
#        file.write(s+"\n")

data = sentence_to_dict(crego_to_json("../systran/example"))
#print(get_tag(data, 0, "location"))
#print_noun_phrases(data, get_noun_phrases(data))
#print(sentence_to_dict(data))
resolve_anaphoras(data, get_noun_phrases(data))

#with open("../systran/parsed_example.json",'w') as file:
#    json.dump(crego_to_json("../systran/example"),file)

#json.dump(crego_to_json("../systran/test")))

#print("toto")

#activate_entities(context,["wayne_rooney"])
#context=Context()
#print(match_entities(context,["wayne rooney","wayne"]))

#liste=["Everton","Goodison Park","Roberto Martinez","Martinez","Champions League","Diego Simeone","Atletico Madrid",
#"FIFA","David Moyes","Barcelona","Real Sociedad","New Year's Day","Premier League","Roberto"];
#print(match_entities(context,liste))

#print(minimize_distance("soccer_player",["the soccer player"]))



#print(context.network.shortest_path("wayne_rooney","bedroom"))


#for g in nx.weakly_connected_component_subgraphs(context.network.network):
#    print(nx.average_shortest_path_length(g))

text="""Everton are on their worst run since December 2005, but the Goodison Park fans must get behind Roberto Martinez
Martinez was praised last year for his style of play that took Everton to the brink of Champions League qualification
Talk of Martinez needing to change his style is baffling Diego Simeone's work at Atletico Madrid has been 
unbelievable, I hope he wins FIFA's coach of the year award 
He was darling of Goodison Park this time last year, hailed by supporters for bringing back ‘the School of Science’.
Having got Everton playing a slick, fast brand of football that almost took them into the Champions League, Roberto Martinez could 
do no wrong but, suddenly, he has become the topic of an increasingly heated debate.The argument? He needs to change and get7
 Everton playing a more solid and direct style, like David Moyes favoured. Maybe some watched Real Sociedad’s backs-to-the-wall 
 victory against Barcelona and were reminded of similar big wins that their former manager had inspired.       
    Roberto Martinez is under pressure at Everton with his team lying just four points ahead of the relegation zone      
    Everton have been struggling in the Premier League and have failed to hit the heights of last season  
A 2-0 defeat by Hull on New Year's Day was Everton's fourth Premier League loss in a row
"""