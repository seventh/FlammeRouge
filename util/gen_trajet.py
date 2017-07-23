#!/usr/bin/python3

"""Générateur de l'ensemble des tracés possibles
"""

import copy

import Polygon

import trajet

NB_OCTETS = 6
TRAJETS = "trajets.bin"


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
                [0, 64], [9, 63], [18, 62], [26, 60], [
                    35, 56], [43, 52], [50, 47],
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
            # Alignement sur le dernier code complet
            # Un code fait NB_OCTETS octets
            trajets.seek(0, 2)
            taille = trajets.tell()
            trajets.seek(-NB_OCTETS - taille % NB_OCTETS, 1)
            données = trajets.read(NB_OCTETS)
            code = int.from_bytes(données, "big", signed=True)
            t = trajet.décoder(code)
            retour = Contexte.reprendre(t)
    except FileNotFoundError:
        retour = Contexte.premier()

    return retour


if __name__ == "__main__":
    contexte = reprendre()
    with open(TRAJETS, "ab") as sortie:
        nb = sortie.tell() // 6
        print("{} | {}".format(nb, contexte.trajet()))
        while contexte.prochain():
            t = contexte.trajet()
            code = trajet.coder(t)
            données = code.to_bytes(6, "big")
            sortie.write(données)
            nb += 1
            if nb % 100000 == 0:
                print("{:.1f}M | {}".format(nb / 1000000, t))
