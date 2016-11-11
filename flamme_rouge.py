#!/usr/bin/python3

# Copyright ou © ou Copr. Guillaume Lemaître (2016)
#
#   guillaume.lemaitre@gmail.com
#
# Ce logiciel est un programme informatique permettant de jouer seul au jeu de
# plateau "Flamme rouge" avec un visuel bien infect.
#
# Ce logiciel est régi par la licence CeCILL soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions de la
# licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA sur le site
# "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie, de
# modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée. Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme, le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# À cet égard, l'attention de l'utilisateur est attirée sur les risques
# associés au chargement, à l'utilisation, à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant donné
# sa spécificité de logiciel libre, qui peut le rendre complexe à manipuler et
# qui le réserve donc à des développeurs et des professionnels avertis
# possédant des connaissances informatiques approfondies. Les utilisateurs
# sont donc invités à charger et tester l'adéquation du logiciel à leurs
# besoins dans des conditions permettant d'assurer la sécurité de leurs
# systèmes et ou de leurs données et, plus généralement, à l'utiliser et
# l'exploiter dans les mêmes conditions de sécurité.
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez pris
# connaissance de la licence CeCILL, et que vous en avez accepté les termes.


"""Implémentation du jeu "Flamme rouge" pour un joueur
"""

import collections
import enum
import logging
import random


class Couleur(enum.Enum):

    bleu = 1
    noir = 2
    gris = 3
    vert = 4


Paire = collections.namedtuple("Paire", ["sprinteur", "rouleur"])


class Joueur:

    def __init__(self, couleur):
        self.couleur = couleur
        self.sprinteur = [2, 2, 2,
                          3, 3, 3,
                          4, 4, 4,
                          5, 5, 5,
                          9, 9, 9]
        self.rouleur = [3, 3, 3,
                        4, 4, 4,
                        5, 5, 5,
                        6, 6, 6,
                        7, 7, 7]
        self.défausse_sprinteur = []
        self.défausse_rouleur = []
        random.shuffle(self.sprinteur)
        random.shuffle(self.rouleur)

    def placer(self, tracé):
        """Fournit une paire de lignes pour le placement sur la ligne de
        départ.
        """
        raise NotImplementedError

    def jouer(self, tracé):
        """Fournit une paire de déplacements pour ses coureurs
        """
        raise NotImplementedError

    def _piocher(self, tas, défausse):
        if len(tas) < 4:
            random.shuffle(défausse)
            tas.extend(défausse)
            défausse.clear()

        retour = tas[:4]
        tas[:] = tas[4:]

        return retour


class Humain(Joueur):

    def placer(self, tracé):
        libres = list()
        for i in range(tracé.départ):
            case = tracé.cases[i]
            if case.gauche is None:
                libres.append(i)
            if case.droite is None:
                libres.append(i)

        tracé.afficher(0, tracé.départ)

        while True:
            try:
                sprinteur = tracé.arrivée - \
                    int(input("Position du sprinteur ? "))
                if sprinteur in libres:
                    libres.remove(sprinteur)
                    break
            except ValueError:
                pass

        while True:
            try:
                rouleur = tracé.arrivée - int(input("Position du rouleur ? "))
                if rouleur in libres:
                    libres.remove(rouleur)
                    break
            except ValueError:
                pass

        return Paire(sprinteur, rouleur)

    def jouer(self, tracé):
        tracé.afficher()
        énergies_sprinteur = sorted(self._piocher(
            self.sprinteur, self.défausse_sprinteur))
        énergies_rouleur = sorted(self._piocher(
            self.rouleur, self.défausse_rouleur))
        print("Choix du sprinteur : {}".format(
            ", ".join(map(str, énergies_sprinteur))))
        print("Choix du rouleur : {}".format(
            ", ".join(map(str, énergies_rouleur))))

        while True:
            try:
                sprinteur = int(input("Énergie du sprinteur ? "))
                énergies_sprinteur.remove(sprinteur)
                break
            except ValueError:
                pass

        while True:
            try:
                rouleur = int(input("Énergie du rouleur ? "))
                énergies_rouleur.remove(rouleur)
                break
            except ValueError:
                pass

        self.défausse_sprinteur.extend(énergies_sprinteur)
        self.défausse_rouleur.extend(énergies_rouleur)

        return Paire(sprinteur, rouleur)


class Robot(Joueur):
    """Robot qui joue au pif
    """

    def placer(self, tracé):
        libres = list()
        for i in range(tracé.départ):
            case = tracé.cases[i]
            if case.gauche is None:
                libres.append(i)
            if case.droite is None:
                libres.append(i)
        sprinteur, rouleur = random.sample(libres, 2)
        return Paire(sprinteur, rouleur)

    def jouer(self, tracé):
        énergies_sprinteur = self._piocher(
            self.sprinteur, self.défausse_sprinteur)
        énergies_rouleur = self._piocher(self.rouleur, self.défausse_rouleur)

        sprinteur = random.sample(énergies_sprinteur, 1)[0]
        rouleur = random.sample(énergies_rouleur, 1)[0]

        énergies_sprinteur.remove(sprinteur)
        énergies_rouleur.remove(rouleur)

        self.défausse_sprinteur.extend(énergies_sprinteur)
        self.défausse_rouleur.extend(énergies_rouleur)

        return Paire(sprinteur, rouleur)


class Robourrin(Joueur):
    """Robot qui joue tout ce qu'il a de plus fort
    """

    def placer(self, tracé):
        return Paire(4, 4)

    def jouer(self, tracé):
        énergies_sprinteur = self._piocher(
            self.sprinteur, self.défausse_sprinteur)
        énergies_rouleur = self._piocher(self.rouleur, self.défausse_rouleur)

        sprinteur = max(énergies_sprinteur)
        rouleur = max(énergies_rouleur)

        énergies_sprinteur.remove(sprinteur)
        énergies_rouleur.remove(rouleur)

        self.défausse_sprinteur.extend(énergies_sprinteur)
        self.défausse_rouleur.extend(énergies_rouleur)

        return Paire(sprinteur, rouleur)


class Case:

    def __init__(self):
        self.droite = None
        self.gauche = None

    def est_vide(self):
        return (self.droite is None and
                self.gauche is None)

    def poser(self, pion):
        """Renvoit vrai ssi le pion a bien pu être posé sur la case
        """
        retour = True
        if self.droite is None:
            self.droite = pion
        elif self.gauche is None:
            self.gauche = pion
        else:
            retour = False
        return retour

    def retirer(self, pion):
        if self.droite == pion:
            self.droite = None
        else:
            self.gauche = None


class Profil(enum.Enum):

    sprinteur = 1
    rouleur = 2


class Pion(collections.namedtuple("Pion", ["profil", "joueur"])):

    def __str__(self):
        retour = self.profil.name[0].upper()
        retour += self.joueur.couleur.name[0].lower()

        return retour


class Tracé:

    def __init__(self):
        self.cases = list()
        for i in range(self.arrivée + 9):
            self.cases.append(Case())
        self.positions = dict()

    @property
    def départ(self):
        """Indice de la première case de course
        """
        return 5

    @property
    def arrivée(self):
        """Indice de la dernière case de course
        """
        return 73

    def poser(self, pion, ligne):
        """Placement des pions sur la ligne de départ
        """
        for i in reversed(range(ligne + 1)):
            if self.cases[i].poser(pion):
                self.positions[pion] = i
                break
        else:
            logging.error("Pas de place!")

    def retirer(self, pion):
        self.cases[self.positions[pion]].retirer(pion)
        del self.positions[pion]

    def afficher(self, début=None, garde=None, aspiration=list()):
        if début is None:
            début = min(self.positions.values(), default=0)
        if garde is None:
            garde = 1 + max(self.positions.values(), default=len(self.cases))

        # Ligne supérieure
        ligne = str()
        for i in range(début, garde):
            ligne += "+----"
        ligne += "+"
        print(ligne)

        # Côté gauche
        ligne = str()
        for i in range(début, garde):
            if i == self.départ or i == self.arrivée:
                ligne += "‖ "
            else:
                ligne += "| "
            if i in aspiration:
                ligne += "→→"
            else:
                pion = self.cases[i].gauche
                if pion is None:
                    ligne += "  "
                else:
                    ligne += str(pion)
            ligne += " "
        if garde == self.départ or garde == self.arrivée:
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

        # Ligne médiane
        ligne = str()
        for i in range(début, garde):
            ligne += "+~~~~"
        ligne += "+"
        print(ligne)

        # Côté droit
        ligne = str()
        for i in range(début, garde):
            if i == self.départ or i == self.arrivée:
                ligne += "‖ "
            else:
                ligne += "| "
            if i in aspiration:
                ligne += "→→"
            else:
                pion = self.cases[i].droite
                if pion is None:
                    ligne += "  "
                else:
                    ligne += str(pion)
            ligne += " "
        if garde == self.départ or garde == self.arrivée:
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

        # Ligne inférieure
        ligne = str()
        for i in range(début, garde):
            ligne += "+===="
        ligne += "+"
        print(ligne)

        # Numéro de case
        ligne = str()
        for i in range(début, garde):
            if i == self.départ or i == self.arrivée:
                ligne += "‖ {:>2} ".format(self.arrivée - i)
            else:
                ligne += "| {:>2} ".format(self.arrivée - i)
        if garde == self.départ or garde == self.arrivée:
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

    def aspirer(self):
        """Applique l'algorithme d'aspiration
        """
        # Détermination des cases d'aspiration
        cases_aspiration = list()
        for i in range(min(self.positions.values()) + 1,
                       max(self.positions.values())):
            if (not self.cases[i - 1].est_vide() and
                    self.cases[i].est_vide() and
                    not self.cases[i + 1].est_vide()):
                cases_aspiration.append(i)

        # Affichage
        if len(cases_aspiration) != 0:
            self.afficher(aspiration=cases_aspiration)

        # Application de l'aspiration
        for i in cases_aspiration:
            j = i - 1
            while not self.cases[j].est_vide():
                case = self.cases[j]
                pion = case.droite
                self.retirer(pion)
                self.poser(pion, j + 1)
                pion = case.gauche
                if pion is not None:
                    self.retirer(pion)
                    self.poser(pion, j + 1)
                j -= 1

    def fatiguer(self):
        """Ajoute de la fatigue à tous les coureurs face au vent
        """
        fatigués = collections.defaultdict(list)

        for i in range(min(self.positions.values()),
                       1 + max(self.positions.values())):
            case = self.cases[i]
            if (not case.est_vide() and
                    i < self.arrivée and
                    self.cases[i + 1].est_vide()):
                pion = case.droite
                if pion.profil == Profil.sprinteur:
                    pion.joueur.défausse_sprinteur.append(2)
                else:
                    pion.joueur.défausse_rouleur.append(2)
                fatigués[pion.joueur.couleur].append(pion)

                pion = case.gauche
                if pion is not None:
                    if pion.profil == Profil.sprinteur:
                        pion.joueur.défausse_sprinteur.append(2)
                    else:
                        pion.joueur.défausse_rouleur.append(2)
                    fatigués[pion.joueur.couleur].append(pion)

        for couleur in sorted(fatigués, key=lambda c: c.name):
            ligne = "Équipe {}e : fatigue ".format(couleur.name)
            coureurs = sorted(fatigués[couleur], key=str)
            ligne += " et ".join(["du {}".format(x.profil.name)
                                  for x in coureurs])
            print(ligne)

    def ordre(self):
        """Affiche l'ordre des équipes dans la course
        """
        couleurs = list()
        for i in reversed(range(min(self.positions.values()),
                                max(self.positions.values()) + 1)):
            case = self.cases[i]
            pion = case.droite
            if pion is not None and pion.joueur.couleur not in couleurs:
                couleurs.append(pion.joueur.couleur)
            pion = case.gauche
            if pion is not None and pion.joueur.couleur not in couleurs:
                couleurs.append(pion.joueur.couleur)

        # Affichage
        for i in range(len(couleurs)):
            print("Équipe n°{} : {}".format(i + 1, couleurs[i].name))


def principal():
    joueurs = [Humain(Couleur.gris), Robourrin(Couleur.bleu),
               Robot(Couleur.noir), Robot(Couleur.vert)]
    random.shuffle(joueurs)
    tracé = Tracé()

    # Placement initial
    for joueur in joueurs:
        paire = joueur.placer(tracé)
        if paire.sprinteur >= paire.rouleur:
            pion = Pion(Profil.sprinteur, joueur)
            tracé.poser(pion, paire.sprinteur)
            pion = Pion(Profil.rouleur, joueur)
            tracé.poser(pion, paire.rouleur)
        else:
            pion = Pion(Profil.rouleur, joueur)
            tracé.poser(pion, paire.rouleur)
            pion = Pion(Profil.sprinteur, joueur)
            tracé.poser(pion, paire.sprinteur)

    # Course !
    fin_de_partie = False
    while not fin_de_partie:
        print("\n")

        # Phase énergie
        paires = dict()
        for joueur in joueurs:
            paires[joueur] = joueur.jouer(tracé)

        # Phase de déplacement
        for i in reversed(range(min(tracé.positions.values()),
                                1 + max(tracé.positions.values()))):
            case = tracé.cases[i]
            # Le pion droit d'abord
            pion = case.droite
            if pion is not None:
                paire = paires[pion.joueur]
                énergie = paire.rouleur
                if pion.profil == Profil.sprinteur:
                    énergie = paire.sprinteur
                tracé.retirer(pion)
                tracé.poser(pion, i + énergie)
            # ...puis le pion gauche
            pion = case.gauche
            if pion is not None:
                paire = paires[pion.joueur]
                énergie = paire.rouleur
                if pion.profil == Profil.sprinteur:
                    énergie = paire.sprinteur
                tracé.retirer(pion)
                tracé.poser(pion, i + énergie)

        # Phase finale
        tracé.aspirer()
        tracé.fatiguer()

        # Détection de la fin de partie
        fin_de_partie = (max(tracé.positions.values()) > 72)

    # Fin de la partie
    tracé.afficher()
    tracé.ordre()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    principal()
