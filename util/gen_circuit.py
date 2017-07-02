#!/usr/bin/python3

"""Générateur de l'ensemble des tracés possibles
"""

import copy
import json
import struct

import Polygon


def dénombrer_formes(chemin):
    """Dénombre les formes à partir du fichier des courses
    """
    comptes = dict()

    with open(chemin, "rt") as entrée:
        parcours = json.load(entrée)

    for nom, tronçon in parcours["tronçons"].items():
        if nom.isupper():
            angle = abs(parcours["cases"][tronçon[0]]["angle"])
            if angle not in comptes:
                comptes[angle] = 0
            comptes[angle] += 1

    # 0 → droit (6 cases)
    # 1 → huitième de tour (2 cases)
    # 2 → quart de tour (2 cases)
    retour = Magot(comptes)
    return retour


class Pièce:

    def __init__(self, forme, jalon, angle):
        self.forme = forme
        self.jalon = jalon
        self.angle = angle


# Les mesures sont en millimètres
# Le premier sommet est le prochain jalon (64, 45, 135)
PIÈCES = {
    # quart-droite
    -2: {
        0: [[16, -16], [15, -12], [14, -8], [11, -5], [8, -2], [4, -1], [0, 0],
            [0, 64], [9, 63], [18, 62], [26, 60], [35, 56], [43, 52], [50, 47],
            [57, 41], [63, 34], [68, 27], [72, 19], [76, 10], [78, 2],
            [79, -7], [80, -16]],
        1: [[23, 0], [68, 45], [61, 51], [54, 56], [46, 60], [37, 64],
            [29, 66], [20, 67], [11, 68], [2, 67], [-7, 66], [-15, 64],
            [-24, 60], [58, 56], [51, 51], [-45, 45], [0, 0], [3, 3], [7, 4],
            [11, 5], [15, 4], [19, 3]],
    },
    # huitième-droite
    -1: {
        0: [[43, -17], [25, 0], [0, 0], [0, 64], [51, 64], [88, 28]],
        1: [[43, 17], [43, 81], [-8, 81], [-45, 45], [0, 0], [18, 17]],
    },
    # rectiligne
    0: {
        0: [[191, 0], [191, 64], [0, 64], [0, 0]],
        1: [[135, 135], [90, 180], [-45, 45], [0, 0]],
    },
    # huitième-gauche
    1: {
        0: [[88, 36], [43, 81], [25, 64], [0, 64], [0, 0], [51, 0]],
        1: [[36, 88], [-28, 88], [-28, 63], [-45, 45], [0, 0], [36, 36]],
    },
    # quart-gauche
    2: {
        0: [[80, 80], [16, 80], [15, 76], [14, 72], [11, 69], [8, 66], [4, 65],
            [0, 64], [0, 0], [9, 1], [18, 2], [26, 4], [35, 8], [43, 12],
            [50, 17], [57, 23], [63, 30], [68, 37], [72, 45], [76, 54],
            [78, 62], [79, 71]],
        1: [[0, 113], [-45, 68], [-42, 65], [-41, 61], [-40, 57], [-41, 53],
            [-42, 49], [-45, 45], [0, 0], [6, 7], [11, 14], [15, 22], [19, 31],
            [21, 39], [22, 48], [23, 57], [22, 66], [21, 75], [19, 83],
            [15, 92], [11, 10], [6, 17]],
    },
}


def pièce(type, angle, écart):
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
    patron = PIÈCES[type][angle % 2]
    sommets = list(
        map(lambda v: [v[0] + écart[0], v[1] + écart[1]], map(f, patron)))
    forme = Polygon.Polygon(sommets)

    retour = Pièce(forme, sommets[0], (angle + type) % 8)
    return retour


class Magot:
    """Inventaire de pièces restant à assembler
    """

    def __init__(self, comptes):
        self._comptes = comptes

    def est_vide(self):
        """Vrai ssi il n'y a plus aucune pièce
        """
        retour = (len(self._comptes) == 0)
        return retour

    def types(self):
        """Itérateur des types de pièces pouvant encore être assemblées
        """
        retour = list()
        for type in self._comptes:
            if type != 0:
                retour.append(type)
                retour.append(-type)
            elif not (len(self._comptes) > 1 and self._comptes[0] == 1):
                retour.append(type)
        yield from sorted(retour)

    def prélever(self, type):
        clef = abs(type)
        if self._comptes[clef] == 1:
            del self._comptes[clef]
        else:
            self._comptes[clef] -= 1


class Tracé:

    def __init__(self, magot):
        self._jalon = [0, 0]
        self._angle = 0  # en huitième de tour
        self._tuiles = Polygon.Polygon()
        self._chemin = list()
        self._magot = magot  # tuiles restantes

    def __iter__(self):
        if self._tuiles.nPoints() == 0:
            # On commence forcément par une tuile droite
            retour = copy.deepcopy(self)
            retour.poser(0)
            yield retour
        else:
            for type in self._magot.types():
                retour = copy.deepcopy(self)
                if retour.poser(type):
                    yield retour

    def __str__(self):
        retour = str(self._chemin)
        return retour

    def poser(self, type):
        retour = True
        p = pièce(type, self._angle, self._jalon)
        croisement = p.forme & self._tuiles
        if croisement:
            retour = False
        else:
            self._magot.prélever(type)
            self._tuiles = p.forme | self._tuiles
            self._chemin.append(type)
            self._jalon = p.jalon
            self._angle = p.angle
        return retour


def rechercher(tracé, sortie):
    if tracé._magot.est_vide():
        valeur = 0
        for i in tracé._chemin:
            valeur = (valeur << 3) + (i & 0x07)
        données = struct.pack(">Q", valeur)
        sortie.write(données)
    else:
        for t in tracé:
            rechercher(t, sortie)


if __name__ == "__main__":
    magot = dénombrer_formes("../courses.json")
    t = Tracé(magot)
    sortie = open("formes.bin", "wb")
    rechercher(t, sortie)
