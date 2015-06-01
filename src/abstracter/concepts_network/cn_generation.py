"""@file cn_generation.py

All utils to generate a concepts network from raw data
or expand an already existing one.

Example :
@code
from abstracter.concepts_network.cn_generation import *

creation_demo("names_2015_03_29.jsons", "concepts_2015_03_29.jsons")
@endcode
Will treat those two files and generate a ConceptNetwork
based on those words.

The building of the network is made by different means :
* expand_similarity will expand the words by using Association requests
in Conceptnet5.
* expand_lookup will do the same with Lookup requests
* expand_edges will do the same with search requests
* expand_names will run a search in Freebase.

@see conceptnet5_client

Each time, you have the choice between :
* using it on a file (a raw list of words in JSONStream format)
* using it on the network

We use activation to tag the nodes to keep. Nodes coming directly from
a file (words from the file) are activated. Nodes created by
further requests aren't. When you use a method on the network, you can choose
wether you want it to treat activated or not activated nodes. Activated nodes
are considered relevant, but treating not activated nodes may help
you to find new interesting links.

When you use a method, you can also expand the nodes without creating
new ones at the end, or at the beginning of and edge (to_existing and from_existing).


To create a new network, you may use a code like :
@code
from abstracter.concepts_network.cn_generation import *

LOG_FILE = open("log.txt", 'a')
print_network_status()

use_method_on_file(DATA_DIR + "names_2015_03_29.jsons", expand_names, max=1000, to_existing=False, from_existing=False)
print_network_status()

use_method_on_file(DATA_DIR + "concepts_2015_03_29.jsons", expand_lookup, max=1000, to_existing=False, from_existing=False)
print_network_status()

use_method_on_network(expand_edges, max=100000, to_existing=True, from_existing=False, not_act=True, act=False)
print_network_status()

use_method_on_network(expand_edges, max=100000, to_existing=False, from_existing=True, not_act=False, act=True)
print_network_status()

tag_less_linked_nodes(limit=100000)
print_network_status()

clear_ic(limit=100000)
clear_act(limit=100000)
deactivate_nodes(limit=100000)
print_network_status()

save_dir("rc")
LOG_FILE.close()
@endcode

And it will be ready to use.

To adapt a new network (for example, to add new words from a file) :
@code
from abstracter.concepts_network.cn_generation import *

LOG_FILE = open("rc4/log.txt", 'a')
load_dir("rc4")
activate_nodes()# activate all nodes in the network, to keep them
print_network_status()

use_method_on_file(DATA_DIR + "names_2015_03_29.jsons", expand_names, max=100000, to_existing=False, from_existing=False)
print_network_status()

use_method_on_file(DATA_DIR + "concepts_2015_03_29.jsons", expand_lookup, max=100000, to_existing=False, from_existing=False)
print_network_status()

use_method_on_network(expand_edges, max=100000, to_existing=True, from_existing=False, not_act=True, act=False)
print_network_status()

use_method_on_network(expand_edges, max=100000, to_existing=False, from_existing=True, not_act=False, act=True)
print_network_status()

tag_less_linked_nodes(limit=100000)
print_network_status()

clear_ic(limit=100000)
clear_act(limit=100000)
deactivate_nodes(limit=100000)
print_network_status()

save_dir("rc5")
LOG_FILE.close()
@endcode

To every function, the arguments 'limit' or 'max' represent a maximum
number of nodes to consider. It is useful, to choose between doing
small tests and creating real-life bigger networks.
"""

import abstracter.conceptnet5_client.concurrent_api as ca
from abstracter.concepts_network import ConceptNetwork
from abstracter.util import json_stream as js
import abstracter.freebase_client as fb
import re
import os


############################
# Default name IC (on 100)
###########################

NAME_IC = 80

##############################
# Default ic of a word (if no information available)
################################
OTHER_IC = 40

DEFAULT_IC = 40

#####################################
# Default directory where to retrieve concepts and names dicts
#####################################

DATA_DIR = "../concepts_names_dicts/"

####################################
# Network
##################################

NETWORK = ConceptNetwork()

####################################
# Black list : contains all
# words, names, concepts, which did not
# provide any useful result when we tried
# requests
####################################
BL = set()

####################################
# Success list : contains all words
# which were sent to conceptnet5 or freebase
# and gave us good results (no need to sent
# new requests with these words)
######################################

SL = set()

LOG_FILE = None


def print_log(string):
    print(string)
    if LOG_FILE:
        LOG_FILE.write(string + "\n")


################################
# utils
############################


def create_node(concept, ic=DEFAULT_IC, a=0):
    """
    Creates a node in the ConceptNetwork.
    @return True if the node has really been created.
    """
    if not NETWORK.has_node(concept):
        NETWORK.add_node(id=concept, ic=ic, a=a)
        return True
    return False


def create_edge(fromId, toId, weight, rel):
    """
    Creates an edge in the ConceptNetwork.
    @return True if the edge has really been created.
    """
    if not NETWORK.has_edge(fromId=fromId, toId=toId):
        NETWORK.add_edge(fromId=fromId, toId=toId, w=weight, r=rel)
        return True
    return False


def add_list(the_list, word):
    """
    Adding a word to SL or BL (which implementation
    can be changed).
    """
    if word not in the_list:
        the_list.add(word)


################################
# expand methods
###################################


def expand_names(words, from_existing=False, to_existing=False):
    """
    Expands a list of names, i.e creates
    new nodes with Freebase information.

    @warning words may be a dict or a list
    @see abstracter.freebase_client
    """
    temp = not(type(words) is list)
    try:
        if temp:
            dict = fb.search_names(list(word for word in words if words[word] > 1))
        else:
            dict = fb.search_names(words)
    except Exception as e:
        print("Warning,  exception :")
        print(e)
        dict = {}
    for word in dict:
        data = dict[word]
        # If we didn't get anything, just dismiss the word
        if data:
            if not from_existing:
                # we got something : add the word to the success list
                add_list(SL, word)
            # compute a weight according to freebase's score
            weight = 100 * data['score'] / (data['score'] + 200)  # between 0 and 100
            # data['from'] may be something else than our word.
            # we can add it, of course, but we must check if it
            # is relevant.
            if len(data['from']) < 40:
                if not from_existing:
                    create_node(concept=data['from'],
                                ic=int(min(NAME_IC + (words[word] if temp else 0), 100)),
                                a=100)
                # data['to'] has also to be relevant
                if 'to' in data and data['to'] and len(data['to']) < 30:
                    if not(to_existing) or NETWORK.has_node(data['to']):
                        create_node(concept=data['to'], a=0)
                        create_edge(fromId=data['from'],
                                    toId=data['to'],
                                    weight=int(weight),
                                    rel="IsA")
        else:
            add_list(BL, word)


def expand_edges(words, from_existing=False, to_existing=False):
    """
    Expand edges in the network.

    @param words A list of words or a dict of words : number
    of occurrences.
    It is a dict if we're using the method on a file,
    a list if we're using it on a network.

    @see abstracter.conceptnet5_client
    """
    temp = not(type(words) is list)
    try:
        if temp:
            dict = ca.search_edges_from(list(word for word in words if words[word] > 1),
                                        filter='/c/en/',
                                        minWeight=1.3,
                                        limit=10)
        else:
            dict = ca.search_edges_from(words,
                                        filter='/c/en/',
                                        minWeight=1.3,
                                        limit=10)
    except Exception as e:
        print("Warning,  exception :")
        print(e)
        dict = {}
    for word in dict:
        edges = dict[word]
        if edges:
            if not from_existing:
                add_list(SL, word)
                create_node(word, ic=int(min(OTHER_IC + (words[word] if temp else 0), 100)), a=100)
        else:
            add_list(BL, word)
        for e in edges:
            if e.end != word and len(e.end) < 30:
                if not(to_existing) or NETWORK.has_node(e.end):
                    create_node(e.end, ic=int(min(OTHER_IC, 100)), a=0)
                    create_edge(fromId=word, toId=e.end, weight=int(min(e.weight * 30, 100)), rel=e.rel)


def expand_lookup(words, from_existing=False, to_existing=False):
    """
    Expand words by a lookup search.
    @warning words is a dict,  or a list

    @see abstracter.conceptnet5_client
    """
    temp = not(type(words) is list)
    try:
        dict = ca.search_concepts(list(word for word in words),
                                  filter='/c/en/', limit=10)
    except Exception as e:
        print("Warning,  exception :")
        print(e)
        dict = {}
    for word in dict:
        edges = dict[word]
        if edges:
            if not from_existing:
                add_list(SL, word)
                create_node(word,
                            ic=int(min(OTHER_IC + (words[word] if temp else 0), 100)),
                            a=100)
        else:
            add_list(BL, word)
        for e in edges:
            if e.start != word and len(e.start) < 30:
                if not(from_existing) or NETWORK.has_node(e.start):
                    create_node(e.start, ic=int(min(OTHER_IC, 100)), a=0)
            if e.end != word and len(e.end) < 30:
                if not(to_existing) or NETWORK.has_node(e.end):
                    create_node(e.end, ic=int(min(OTHER_IC, 100)), a=0)
            if NETWORK.has_node(e.start) and NETWORK.has_node(e.end):
                create_edge(fromId=e.start, toId=e.end,
                            weight=int(min(e.weight * 30, 100)), rel=e.rel)


def expand_similarity(words, from_existing=False, to_existing=False):
    """
    Expand words by an association search.

    @warning Too slow to run on more than 5000 words.

    @see abstracter.conceptnet5_client
    """
    try:
        dict = ca.get_similar_concepts(words, limit=3, filter='/c/en/')
    except Exception as e:
        dict = {}
        print("Warning,  exception :")
        print(e)
    for word in dict:
        concepts = dict[word]
        if concepts:
            add_list(SL, word)
        else:
            add_list(BL, word)
        for c in concepts:
            if c[0] != word and len(c[0]) < 30:
                if not from_existing:
                    create_node(c[0], ic=DEFAULT_IC, a=0)
                if not(to_existing) or NETWORK.has_node(c[0]):
                    create_node(c[0], ic=DEFAULT_IC, a=0)
                    create_edge(fromId=word,
                                toId=c[0],
                                weight=int(min(c[1] * 70, 100)),
                                rel='SimilarTo')


###############################################
# network treatment
############################################


def tag_linked_nodes(limit=1000):
    k = 0
    q = 0
    print_log("tag linked nodes on current network...")
    for n, d in NETWORK.nodes():
        k += 1
        if NETWORK[n]['a'] < 100 and len(list(NETWORK.predecessors(n))) + len(list(NETWORK.successors(n))) > 1:
            NETWORK[n]['a'] = 100
            q += 1
            if q % 100 == 0:
                print(q.__str__() + " nodes reactivated !")
        if k % 500 == 0:
            print(k.__str__() + " nodes looked !")
        if k > limit:
            break
    print_log(k.__str__() + " nodes looked !")
    print_log(q.__str__() + " nodes reactivated !")


def tag_less_linked_nodes(limit=1000):
    k = 0
    q = 0
    print_log("tag linked nodes on current network...")
    for n, d in NETWORK.nodes():
        k += 1
        if NETWORK[n]['a'] < 100 and len(list(NETWORK.predecessors(n))) + len(list(NETWORK.successors(n))) >= 1:
            NETWORK[n]['a'] = 100
            q += 1
            if q % 100 == 0:
                print(q.__str__() + " nodes reactivated !")
        if k % 500 == 0:
            print(k.__str__() + " nodes looked !")
        if k > limit:
            break
    print_log(k.__str__() + " nodes looked !")
    print_log(q.__str__() + " nodes reactivated !")


def tag_much_linked_nodes(limit=1000):
    k = 0
    q = 0
    print_log("tag linked nodes on current network...")
    for n, d in NETWORK.nodes():
        k += 1
        if NETWORK[n]['a'] < 100 and len(list(NETWORK.predecessors(n))) > 1:
            NETWORK[n]['a'] = 100
            q += 1
            if q % 100 == 0:
                print(q.__str__() + " nodes reactivated !")
        if k % 500 == 0:
            print(k.__str__() + " nodes looked !")
        if k > limit:
            break
    print_log(k.__str__() + " nodes looked !")
    print_log(q.__str__() + " nodes reactivated !")


def clear_nodes(filter='a', limit=1000):
    k = 0
    q = 0
    print_log("clear nodes on current network with filter " + filter)
    for n in NETWORK.nodes().copy():
        k += 1
        if NETWORK[n[0]][filter] == 0:
            NETWORK.remove_node(n[0])
            q += 1
            if q % 200 == 0:
                print(q.__str__() + " nodes removed !")
        if k % 5000 == 0:
            print(k.__str__() + " nodes looked !")
        if k > limit:
            break
    print_log(k.__str__() + " nodes looked !")
    print_log(q.__str__() + " nodes removed !")


def clear_ic(limit):
    clear_nodes(filter='ic', limit=limit)


def clear_act(limit):
    clear_nodes(filter='a', limit=limit)


def deactivate_nodes(limit=1000):
    print_log("deactivate nodes...")
    k = 0
    for n in NETWORK.nodes():
        NETWORK[n[0]]['a'] = 0
        k += 1
        if k % 500 == 0:
            print(k.__str__() + " nodes looked !")
        if k > limit:
            break
    print_log("done !")


def activate_nodes():
    print_log("activate nodes...")
    for n in NETWORK.nodes():
        NETWORK[n[0]]['a'] = 100
    print_log("done !")


##########################################


def use_method_on_file(file, expand_method, max, to_existing, from_existing):
    """
    @brief Use a specified method on a file.

    We may have a lot of words to consider (10 000, for example). We create
    dicts of 500 words, calling the method (and doing concurrent requests)
    on each one.

    @param file name of the file. It has to be JSONStream readable ;
    more precisely, we await on each line a tuple [word, number] where
    number represents a number of occurrences.

    @param expand_method The method to use.
    """
    print_log("Using method " +
              expand_method.__name__ +
              " on file " + file.__repr__() + "...")
    print_log("to_existing_nodes : " +
              to_existing.__str__() + ",  from_existing : " +
              from_existing.__str__())
    dict = {}
    k = 0
    for w in js.read_json_stream(file):
        if (re.match('^[a-zA-Z\s-]*$', w[0])
           and len(w[0]) < 20 and w[1] > 0 and not w[0] in SL
           and not w[0] in BL and not NETWORK.has_node(w[0])):
            dict[w[0]] = w[1]
            k += 1
            if len(dict) > 500:
                expand_method(words=dict, to_existing=to_existing,
                              from_existing=from_existing)
                dict = {}
            if k > max:
                break
    if len(dict) > 0:
        expand_method(words=dict, to_existing=to_existing,
                      from_existing=from_existing)
    print_log("Looked at " + k.__str__() + " elements.")


def use_method_on_network(expand_method, max, to_existing,
                          from_existing, act=True, not_act=True):
    """
    @brief Use a specified method on the network.

    The principle is similar to use_method_on_file.

    @param expand_method the method to use.
    @param act if we check activated nodes.
    @param not_act if we check not activated nodes.
    """
    print_log("Using method " + expand_method.__name__ + " on current network...")
    print_log("to_existing_nodes : " + to_existing.__str__() +
              ",  from_existing : " + from_existing.__str__() +
              ",  activated :" + act.__str__() +
              ",  not activated :" + not_act.__str__())
    list = []
    k = 0
    for n, d in NETWORK.nodes():
        if ((not_act and d['a'] == 0) or (act and d['a'] > 0)):
            list.append(n)
            k += 1
        else:
            pass
        if len(list) > 500:
            expand_method(words=list, to_existing=to_existing, from_existing=from_existing)
            list = []
        if k > max:
            break
    if len(list) > 0:
        expand_method(words=list, to_existing=to_existing, from_existing=from_existing)
    print_log("Looked at " + k.__str__() + " nodes.")

####################################################


def load_dir(name):
    """
    @brief Loads a directory : network, success list, black list.

    For example, load_dir("rc") will attempt to load :
    * rc/rc_nodes.jsons
    * rc/rc_edges.jsons
    * rc/rc_black_list.jsons
    * rc/rc_success_list.jsons
    """
    print_log("Loading network " + name + "...")
    NETWORK.load_from_JSON_stream(nodes_files=[name + "/" + name + "_nodes.jsons"],
                                  edges_files=[name + "/" + name + "_edges.jsons"])
    for n in js.read_json_stream(name + "/" + name + "_black_list.jsons"):
        add_list(BL, n[0])
    for n in js.read_json_stream(name + "/" + name + "_success_list.jsons"):
        add_list(SL, n[0])


def save_dir(name):
    """
    @brief Saves network, success list and black list.
    """
    print_log("Saving to network " + name + "...")
    if not os.path.isdir(name):
        os.makedirs(name)
    NETWORK.save_to_JSON_stream(name + "/" + name)
    js.write_json_stream(list(BL), name + "/" + name + "_black_list.jsons")
    js.write_json_stream(list(SL), name + "/" + name + "_success_list.jsons")


def print_network_status():
    """
    Prints information on the network in the log file (if not None).
    """
    q = 0
    for n in NETWORK.nodes():
        if NETWORK[n[0]]['a'] > 0:
            q += 1
    print_log("Current network has %i nodes and %i edges." % (len(NETWORK.nodes()), len(NETWORK.edges())))
    print_log("%i nodes are activated (thus will be kept)." % q)
    print_log("Current black list has %i entries" % (len(BL)))
    print_log("Current success list has %i entries\n\n" % (len(SL)))


def creation_demo(namesfile, conceptsfile):
    rcdir = "../demo_rc/"
    if not os.path.isdir(rcdir):
        os.makedirs(rcdir)
    LOG_FILE = open(rcdir + "log.txt", 'a')
    print_network_status()
    use_method_on_file(DATA_DIR + namesfile, expand_names, max=1000, to_existing=False, from_existing=False)
    print_network_status()
    use_method_on_file(DATA_DIR + conceptsfile, expand_lookup, max=1000, to_existing=False, from_existing=False)
    print_network_status()
    use_method_on_network(expand_edges, max=10000, to_existing=False, from_existing=True, not_act=True, act=False)
    print_network_status()
    use_method_on_network(expand_edges, max=30000, to_existing=False, from_existing=False, not_act_only=True)
    print_network_status()
    clear_ic(limit=100000)
    clear_act(limit=100000)
    deactivate_nodes(limit=100000)
    print_network_status()
    save_dir(rcdir)
    LOG_FILE.close()
