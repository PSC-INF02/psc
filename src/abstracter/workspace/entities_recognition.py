from abstracter.concepts_network import *
from abstracter import *
from abstracter.util.distance import levenshtein

def _get_full_name(name,names_list):
    for e in names_list:
        if name in e:
            return e
    return None



def _refactor(names_list):
    for name in names_list:
        yield name.lower().replace(' ','_')


def match_entities(par_context,names_list):
    """
    Names or subjects that appear in a phrase are linked together and to entities in the conceptsNetwork.

    @param network conceptsNetwork
    @param names_list List of names, ordered as they appear in the text.

    @return A dict of name : entity in the ConceptNetwork (or name itself if this entity doesn't exist).
    """
    context=par_context if par_context else Context()
    #first : refactor the names in names_list (replace spaces with underscores...)
    refactored=list(_refactor(names_list))
    result=dict()

    #find first matches : entity that are in the concept network
    first_matches=list()
    for name in refactored:
        if context.network.has_node(name):
            result[name]=name
            first_matches.append(name)
    #print(result)

    #find second matches : a surname instead of a full name, for example
    second_matches=list()
    temp=refactored.copy()
    temp.reverse()
    for i in range(len(refactored)):
        name=temp[0]
        temp.remove(name)
        if _get_full_name(name,temp):
            result[name]=_get_full_name(name,temp)
            second_matches.append(name)
    #print(result)

    for name in first_matches:
        refactored.remove(name)

    for name in second_matches:
        refactored.remove(name)    

    if refactored:
        possible_matches=list(_activate_entities(context,first_matches))
        for name in refactored:
            n,d=_minimize_distance(name,possible_matches)
            if d<0.5:
                result[name]=n
            else:
                result[name]=name
    return result



def _minimize_distance(name,name_list):
    result=name,-1
    for name2 in name_list:
        d=levenshtein(name,name2, normalized=True, max_dist=-1)
        if result[1]<0:
            result=name2,d
        if d<result[1]:
            result=name2,d
    return result


def _activate_entities(context,entities_list):
    for e in entities_list:
        context.activate(e,50)
    context.run(len(entities_list)*5)
    return context.get_activated_nodes()
    #print(list(context.get_activated_nodes()))

