"""Lecteur/Enregistreur d'entiers signés avec une certaine précision
"""

import fractions
import trajet
import trajet2


def _taille_bloc(nb_bits):
    retour = nb_bits // fractions.gcd(nb_bits, 8)
    return retour


class Lecteur:

    def __init__(self, fichier, nb_bits):
        self._fichier = fichier
        self._nb_bits = nb_bits
        self._taille_bloc = _taille_bloc(nb_bits)
        self._nb_items_par_bloc = self._taille_bloc * 8 // self._nb_bits
        self._masque = (1 << nb_bits) - 1
        self._bloc = None
        self._item = self._nb_items_par_bloc

    def lit(self):
        retour = None
        if self._item == self._nb_items_par_bloc:
            données = self._fichier.read(self._taille_bloc)
            if len(données) == 0:
                self._bloc = None
            else:
                self._bloc = int.from_bytes(données, "big", signed=True)
                self._item = 0
        if self._bloc is not None:
            self._item += 1
            retour = self._masque & (self._bloc >> (
                self._nb_bits * (self._nb_items_par_bloc - self._item)))
        return retour


class Metteur:

    def __init__(self, fichier, nb_bits):
        self._fichier = fichier
        self._nb_bits = nb_bits
        self._taille_bloc = _taille_bloc(nb_bits)
        self._nb_items_par_bloc = self._taille_bloc * 8 // self._nb_bits
        self._bloc = 0
        self._item = 0

# On choisit de ne pas graver le reliquat !
#    def __del__(self):
#        while self._item != 0:
#            self.met(0)

    def met(self, valeur):
        self._bloc <<= self._nb_bits
        self._bloc += valeur
        if self._item < self._nb_items_par_bloc - 1:
            self._item += 1
        else:
            données = self._bloc.to_bytes(self._taille_bloc, "big")
            self._fichier.write(données)
            self._item = 0
            self._bloc = 0


if __name__ == "__main__":
    # Conversion
    i = 0
    with open("trajets.bin", "rb") as entrée, open("trajets2.bin", "wb") as sortie:
        L = Lecteur(entrée, 48)
        M = Metteur(sortie, 38)
        while True:
            valeur = L.lit()
            if valeur is None:
                break
            t = trajet.décoder(valeur)
            valeur2 = trajet2.coder(t)
            M.met(valeur2)
            i += 1
            if i % 100000 == 0:
                print("Conversion : {}".format(i))
    print("Conversion : {}".format(i))

    # Vérification
    i = 0
    with open("trajets2.bin", "rb") as entrée, open("trajets3.bin", "wb") as sortie:
        L = Lecteur(entrée, 38)
        M = Metteur(sortie, 48)
        while True:
            valeur = L.lit()
            if valeur is None:
                break
            t = trajet2.décoder(valeur)
            valeur2 = trajet.coder(t)
            M.met(valeur2)
            i += 1
            if i % 100000 == 0:
                print("Vérification : {}".format(i))
    print("Vérification : {}".format(i))
