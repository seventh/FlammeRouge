#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-

"""Supprime un octet inutile du fichier de trajets
"""

import logging

ENTRÉE = "trajets-c.bin"


def vérifier(entrée):
    """Vrai ssi le 7ème octet de chaque enregistrement de 10 octets vaut 0
    """
    retour = True
    with open(entrée, "rb") as flux:
        flux.seek(0, 2)
        taille = flux.tell()
        if taille % 10 != 0:
            logging.error("Taille incorrecte : {} octets".format(taille))
            retour = False
        else:
            logging.info("Taille correcte : {} octets".format(taille))
        flux.seek(0, 0)

        n = 0
        while retour:
            données = flux.read(10)
            if len(données) == 0:
                logging.info("Fin de vérification")
                break
            if données[6] != 0:
                logging.error("Octet utile ! {}".format(flux.tell() - 10))
                retour = False
            n += 1
            if n % 10000000 == 0:
                logging.info(
                    "{}M enregistrements vérifiés".format(n // 1000000))
    return retour


def modifier(entrée):
    """Supprime le 7ème octet de chaque enregistrement de 10 octets
    """
    é = 6
    l = 7
    n = 0
    # il manque volontairement un '+' le temps de la mise-au-point
    with open(entrée, "rb") as flux:
        flux.seek(0, 2)
        taille = flux.tell() - 3

        # Partie conservée : fin de l'enregistrement N, début de
        # l'enregistrement N+1
        while l < taille:
            flux.seek(l, 0)
            données = flux.read(9)
            l += 10

            flux.seek(é, 0)
            flux.write(données)
            é += 9

            n += 1
            if n % 1000000 == 0:
                logging.info(
                    "{}M enregistrements traités".format(n // 1000000))

        # Fin du dernier enregistrement
        flux.seek(l, 0)
        données = flux.read(3)

        flux.seek(é, 0)
        flux.write(données)
        é += 3

        # Troncature
        flux.truncate(é)


if __name__ == "__main__":
    logging.basicConfig(datefmt="%d/%m %Hh%M",
                        format="%(asctime)s | %(message)s",
                        level=logging.INFO)

    if vérifier(ENTRÉE):
        modifier(ENTRÉE)
