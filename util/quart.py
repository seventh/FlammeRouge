#!/usr/bin/python3

"""Coordonnées d'un quart de cercle
"""

import math
import sys


def points(rayon, précision):
    # Recherche du nombre optimal de segments
    cos = 1.0 - 5 * 10 ** (-précision - 1) / rayon
    angle = math.acos(cos)
    nb = math.floor(math.pi / (2 * angle))

    # Génération des points
    for i in range(nb + 1):
        angle = (i * math.pi) / (2 * nb)
        cos = math.cos(angle)
        sin = math.sin(angle)

        x = round(rayon * sin, précision)
        y = round(rayon * (1 - cos), précision)
        yield (x, y)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        RAYON = float(sys.argv[1])
        for p in points(RAYON, 1):
            print(p)
