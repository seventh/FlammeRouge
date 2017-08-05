#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Détermine le trajet le plus compact
"""

import math

import Polygon

import agent
import trajet
import gen_trajet

TRAJETS = "trajets-python.bin"


def aire(t):
    """Détermine l'aire du rectangle englobant
    """
    p = gen_trajet.Pièce(Polygon.Polygon(), [0, 0], 0)
    for tuile in t:
        n = gen_trajet.Pièce.neuve(tuile, p.angle, p.jalon)
        p.forme.addContour(n.forme.contour(0))
        p.jalon = n.jalon
        p.angle = n.angle
    xm, xM, ym, yM = p.forme.boundingBox()
    retour = (xM - xm) * (yM - ym)

    # On tente également une rotation de 45°
    p.forme.rotate(math.pi / 4, 0, 0)
    xm, xM, ym, yM = p.forme.boundingBox()
    aire2 = (xM - xm) * (yM - ym)
    if aire2 < retour:
        retour = aire2
    return retour


def trouver():
    meilleur_t = None
    meilleur_s = None
    with open(TRAJETS, "rb") as entrée:
        a = agent.Lecteur(entrée, trajet.NB_BITS)
        while True:
            code = a.lit()
            if code is None:
                break
            t = trajet.décoder(code)
            s = aire(t)
            if (meilleur_t is None or
                    meilleur_s > s):
                meilleur_t = t
                meilleur_s = s
                print("{} → {}".format(s, t))


if __name__ == "__main__":
    trouver()
