"""
I intend to create very small examples of Rc (visual ones)
by parsing a small .jsons file, containing edges from a real RC.
"""

import abstracter.conceptnet5_client.concurrent_api as ca
from abstracter.concepts_network import ConceptNetwork
from abstracter.util import json_stream as js
from abstracter.conceptnet5_client import api as cn5
import abstracter.freebase_client as fb
import re
from abstracter.conceptnet5_client.result import *
import os


NETWORK = ConceptNetwork()


def load_edges(filename):
    for e in js.read_json_stream(filename):
        NETWORK.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])


def plot():
    NETWORK.draw(filename="example.eps")

load_edges("extrait_rc3_edges.jsons")
#plot()
#for e in NETWORK.edges():
#    print(e)
NETWORK.pretty_draw()