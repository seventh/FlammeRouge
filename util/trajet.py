"""Un trajet est une succession de 21 entiers entre -2 et 2 débutant et
 terminant par 0

Le codage vers un entier inférieur à 5^19 permet de stocker un trajet
sur seulement 6 octets.
"""

import itertools


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
    retour = [0]
    while len(retour) < 20:
        code, r = divmod(code, 5)
        retour.append(r - 2)
    retour.append(0)
    retour.reverse()
    return retour


def _choisir(liste, pos):
    """Extrait la liste dont les élements sont aux positions correspondantes
    """
    retour = [liste[p] for p in pos]

    return retour


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
    """
    pos = list(range(1, 21))
    # Choix de la position des huitièmes de tour
    for c1 in itertools.combinations(range(len(pos)), 6):
        pos1 = _choisir(pos, c1)
        res1 = _filtrer(pos, c1)
        # Choix de la position des quarts de tour
        for c2 in itertools.combinations(range(len(res1)), 6):
            pos2 = _choisir(res1, c2)
            # res2 = _filtrer(res1, c2)
            # Choix de la position des huitièmes de tour à gauche
            for n1 in range(len(pos1) + 1):
                for c3 in itertools.combinations(range(len(pos1)), n1):
                    pos3 = _choisir(pos1, c3)
                    res3 = _filtrer(pos1, c3)
                    # Choix de la position des quarts de tour à gauche
                    for n2 in range(len(pos2) + 1):
                        for c4 in itertools.combinations(range(len(pos2)), n2):
                            pos4 = _choisir(pos2, c4)
                            res4 = _filtrer(pos2, c4)
                            print(_construire(pos3, res3, pos4, res4))


if __name__ == "__main__":
    gen()
