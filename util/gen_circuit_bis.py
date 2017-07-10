#!/usr/bin/python3

"""Générateur de l'ensemble des circuits possibles

Se base sur la sortie de gen_circuit.py, qui fournit les tracés
"""

import itertools
import json


def code(tronçon, entrée):
    retour = ""
    codes = {-1: "↓", 0: "→", 1: "↑"}
    for nom_case in tronçon:
        pente = entrée["cases"][nom_case]["pente"]
        retour += codes[pente]
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

    # Il reste deux restrictions spécifiques au type «0» :
    #  - quand on choisit une face, on ne peut poser l'autre (et oui !)
    #  - on commence par A/a et on termine par U/u.
    signatures = dict()

    print(tronçons.keys())
    for p in itertools.permutations(sorted(tronçons, key=str.lower)):
        signature = ""
        for nom in p:
            signature += tronçons[nom]
        if signature not in signatures:
            signatures[signature] = p

    for signature, suite in signatures.items():
        print(signature, suite)


if __name__ == "__main__":
    dénombrer_variantes("../courses.json", 2)
