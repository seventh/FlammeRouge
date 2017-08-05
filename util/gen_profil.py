#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Générateur de l'ensemble des circuits possibles pour un trajet donné
"""

import collections
import itertools
import json
import os
import sys


def profil(étape, courses):
    retour = str()

    for tronçon in étape:
        cases = courses["tronçons"][tronçon]
        retour += code(cases, courses)
    return retour


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


def dénombrer_variantes(parcours, type, card):
    """Identifie les combinaisons différentes de tuiles d'un même type.

    En cas de doublon, l'ordre alphabétique est toujours privilégié
    """
    codes = dict()
    tronçons = str()
    negs = dict()
    for nom, tronçon in parcours["tronçons"].items():
        # Le tronçon est-il du type requis ?
        angle = parcours["cases"][tronçon[0]]["angle"]
        if angle == type:
            tronçons += nom
            codes[nom] = code(tronçon, parcours)
        elif angle == -type:
            codes[nom] = code(tronçon, parcours)

    if card is None:
        card = len(tronçons)

    signatures = dict()

    def clef(chaîne):
        retour = (chaîne.lower(), chaîne.swapcase())
        return retour

    if type != 0:
        for c in itertools.combinations(tronçons, card):
            negs = set(tronçons)
            for k in c:
                negs.remove(k)
            negs = [k.swapcase() for k in negs]

            for p in itertools.permutations(c):
                signature = ""
                for nom in p:
                    signature += codes[nom]
                for q in itertools.permutations(negs):
                    signeg = ""
                    for nom in q:
                        signeg += codes[nom]
                    clé = (signature, signeg)
                    mem = "".join(p + q)
                    if (clé not in signatures or
                            clef(signatures[clé]) > clef(mem)):
                        signatures[clé] = mem
    else:
        # Il reste deux restrictions spécifiques au type «0» :
        #  - quand on choisit une face, on ne peut poser l'autre (et oui !)
        #  - on commence par un départ et on termine par une arrivée (et oui !)
        groupes = dict()
        départs = list()
        arrivées = list()
        autres = list()
        for k in tronçons:
            clé = k.lower()
            groupes.setdefault(clé, list()).append(k)
            if parcours["tronçons"][k][0] == "départ":
                départs.append(k)
            elif parcours["tronçons"][k][-1] == "arrivée":
                arrivées.append(k)
            else:
                autres.append(k)

        def combi(groupe):
            for f in itertools.product(*[groupes[g] for g in groupe if g.islower()]):
                for p in itertools.permutations(f):
                    yield p

        for t in itertools.product(combi(départs), combi(autres), combi(arrivées)):
            p = "".join(sum(t, ()))
            signature = ""
            for nom in p:
                signature += codes[nom]
            if (signature not in signatures or
                    clef(signatures[signature]) > clef(p)):
                signatures[signature] = p

    for signature in sorted(signatures, key=lambda s: clef(signatures[s])):
        yield signatures[signature]


def préparer_variantes(entrée, sortie):
    profils = dict()

    with open(entrée, "rt") as flux:
        courses = json.load(flux)

    if os.path.exists("profils.json"):
        with open(sortie, "rt") as flux:
            profils = json.load(flux)

        for clef1 in list(profils):
            for clef2 in list(profils[clef1]):
                profils[clef1][int(clef2)] = profils[clef1][clef2]
                del profils[clef1][clef2]
            profils[int(clef1)] = profils[clef1]
            del profils[clef1]
    else:
        profils[0] = {9: list(dénombrer_variantes(courses, 0, None))}
        profils[1] = dict()
        for i in range(6):
            profils[1][i] = list(dénombrer_variantes(courses, 1, i))
        profils[2] = dict()
        for i in range(6):
            profils[2][i] = list(dénombrer_variantes(courses, 2, i))

            with open(sortie, "wt") as flux:
                json.dump(profils, flux)

    return courses, profils


def iter_étape(trajet, courses, profils):
    nb1 = trajet.count(1)
    nb2 = trajet.count(2)

    for c0, c1, c2 in itertools.product(profils[0][9],
                                        profils[1][nb1],
                                        profils[2][nb2]):
        etape = str()
        p0 = 0
        p1 = 0
        m1 = nb1
        p2 = 0
        m2 = nb2
        for tuile in trajet:
            if tuile == -2:
                etape += c2[m2]
                m2 += 1
            elif tuile == -1:
                etape += c1[m1]
                m1 += 1
            elif tuile == 0:
                etape += c0[p0]
                p0 += 1
            elif tuile == 1:
                etape += c1[p1]
                p1 += 1
            elif tuile == 2:
                etape += c2[p2]
                p2 += 1

        k = profil(etape, courses)
        yield etape, k


if __name__ == "__main__":
    courses, profils = préparer_variantes("../courses.json", "profils.json")

    trajet = list()
    if len(sys.argv) == 22:
        for arg in sys.argv[1:]:
            if arg[-1] == ",":
                tuile = int(arg[:-1])
            else:
                tuile = int(arg)
            trajet.append(tuile)
        print(trajet)

        sigs = collections.defaultdict(int)

        for étape, sig in iter_étape(trajet, courses, profils):
            sigs[sig] += 1

        print(max(sigs.values()))
