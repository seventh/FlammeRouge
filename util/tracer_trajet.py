#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Trace le trajet

Exemple : ./tracer_trajet.py  -2 -2 0 0 1 1 0 0 -2 1 -1 0 -1 2 1 0 0 2 2 0
"""

import json
import sys
import turtle

import gen_trajet


def charger(nom):
    retour = None
    with open(nom, "rt") as entrée:
        retour = json.load(entrée)
    return retour


def zoom(x):
    return x / 4


def dessiner(polygone):
    # Dessin
    turtle.penup()
    turtle.setposition(map(zoom, polygone[0][0]))
    turtle.pendown()
    for i in range(1, len(polygone[0])):
        turtle.setposition(map(zoom, polygone[0][i]))
    turtle.setposition(map(zoom, polygone[0][0]))


if __name__ == "__main__":
    formes = charger("formes.json")

    # Initialisation
    turtle.setup()

    # Dessin de chaque tuile
    pos = [0, 0]
    angle = 0

    for tuile in sys.argv[1:]:
        pièce = gen_trajet.Pièce.neuve(int(tuile), angle, pos)
        dessiner(pièce.forme)
        pos = pièce.jalon
        angle = pièce.angle

    turtle.exitonclick()
