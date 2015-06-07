"""
@file network_generation_example.py

Uses functions defined in file abstracter.concepts_network.cn_generation
(check here for further information).
"""

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