#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Comparateur de performances de deux fonctions
"""

import logging
import random

from trajet import décoder

N = 100000


def dec2(code):
    """Transforme tout entier naturel inférieur à 5^19 en un trajet
    """
    retour = 21 * [0]
    for i in reversed(range(1, 20)):
        code, r = divmod(code, 5)
        retour[i] = r - 2
    return retour


def dec3(code):
    """Transforme tout entier naturel inférieur à 5^19 en un trajet
    """
    retour = 21 * [0]
    for i in range(19, 0, -1):
        code, r = divmod(code, 5)
        retour[i] = r - 2
    return retour


def mesurer(fonction, entrées):
    logging.info("Début de la mesure de {!r}".format(fonction.__name__))
    for e in entrées:
        fonction(e)
    logging.info("Fin de la mesure de {!r}".format(fonction.__name__))


def comparer(f1, f2, entrées):
    retour = True
    logging.info("Début de la comparaison")
    for e in entrées:
        v1 = f1(e)
        v2 = f2(e)
        if v1 != v2:
            logging.info("Échec de l'équivalence pour {}".format(e))
            retour = False
    logging.info("Fin de la comparaison : {}".format(retour))
    return retour


def tirer(taille):
    retour = list()
    len_retour = 0

    logging.info("Tirage des valeurs - Début")
    while len_retour < taille:
        valeur = random.randrange(5**19)
        if True or valeur not in retour:
            retour.append(valeur)
            len_retour += 1
    logging.info("Tirage des valeurs - Fin")

    return retour


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(message)s', datefmt='%X')
    valeurs = tirer(N)
    if comparer(dec2, dec3, valeurs):
        mesurer(dec2, valeurs)
        mesurer(dec3, valeurs)
