#!/usr/bin/python3

"""Générateur de l'ensemble des tracés possibles
"""

import copy
import json

import Polygon

import agent
import trajet

TRAJETS = "trajets2.bin"


class Magot:

    def __init__(self):
        self._comptes = {0: 7, 1: 6, 2: 6}

    def __iter__(self):
        types = sorted(list(self._comptes.keys()) +
                       [-famille for famille in self._comptes if famille != 0],
                       reverse=True)
        for type in types:
            yield type

    def poser(self, type):
        retour = copy.deepcopy(self)

        famille = abs(type)
        if retour._comptes[famille] == 1:
            del retour._comptes[famille]
        else:
            retour._comptes[famille] -= 1

        return retour


class ChargeurDeFormes(type):

    def __new__(cls, name, parents, dct):
        if dct.get("PIÈCES", None) is None:
            with open("formes.json") as entrée:
                formes = json.load(entrée)
            pièces = dict()
            for t, angles in formes.items():
                pièces[int(t)] = dict()
                for angle, sommets in angles.items():
                    pièces[int(t)][int(angle)] = sommets
            dct["PIÈCES"] = pièces
                        
        return type.__new__(cls, name, parents, dct)


class Pièce(metaclass=ChargeurDeFormes):

    # Initialisé par «ChargeurDeFormes»
    PIÈCES = None
    
    def __init__(self, forme, jalon, angle):
        self.forme = forme
        self.jalon = jalon
        self.angle = angle

    @staticmethod
    def neuve(type, angle, écart):
        """Fournit la Pièce de caractéristiques correspondantes
        """
        transfo = angle // 2
        f = lambda v: [v[0], v[1]]
        if transfo == 1:
            f = lambda v: [-v[1], v[0]]
        elif transfo == 2:
            f = lambda v: [-v[0], -v[1]]
        elif transfo == 3:
            f = lambda v: [v[1], -v[0]]
        patron = Pièce.PIÈCES[type][angle % 2]
        sommets = list(
            map(lambda v: [v[0] + écart[0], v[1] + écart[1]], map(f, patron)))
        forme = Polygon.Polygon(sommets)

        retour = Pièce(forme, sommets[0], (angle + type) % 8)
        return retour


class Strate:

    def __init__(self):
        self.angle = None
        self.jalon = None
        self.forme = None
        self.magot = None
        self.pièce = None
        self.voies = None

    @staticmethod
    def départ():
        retour = Strate()
        départ = Pièce.neuve(0, 0, [0, 0])
        retour.angle = départ.angle
        retour.jalon = départ.jalon
        retour.forme = départ.forme
        retour.magot = Magot()
        retour.pièce = 0
        retour.voies = list(retour.magot)
        return retour

    @staticmethod
    def arrivée(strate):
        retour = None
        arrivée = Pièce.neuve(0, strate.angle, strate.jalon)
        croisement = strate.forme & arrivée.forme
        if not croisement:
            retour = Strate()
            retour.angle = arrivée.angle
            retour.jalon = arrivée.jalon
            retour.forme = strate.forme | arrivée.forme
            retour.magot = dict()
            retour.pièce = 0
            retour.voies = list()
        return retour

    def __str__(self):
        retour = str(self.__dict__)
        return retour

    def poser(self):
        retour = None
        type = None
        while len(self.voies) != 0:
            type = self.voies.pop()
            pièce = Pièce.neuve(type, self.angle, self.jalon)
            croisement = self.forme & pièce.forme
            if not croisement:
                retour = Strate()
                retour.angle = pièce.angle
                retour.jalon = pièce.jalon
                retour.forme = self.forme | pièce.forme
                retour.magot = self.magot.poser(type)
                retour.pièce = type
                retour.voies = list(retour.magot)
                break
        return retour


class Contexte:

    def __init__(self):
        self._strates = None

    @staticmethod
    def reprendre(trajet):
        retour = Contexte()
        # Pose de la première tuile
        retour._strates = [Strate.départ()]
        # Pose des suivantes SAUF la dernière
        for i in range(1, len(trajet) - 1):
            while True:
                strate = retour._strates[-1].poser()
                if strate.pièce == trajet[i]:
                    retour._strates.append(strate)
                    break
        # Pose de la dernière tuile
        retour._strates.append(Strate.arrivée(retour._strates[-1]))

        return retour

    @staticmethod
    def premier():
        retour = Contexte()
        # Pose de la première tuile
        retour._strates = [Strate.départ()]
        # Pose de deux «tuiles» parfaitement fictives, la preuve :
        retour._strates.append(42)
        retour._strates.append(42)
        # On avance jusqu'au premier contexte viable
        retour.prochain()
        return retour

    def __str__(self):
        retour = str(self.trajet())
        return retour

    def prochain(self):
        retour = True
        # Suppression de l'arrivée
        self._strates.pop()
        while True:
            # Suppression de la dernière strate variable
            self._strates.pop()
            while 0 < len(self._strates) < 20:
                strate = self._strates[-1].poser()
                if strate is None:
                    self._strates.pop()
                else:
                    self._strates.append(strate)
            if len(self._strates) == 0:
                retour = False
            else:
                # Ajout de l'arrivée si possible
                strate = Strate.arrivée(self._strates[-1])
                if strate is not None:
                    self._strates.append(strate)
                    break
        return retour

    def trajet(self):
        retour = [s.pièce for s in self._strates]
        return retour


def reprendre():
    """Analyse le fichier de sauvegarde pour déterminer le point de reprise
    de la recherche
    """
    retour = None

    try:
        with open(TRAJETS, "rb") as trajets:
            lecteur = agent.Lecteur(trajets, trajet.NB_BITS)
            code = lecteur.dernier()
            t = trajet.décoder(code)
            retour = Contexte.reprendre(t)
    except FileNotFoundError:
        retour = Contexte.premier()

    return retour


if __name__ == "__main__":
    contexte = reprendre()
    with open(TRAJETS, "ab") as sortie:
        nb = 4 * sortie.tell() // 19
        print("{} | {}".format(nb, contexte.trajet()))
        auteur = agent.Metteur(sortie, trajet.NB_BITS)
        while contexte.prochain():
            t = contexte.trajet()
            code = trajet.coder(t)
            auteur.met(code)
            nb += 1
            if nb % 100000 == 0:
                print("{:.1f}M | {}".format(nb / 1000000, t))
