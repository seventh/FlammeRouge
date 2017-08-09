"""Un trajet est une succession de 21 entiers entre -2 et 2 débutant et
 terminant par 0

Le codage vers un entier inférieur à 5^19 permet de stocker un trajet
sur seulement 6 octets.
"""

import itertools


NB_BITS = 48


def coder(trajet):
    """Transforme un trajet en un entier naturel inférieur à 5^19
    """
    retour = 0
    for tuile in trajet[1:-1]:
        retour *= 5
        retour += tuile + 2
    return retour


def décoder(code):
    """Transforme tout entier naturel inférieur à 5^19 en un trajet
    """
    retour = 21 * [0]
    for i in range(19, 0, -1):
        code, r = divmod(code, 5)
        retour[i] = r - 2
    return retour


def _choisir(liste, pos):
    """Extrait la liste dont les élements sont aux positions correspondantes
    """
    retour = [liste[p] for p in pos]

    return retour


def _compresser(liste, sélecteurs):
    acceptés = list()
    refusés = list()

    for l, s in zip(liste, sélecteurs):
        if s:
            acceptés.append(l)
        else:
            refusés.append(l)

    return acceptés, refusés


def _filtrer(liste, pos):
    """Liste dont les éléments aux positions correspondantes ont été filtrés
    """
    retour = list()

    k = 0
    for i in range(len(pos)):
        retour.extend(liste[k:pos[i]])
        k = pos[i] + 1
    retour.extend(liste[k:])

    return retour


def _construire(pos1d, pos1i, pos2d, pos2i):
    retour = 21 * [0]
    for i in pos1d:
        retour[i] = 1
    for i in pos1i:
        retour[i] = -1
    for i in pos2d:
        retour[i] = 2
    for i in pos2i:
        retour[i] = -2
    return retour


def gen():
    """Itérateur des différentes combinaisons de tuiles possibles

    Les trajets obtenus ne sont peut-être pas constructibles.
    """
    pos = list(range(1, 21))

    # Choix de la position des huitièmes de tour
    for c1 in itertools.combinations(range(len(pos)), 6):
        pos1 = _choisir(pos, c1)
        res = _filtrer(pos, c1)
        for c3 in itertools.product([False, True], repeat=len(pos1)):
            pos3, res3 = _compresser(pos1, c3)

            # Choix de la position des quarts de tour
            for c2 in itertools.combinations(range(len(res)), 6):
                pos2 = _choisir(res, c2)
                for c4 in itertools.product([False, True], repeat=len(pos2)):
                    pos4, res4 = _compresser(pos2, c4)

                    retour = _construire(pos3, res3, pos4, res4)
                    yield retour


if __name__ == "__main__":
    for trajet in gen():
        print(trajet)
