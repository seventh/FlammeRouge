"""Un trajet est une succession de 21 entiers entre -2 et 2 débutant et
 terminant par 0

Le codage vers un entier inférieur à 5^19 permet de stocker un trajet
sur seulement 6 octets.
"""


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
