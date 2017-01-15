#!/usr/bin/env python3

"""Test du moteur
"""

import unittest
from flamme_rouge import Case, Couleur, Joueur, Pente, Pion, Profil, Tracé


class TestMoteur(unittest.TestCase):
    """Vérification des règles d'aspiration et de fatigue
    """

    def test_aspi_à_l_arrivée(self):
        """Un coureur arrivé ne provoque pas d'aspiration
        """
        # Conditions initiales
        cases = [Case(Pente.plat),
                 Case(Pente.plat),
                 Case(Pente.plat)]
        tracé = Tracé(cases, 0, 1, len(cases))
        joueur = Joueur(Couleur.gris, 1)
        p1 = Pion(Profil.sprinteur, joueur)
        p2 = Pion(Profil.rouleur, joueur)
        tracé.poser(p1, 0)
        tracé.poser(p2, 2)
        tracé.afficher()

        # effet
        tracé.aspirer_et_fatiguer()

        # Vérification
        self.assertTrue(tracé.cases[1].est_vide(), "Aspiration à l'arrivée")


if __name__ == "__main__":
    unittest.main()
