#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Générateur de l'ensemble des circuits possibles pour un trajet donné
"""

import itertools
import json


def charger_profils(entrée):
    retour = list()

    codes = {-1: "↓", 0: "→", 1: "↑"}
    profils = dict()
    with open(entrée, "rt") as flux:
        courses = json.load(flux)

        for nom_tronçon in courses["tronçons"]:
            profil = str()
            for nom_case in courses["tronçons"][nom_tronçon]:
                if nom_case == "arrivée":
                    code = "A"
                elif nom_case == "départ":
                    code = "D"
                else:
                    pente = courses["cases"][nom_case]["pente"]
                    code = codes[pente]
                profil += code
            profils[nom_tronçon] = profil

    for clef in sorted(profils.keys()):
        if clef.islower():
            retour.append((profils[clef], profils[clef.upper()]))

    return retour


def compresser_signature(signature):
    """Applique un encodage RLE à la signature
    """
    retour = str()

    i = 0
    while i < len(signature):
        j = i + 1
        while (j < len(signature) and signature[i] == signature[j]):
            j += 1
        retour += "{}{:02}".format(signature[i], j - i)
        i = j
    return retour


def itérer(paires):
    sigs = set()

    for p in itertools.permutations(paires[1:-1]):
        for profil in itertools.product(paires[0], *p, paires[-1]):
            sig = "".join(profil)
            sig = compresser_signature(sig)

            if sig not in sigs:
                print(sig)
                sigs.add(sig)


if __name__ == "__main__":
    paires = charger_profils("../courses.json")
    itérer(paires)
