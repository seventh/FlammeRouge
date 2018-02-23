#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Analyse et compactage de la base initiale
"""

import math
import struct

import trajet
import trajet2

ENTRÉE = "trajets-c.bin"
SORTIE = "trajets2-python.bin"


def modifier(nom_fichier):
    """Ouvre un fichier binaire en lecture/écriture sans le purger.
    """
    try:
        retour = open(nom_fichier, "r+b")
    except FileNotFoundError:
        retour = open(nom_fichier, "x+b")

    return retour


def itérer_trajet(t):
    """Produit les quatre variations autour d'un meme trajet
    """
    yield t
    yield [-x for x in t]
    t.reverse()
    yield t
    yield [-x for x in t]


def analyser(entrée, sortie):
    fmt = ">9B"
    nb_octets = struct.calcsize(fmt)
    taille_min = float("inf")
    taille_max = 0

    avancement = 0
    with modifier(sortie) as binaire:
        with open(entrée, "rb") as flux:
            while True:
                tampon = flux.read(nb_octets)
                if len(tampon) < nb_octets:
                    break
                données = struct.unpack(fmt, tampon)

                code = 0
                for i in range(6):
                    code <<= 8
                    code += données[i]
                taille = 0
                for i in range(3):
                    taille <<= 8
                    taille += données[6 + i]

                avancement += 1
                if avancement % 1000000 == 0:
                    print("| {}M enregistrements lus".format(
                        avancement // 1000000))

                # Variation autour d'un seul trajet
                t = trajet.décoder(code)
                for t2 in itérer_trajet(t):
                    code = trajet2.coder(t2)

                    décalage, bit = divmod(code, 8)

                    binaire.seek(décalage, 0)
                    octet = int.from_bytes(binaire.read(1), "little")
                    octet |= 1 << bit
                    binaire.seek(décalage, 0)
                    binaire.write(octet.to_bytes(1, "little"))

                # Taille
                affichage = False
                if taille < taille_min:
                    affichage = True
                    taille_min = taille
                if taille > taille_max:
                    affichage = True
                    taille_max = taille
                if affichage:
                    print("min = {} | max = {} | stockage : {:.2f} bits".format(
                        taille_min, taille_max,
                        math.log(taille_max - taille_min + 1, 2)))


if __name__ == "__main__":
    analyser(ENTRÉE, SORTIE)
