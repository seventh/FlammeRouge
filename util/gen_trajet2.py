#!/usr/bin/python3

"""Générateur de l'ensemble des tracés possibles
"""

import copy

import Polygon

import trajet

NB_OCTETS = 6
TRAJETS = "trajets.bin"


class Magot:

    def __init__(self):
        self._comptes = {0: 7, 1: 6, 2: 6}

    def __iter__(self):
        types = sorted(self._comptes.keys() +
                       [-famille for famille in self._comptes if famille != 0])
        for type in types:
            yield type

    def poser(self, type):
        retour = copy.deepcopy(self)

        famille = abs(type)
        if retour._comptes[famille] == 1:
            del retour._comptes[famille]
        else:
            retour._comptes[famille] -= 1

        return retour


class Strate:

    def __init__(self):
        self.jalon = [0, 0]
        self.angle = 0
        self.forme = Polygon([])
        self.magot = Magot()

    def poser(self, type):
        retour = copy.deepcopy(self)

        return retour


class Contexte:

    def __init__(self, trajet):
        self._strates = [Strate()]


def reprendre():
    """Analyse le fichier de sauvegarde pour déterminer le point de reprise
    de la recherche
    """
    retour = None

    code = None
    try:
        with open(TRAJETS, "rb") as trajets:
            # Alignement sur le dernier code complet
            # Un code fait NB_OCTETS octets
            trajets.seek(0, 2)
            taille = trajets.tell()
            trajets.seek(-NB_OCTETS - taille % NB_OCTETS, 1)
            données = trajets.read(NB_OCTETS)
            code = int.from_bytes(données, "big", signed=True)
            retour = trajet.décoder(code)
    except FileNotFoundError:
        code = 0

    return retour


if __name__ == "__main__":
    contexte = reprendre()
