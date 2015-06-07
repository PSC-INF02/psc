"""
@file network_propagation_example.py
@author PSC INF02

Exemple créé pour montrer la propagation
d'activation d'un un réseau de concepts.
Prévu pour la soutenance du PSC du 19 mai 2015.

exemple d'utilisation en ligne de commande :
entrer le nombre d'étapes souhaitées,
puis le taux d'activation minimal, puis les mots à activer
> python3 network_propagation_example.py 5 10 bedroom

@warning Placer le fichier dans le répertoire contenant abstracter pour
que les imports fonctionnent.
"""
from abstracter.concepts_network import *
import os
import sys


def num_activated_nodes(net, offset):
    """
    Renvoie le nombre de noeuds d'un RC dont l'activation
    est supérieure à un certain échelon.

    @param net Réseau considéré.
    @param offset Activation minimale.
    """
    k = 0
    for n, d in net.nodes():
        if d['a'] > offset:
            k += 1
    return k

if __name__ == "__main__":

    if not os.path.isdir("drawing_test/"):
        os.mkdir("drawing_test/")

    # Chargement du réseau pour effectuer les tests.
    cn = ConceptNetwork()
    print("Chargement...")
    cn.load("rc5")
    print("Chargement terminé.")

    # Création d'un réseau local pour affichage de celui-ci
    NETWORK = ConceptNetwork()
    numetapes = 5
    tauxminimal = 10

    # Ligne de commande
    if sys.argv[3:]:
        numetapes = int(sys.argv[1])
        tauxminimal = int(sys.argv[2])
        if tauxminimal > 100 or tauxminimal < 0 or numetapes < 0:
            print("Attention, possible entrée erronnée.")
        cn.activate(sys.argv[3:], 60)
    else:
        cn.activate(["wayne_rooney", "manchester_united_f.c."], 60)
        # cn.activate(["water"], 60)
    for i in range(numetapes):
        # Réinitialisation du réseau à chaque étape
        NETWORK = ConceptNetwork()
        print("Étape " + i.__str__() + " : " +
              num_activated_nodes(cn, tauxminimal).__str__() + " noeuds activés.")
        # Affichage des noeuds activés à un certain échelon
        for n in cn.get_activated_nodes(tauxminimal):
            NETWORK.add_node(n, ic=cn[n]['ic'], a=cn[n]['a'])
        for e in cn.get_activated_arcs(tauxminimal):
            NETWORK.add_edge(e[0], e[1], w=e[2]["w"], r=e[2]["r"])

        NETWORK.pretty_draw("drawing_test/" + i.__str__())
        cn.propagate()
