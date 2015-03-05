from abstracter.concepts_network import *
from abstracter import *

def get_full_name(name,names_list):
    temp=name
    for e in entity_list:
        if temp in e:
            temp=e
    return temp


def _refactor(names_list):
	for name in names_list:
		yield name.lower().replace(' ','_')


def match_entities(par_context,names_list):
	"""
	Names or subjects that appear in a phrase are linked together and to entities in the conceptsNetwork.

	@param network conceptsNetwork
	@param names_list List of names, ordered as they appear in the text.
	"""
	context=par_context if par_context else Context()
	refactored=_refactor(names_list)
	result=dict()
	first_matches=list()
	for name in refactored:
		if context.network.has_node(name):
			result[name]=name
			first_matches.append(name)
	for name in refactored:
		if get_full_name(name,first_matches) != name:
			result[name]=get_full_name(name,first_matches)

	#print(list(_activate_entities(context,first_matches)))
	return result

	#pass

def _activate_entities(context,entities_list):
	for e in entities_list:
		context.activate(e,50)
	context.run(len(entities_list)*5)
	return context.get_activated_nodes()
	#print(list(context.get_activated_nodes()))

