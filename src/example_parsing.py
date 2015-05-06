"""
I intend to create very small examples of Rc (visual ones)
by parsing a small .jsons file, containing edges from a real RC.
"""

from abstracter.concepts_network import ConceptNetwork
from abstracter.util import json_stream as js


NETWORK = ConceptNetwork()


def load_edges(filename):
    for e in js.read_json_stream(filename):
        NETWORK.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])


def plot():
    NETWORK.draw(filename="example.eps")

#load_edges("extrait_rc3_edges.jsons")
#plot()
#for e in NETWORK.edges():
#    print(e)
#NETWORK.pretty_draw()

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

edges2 = [["total_football", "computer_game", {"r": "IsA", "w": 30}],
["total_football", "video_game", {"r": "IsA", "w": 17}],
["total_football", "software", {"r": "IsA", "w": 17}],
["software", "process_information", {"r": "UsedFor", "w": 60}],
["software", "code", {"r": "IsA", "w": 47}],
["software", "compatible", {"r": "HasProperty", "w": 47}]
]

edges3 = [["sevilla_fc", "soccer_club", {"r": "IsA", "w": 17}],
["sevilla_fc", "football_team", {"r": "IsA", "w": 29}],
["sevilla_fc", "sport_team", {"r": "IsA", "w": 17}],
["olympique_lyonnais", "soccer_club", {"r": "IsA", "w": 17}],
["olympique_lyonnais", "sport_team", {"r": "IsA", "w": 17}],
["sport_team", "team", {"r": "IsA", "w": 30}],
["football_team", "team", {"r": "IsA", "w": 47}],
["team", "group_of_person", {"r": "IsA", "w": 47}],
["team", "soccer_game", {"r": "AtLocation", "w": 77}]
]

for e in edges3:
    NETWORK.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])

NETWORK.pretty_draw()
