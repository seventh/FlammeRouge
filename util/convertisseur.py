#!/usr/bin/env python3

"""Convertisseur d'un fichier de recherche du format TRAJET1 à TRAJET4

Un fichier TRAJET1 se décompose ainsi :
  - succession d'entiers sur 6 octets, gros-boutisme

Un fichier TRAJET3 se décompose ainsi :
  - un entier sur 5 octets, gros-boutisme
  - une succession de bits

Un fichier TRAJET4 se décompose ainsi :
  - une suite de bits, chaque bit représentant l'état "le trajet est
    constructible" du trajet de code «trajet2» correspondant.
"""

import trajet
import trajet2


ENTRÉE = "trajets.bin"
SORTIE = "trajets4.bin"


class Trajet1:
    """Les données d'un fichier au format TRAJET1 sont au format «trajet»
    """

    def __init__(self, chemin):
        self._flux = open(chemin, "rb")

    def lit(self):
        retour = None
        données = self._flux.read(6)
        if (données is not None and len(données) == 6):
            valeur = int.from_bytes(données, "big", signed=True)
            retour = trajet.décoder(valeur)
        return retour


class Trajet3:
    """Les données d'un fichier au format TRAJET3 sont au format «trajet2»
    """

    def __init__(self, chemin):
        self._chemin = chemin
        self._octets = list()
        self._dernier = 0

    def __del__(self):
        with open(self._chemin, "wb") as sortie:
            données = self._dernier.to_bytes(5, "big")
            sortie.write(données)
            for octet in self._octets:
                données = octet.to_bytes(1, "big")
                sortie.write(données)

    def met(self, t):
        valeur = trajet2.coder(t)
        self._dernier = valeur

        print(valeur)
        octet, bit = divmod(valeur, 8)
        print(octet)
        if len(self._octets) <= octet:
            self._octets.extend((octet - len(self._octets) + 1) * [0])
        self._octets[octet] |= 1 << (7 - bit)


class Trajet4:

    def __init__(self, chemin):
        try:
            self._flux = open(chemin, "r+b")
        except FileNotFoundError:
            self._flux = open(chemin, "x+b")
        self._flux.truncate((trajet2.CODE_GARDE + 7) // 8)

    def __del__(self):
        self._flux.close()
        self._flux = None

    def met(self, t):
        code = trajet2.coder(t)
        décalage, bit = divmod(code, 8)
        self._flux.seek(décalage, 0)
        octet = self._flux.read(1)
        valeur = int.from_bytes(octet, "little")
        valeur |= 1 << bit
        self._flux.seek(-1, 1)
        octet = valeur.to_bytes(1, "little")
        self._flux.write(octet)


if __name__ == "__main__":
    E = Trajet1(ENTRÉE)
    S = Trajet4(SORTIE)

    while True:
        t = E.lit()
        if t is None:
            break
        S.met(t)
    del S
