#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import turtle


def charger(nom):
    retour = None
    with open(nom, "rt") as entrée:
        retour = json.load(entrée)
    return retour


def dessiner(type, angle, forme):
    # Nettoyage
    turtle.clearscreen()
    turtle.title("Forme type {}, angle {}".format(type, angle))
    # Dessin
    turtle.penup()
    turtle.setposition(*forme[0])
    turtle.pendown()
    for x, y in forme[1:]:
        turtle.setposition(x, y)
    turtle.setposition(*forme[0])
    turtle.exitonclick()


if __name__ == "__main__":
    formes = charger("formes.json")
    for type, angles in formes.items():
        for angle, forme in angles.items():
            dessiner(type, angle, forme)
