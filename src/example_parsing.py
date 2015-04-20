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

from abstracter.concepts_network import ConceptNetwork
from abstracter.util import json_stream as js

NETWORK = ConceptNetwork()
edges = [["wayne_rooney", "athlete", {"w": 39, "r": "IsA"}],
         ["wayne_rooney", "soccer_player", {"w": 39, "r": "IsA"}],
         ["soccer_player", "athlete", {"w": 47, "r": "IsA"}],
         ["soccer_player", "win_match", {"w": 47, "r": "CapableOf"}],
         ["soccer_player", "at_soccer_game", {"w": 47, "r": "AtLocation"}],
         ["athlete", "sport_event", {"w": 77, "r": "AtLocation"}],
         ["athlete", "play_sport", {"w": 90, "r": "CapableOf"}],
         ["sport_event", "television", {"w": 60, "r": "AtLocation"}]]

for e in edges:
    NETWORK.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])

NETWORK.pretty_draw()
