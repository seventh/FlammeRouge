#!/usr/bin/python3

"""Générateur de l'ensemble des circuits possibles

Se base sur la sortie de gen_circuit.py, qui fournit les tracés
"""

import itertools
import json
import sys


def code(tronçon, entrée):
    retour = ""
    codes = {-1: "↓", 0: "→", 1: "↑"}
    for nom_case in tronçon:
        if nom_case == "arrivée":
            code = "A"
        elif nom_case == "départ":
            code = "D"
        else:
            pente = entrée["cases"][nom_case]["pente"]
            code = codes[pente]
        retour += code
    return retour


def dénombrer_variantes(chemin, type):
    """Identifie les combinaisons différentes de tuiles d'un même type.

    En cas de doublon, l'ordre alphabétique est toujours privilégié
    """
    with open(chemin, "rt") as entrée:
        parcours = json.load(entrée)

    tronçons = dict()
    for nom, tronçon in parcours["tronçons"].items():
        # Le tronçon est-il du type requis ?
        if parcours["cases"][tronçon[0]]["angle"] == type:
            tronçons[nom] = code(tronçon, parcours)

    signatures = dict()

    if type != 0:
        for p in itertools.permutations(sorted(tronçons, key=str.lower)):
            signature = ""
            for nom in p:
                signature += tronçons[nom]
            if signature not in signatures:
                signatures[signature] = "".join(p)
    else:
        # Il reste deux restrictions spécifiques au type «0» :
        #  - quand on choisit une face, on ne peut poser l'autre (et oui !)
        #  - on commence par un départ et on termine par une arrivée (et oui !)
        groupes = dict()
        départs = list()
        arrivées = list()
        autres = list()
        for k in tronçons:
            clef = k.lower()
            groupes.setdefault(clef, list()).append(k)
            if parcours["tronçons"][k][0] == "départ":
                départs.append(k)
            elif parcours["tronçons"][k][-1] == "arrivée":
                arrivées.append(k)
            else:
                autres.append(k)
        for f_début in itertools.permutations(*[groupes[g] for g in départs if g.islower()]):
            for p_début in itertools.product(f_début):
                for f_milieu in itertools.product(*[groupes[g] for g in autres if g.islower()]):
                    for p_milieu in itertools.permutations(f_milieu):
                        for f_fin in itertools.product(*[groupes[g] for g in arrivées if g.islower()]):
                            for p_fin in itertools.permutations(f_fin):
                                p = "".join(p_début + p_milieu + p_fin)
                                signature = ""
                                for nom in p:
                                    signature += tronçons[nom]
                                if (signature not in signatures or
                                        signatures[signature] > p):
                                    signatures[signature] = p

    for signature in sorted(signatures, key=lambda s: signatures[s].lower()):
        print(signature, signatures[signature])


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        dénombrer_variantes("../courses.json", int(sys.argv[1]))
