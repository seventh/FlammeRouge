#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Analyse et compactage de la base initiale
"""

import math
import struct

ENTRÉE = "trajets-c.bin"
SORTIE = "trajets-python.bin"


def dimensionner(entrée):
    fmt = ">6b1I"
    nb_octets = struct.calcsize(fmt)
    taille_min = float("inf")
    taille_max = 0

    with open(entrée, "rb") as flux:
        while True:
            tampon = flux.read(nb_octets)
            if len(tampon) < nb_octets:
                break
            données = struct.unpack(fmt, tampon)
            taille = données[6]
            if not (taille_min <= taille <= taille_max):
                if taille < taille_min:
                    taille_min = taille
                if taille > taille_max:
                    taille_max = taille
                print("min = {} | max = {} | stockage : {:.2f} bits".format(taille_min, taille_max, math.log(taille_max - taille_min + 1, 2)))

if __name__ == "__main__":
    dimensionner(ENTRÉE)
