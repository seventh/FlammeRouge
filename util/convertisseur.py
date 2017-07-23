#!/usr/bin/env python3

"""Convertisseur d'un fichier de recherche du format TRAJET1 à TRAJET3

Un fichier TRAJET1 se décompose ainsi :
  - succession d'entiers sur 6 octets, gros-boutisme

Un fichier TRAJET3 se décompose ainsi :
  - un entier sur 5 octets, gros-boutisme
  - une succession de bits
"""

import trajet
import trajet2


ENTRÉE = "trajets.bin"
SORTIE = "trajets3.bin"


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


if __name__ == "__main__":
    E = Trajet1(ENTRÉE)
    S = Trajet3(SORTIE)

    while True:
        t = E.lit()
        if t is None:
            break
        S.met(t)
    del S
