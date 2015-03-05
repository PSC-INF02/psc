from abstracter.crawler.parse_crawler import * #download_and_parse_data,download_crawler_data,unify

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


from abstracter.workspace.entities_recognition import *
from abstracter import *
context=Context()

#activate_entities(context,["wayne_rooney"])
print(match_entities(context,["wayne rooney","wayne"]))