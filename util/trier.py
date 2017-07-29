#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ordonne tous les codes de trajet

Trop simpliste, ce programme mange avant tout TOUTE la mémoire
"""

import logging

import agent
import trajet


ENTRÉE = "trajets2.bin"
SORTIE = "trajets2-trié.bin"


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s | %(message)s",
                        datefmt="%d/%m %Hh%M",
                        level=logging.INFO)

    codes = list()
    dernier = None

    logging.info("Lecture des codes")
    with open(ENTRÉE, "r+b") as entrée:
        l = agent.Lecteur(entrée, trajet.NB_BITS)
        while True:
            code = l.lit()
            if code is None:
                break
            elif dernier is not None:
                codes.append(dernier)
            dernier = code

    logging.info("Tri des valeurs")
    codes.sort()

    logging.info("Écriture des codes")
    with open(SORTIE, "w+b") as sortie:
        m = agent.Metteur(sortie, trajet.NB_BITS)
        for code in codes:
            m.met(code)
        m.met(dernier)
