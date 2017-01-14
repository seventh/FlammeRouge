#!/usr/bin/python3

# Copyright ou © ou Copr. Guillaume Lemaître (2016, 2017)
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
import json
import logging
import random


def choisir_course(chemin):
    # Lecture du fichier
    parcours = None
    with open(chemin, "rt") as entrée:
        parcours = json.load(entrée)

    # Vérification
    for nom_case, case in parcours["cases"].items():
        if not ("angle" in case and
                "pente" in case):
            logging.error("Case {} incohérente".format(nom_case))

    for nom_tronçon, tronçon in parcours["tronçons"].items():
        if tronçon is None:
            logging.warning("Tronçon {} non déterminé".format(nom_tronçon))
        else:
            if len(tronçon) not in [2, 6]:
                logging.error("Tronçon {} incohérent".format(nom_tronçon))
            for nom_case in tronçon:
                if nom_case not in parcours["cases"]:
                    logging.error(
                        "Case inconnue dans tronçon «{}»".format(nom_tronçon))

    for nom_course, course in parcours["courses"].items():
        for nom_tronçon in course["tracé"]:
            if nom_tronçon not in parcours["tronçons"]:
                logging.error(
                    "Tronçon inconnu dans la course «{}»".format(nom_course))
            elif parcours["tronçons"][nom_tronçon] is None:
                logging.error(
                    "Le course «{}» référence le tronçon «{}»".format(
                        nom_course, nom_tronçon))
            elif nom_tronçon.swapcase() in course["tracé"]:
                logging.error(
                    "Le tronçon «{}» est référencé sous plusieurs formes dans la course «{}»".format(
                        nom_tronçon, nom_course))
            elif course["tracé"].count(nom_tronçon) > 1:
                logging.error(
                    "Le tronçon «{}» est référencé plusieurs fois dans la course «{}»".format(
                        nom_tronçon, nom_course))

    # Choix de la course par le joueur
    noms = sorted(parcours["courses"])
    for i, nom_course in enumerate(noms):
        print("{}) {}".format(i + 1, nom_course))
    while True:
        try:
            i = int(input("Choix du parcours ? ")) - 1
            if 0 <= i < len(noms):
                nom_course = noms[i]
                break
        except ValueError:
            pass

    # Construction de la course choisie
    cases = list()
    départ = None
    arrivée = None
    course = parcours["courses"][nom_course]
    nb_tours = course["tours"]
    tronçons = course["tracé"]
    for i in range(nb_tours):
        for nom_tronçon in tronçons:
            for nom_case in parcours["tronçons"][nom_tronçon]:
                case = parcours["cases"][nom_case]
                if case["pente"] == 0:
                    cases.append(Case(Pente.plat))
                elif case["pente"] == 1:
                    cases.append(Case(Pente.col))
                else:  # case["pente"] == -1
                    cases.append(Case(Pente.descente))

                if nom_case == "départ":
                    départ = len(cases)
                elif nom_case == "arrivée" and arrivée is None:
                    arrivée = len(cases) - 1
    if nb_tours == 1:
        lg_circuit = arrivée - départ
    else:
        lg_circuit = len(cases) / nb_tours
        départ = 0
        t_arrivée = tronçons[-1]
        for nom_case in parcours["tronçons"][t_arrivée]:
            if nom_case == "arrivée":
                cases = [Case(Pente.plat)] + cases
                départ += 1

        arrivée = len(cases)
        t_départ = tronçons[0]
        for nom_case in parcours["tronçons"][t_départ]:
            if nom_case == "départ":
                cases += [Case(Pente.plat)]

    tracé = Tracé(cases, départ, arrivée, lg_circuit)
    return tracé, nb_tours


class Couleur(enum.Enum):

    bleu = 1
    noir = 2
    gris = 3
    vert = 4


Paire = collections.namedtuple("Paire", ["sprinteur", "rouleur"])


class Joueur:

    def __init__(self, couleur, nb_tours):
        self.couleur = couleur
        self.sprinteur = [2, 2, 2,
                          3, 3, 3,
                          4, 4, 4,
                          5, 5, 5,
                          9, 9, 9]
        self.sprinteur = nb_tours * self.sprinteur
        self.rouleur = [3, 3, 3,
                        4, 4, 4,
                        5, 5, 5,
                        6, 6, 6,
                        7, 7, 7]
        self.rouleur = nb_tours * self.rouleur
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
        if len(tas) == 0:
            tas.append(2)

        retour = tas[:4]
        tas[:] = tas[4:]

        return retour


class Humain(Joueur):

    def placer(self, tracé):
        tracé.afficher(0, tracé.départ)

        libres = list()
        for i in range(tracé.départ):
            case = tracé.cases[i]
            if case.gauche is None:
                libres.append(i)
            if case.droite is None:
                libres.append(i)

        while True:
            try:
                sprinteur = tracé.départ + \
                    int(input("Position du sprinteur ? "))
                if sprinteur in libres:
                    libres.remove(sprinteur)
                    break
            except ValueError:
                pass

        while True:
            try:
                rouleur = tracé.départ + int(input("Position du rouleur ? "))
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


class Robomou(Robot):

    def jouer(self, tracé):
        énergies_sprinteur = self._piocher(
            self.sprinteur, self.défausse_sprinteur)
        énergies_rouleur = self._piocher(self.rouleur, self.défausse_rouleur)

        # On a beau jouer au pif, on évite de trop fatiguer
        index_sprinteur = tracé.positions[Pion(Profil.sprinteur, self)]
        index_rouleur = tracé.positions[Pion(Profil.rouleur, self)]

        if tracé.cases[index_sprinteur].pente == Pente.descente:
            sprinteur = min(énergies_sprinteur)
        else:
            for d in range(1, 10):
                if tracé.cases[index_sprinteur + d].pente == Pente.col:
                    if d <= 5:
                        max_sprinteur = 5
                    else:
                        max_sprinteur = d - 1

                    és = [é for é in énergies_sprinteur if é <= max_sprinteur]
                    if len(és) == 0:
                        és = [min(énergies_sprinteur)]
                    break
            else:
                és = énergies_sprinteur
            sprinteur = random.sample(és, 1)[0]

        if tracé.cases[index_rouleur].pente == Pente.descente:
            rouleur = min(énergies_rouleur)
        else:
            for d in range(1, 10):
                if tracé.cases[index_rouleur + d].pente == Pente.col:
                    if d <= 5:
                        max_rouleur = 5
                    else:
                        max_rouleur = d - 1

                    és = [é for é in énergies_rouleur if é <= max_rouleur]
                    if len(és) == 0:
                        és = [min(énergies_rouleur)]
                    break
            else:
                és = énergies_rouleur
            rouleur = random.sample(és, 1)[0]

        énergies_sprinteur.remove(sprinteur)
        énergies_rouleur.remove(rouleur)

        self.défausse_sprinteur.extend(énergies_sprinteur)
        self.défausse_rouleur.extend(énergies_rouleur)

        return Paire(sprinteur, rouleur)


class Robourrin(Joueur):
    """Robot qui joue tout ce qu'il a de plus fort
    """

    def placer(self, tracé):
        return Paire(tracé.départ - 1, tracé.départ - 1)

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


class Rofinot(Joueur):
    """Robot qui joue tout ce qu'il a de plus fort, sans effort inutile
    """

    def placer(self, tracé):
        return Paire(tracé.départ - 1, tracé.départ - 1)

    def jouer(self, tracé):
        énergies_sprinteur = self._piocher(
            self.sprinteur, self.défausse_sprinteur)
        énergies_rouleur = self._piocher(self.rouleur, self.défausse_rouleur)

        # On a beau être un bourrin, on évite de trop fatiguer
        index_sprinteur = tracé.positions[Pion(Profil.sprinteur, self)]
        index_rouleur = tracé.positions[Pion(Profil.rouleur, self)]

        if tracé.cases[index_sprinteur].pente == Pente.descente:
            sprinteur = min(énergies_sprinteur)
        else:
            for d in range(1, 10):
                if tracé.cases[index_sprinteur + d].pente == Pente.col:
                    if d <= 5:
                        max_sprinteur = 5
                    else:
                        max_sprinteur = d - 1

                    és = [é for é in énergies_sprinteur if é <= max_sprinteur]
                    if len(és) == 0:
                        és = [min(énergies_sprinteur)]
                    break
            else:
                és = énergies_sprinteur
            sprinteur = max(és)

        if tracé.cases[index_rouleur].pente == Pente.descente:
            rouleur = min(énergies_rouleur)
        else:
            for d in range(1, 10):
                if tracé.cases[index_rouleur + d].pente == Pente.col:
                    if d <= 5:
                        max_rouleur = 5
                    else:
                        max_rouleur = d - 1

                    ér = [é for é in énergies_rouleur if é <= max_rouleur]
                    if len(ér) == 0:
                        ér = [min(énergies_rouleur)]
                    break
            else:
                ér = énergies_rouleur
            rouleur = max(ér)

        énergies_sprinteur.remove(sprinteur)
        énergies_rouleur.remove(rouleur)

        self.défausse_sprinteur.extend(énergies_sprinteur)
        self.défausse_rouleur.extend(énergies_rouleur)

        return Paire(sprinteur, rouleur)


class Pente(enum.Enum):
    """Pente perçue dans le sens de la marche
    """

    plat = 0
    col = 1
    descente = 2


class Case:

    def __init__(self, pente):
        self.droite = None
        self.gauche = None
        self.pente = pente

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

    def __init__(self, cases, départ, arrivée, lg_tour):
        self.cases = cases
        self._départ = départ
        self._arrivée = arrivée
        self._lg_tour = lg_tour

        self.positions = dict()

    @property
    def départ(self):
        """Indice de la première case de course
        """
        return self._départ

    @property
    def arrivée(self):
        """Indice de la dernière case de course
        """
        return self._arrivée

    @property
    def lg_tour(self):
        """Nombre de cases dans un tour
        """
        return self._lg_tour

    def est_flamme(self, indice):
        retour = (indice == self.départ or
                  indice == self.arrivée or
                  (indice - self.départ) % self.lg_tour == 0)
        return retour

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
        segments = [""]
        for i in range(début, garde):
            case = self.cases[i]
            if case.pente == Pente.plat:
                segments.append("~~~~")
            elif case.pente == Pente.col:
                segments.append("<<<<")
            else:  # case.pente == Pente.descente
                segments.append(">>>>")
        segments.append("")
        print("+".join(segments))

        # Côté gauche
        ligne = str()
        for i in range(début, garde):
            if self.est_flamme(i):
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
        if self.est_flamme(garde):
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

        # Ligne médiane
        ligne = str()
        for i in range(début, garde):
            ligne += "+----"
        ligne += "+"
        print(ligne)

        # Côté droit
        ligne = str()
        for i in range(début, garde):
            if self.est_flamme(i):
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
        if self.est_flamme(garde):
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

        # Ligne inférieure
        segments = [""]
        for i in range(début, garde):
            case = self.cases[i]
            if case.pente == Pente.plat:
                segments.append("====")
            elif case.pente == Pente.col:
                segments.append("<<<<")
            else:  # case.pente == Pente.descente
                segments.append(">>>>")
        segments.append("")
        print("+".join(segments))

        # Numéro de case
        ligne = str()
        for i in range(début, garde):
            if self.est_flamme(i):
                ligne += "‖{: <4}".format(i - self.départ)
            else:
                ligne += "|{: <4}".format(i - self.départ)
        if self.est_flamme(garde):
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

        # Changement de pente
        for i in range(garde, len(self.cases)):
            ligne = None
            if i == self.arrivée:
                ligne = " Arrivée au km {}".format(i - self.départ)
            elif self.cases[garde - 1].pente != self.cases[i].pente:
                ligne = " Prochain point d'étape au km {} : ".format(
                    i - self.départ)
                j = i + 1
                while (j < self.arrivée and
                       self.cases[j].pente == self.cases[i].pente):
                    j += 1
                if self.cases[i].pente == Pente.col:
                    ligne += "ascension"
                elif self.cases[i].pente == Pente.plat:
                    ligne += "plaine"
                else:  # self.cases[i].pente == Pente.descente
                    ligne += "descente"
                ligne += " de {} km".format(j - i)

            if ligne is not None:
                print(ligne)
                break

    def déplacer(self, paires):
        """Applique, du coureur en tête à la voiture-balai, les déplacements
        """
        for i in reversed(range(min(self.positions.values()),
                                1 + max(self.positions.values()))):
            case = self.cases[i]
            # Le pion droit d'abord
            pion = case.droite
            if pion is not None:
                paire = paires[pion.joueur]
                énergie = paire.rouleur
                if pion.profil == Profil.sprinteur:
                    énergie = paire.sprinteur
                self._déplacer_pion(pion, énergie)
            # ...puis le pion gauche
            pion = case.gauche
            if pion is not None:
                paire = paires[pion.joueur]
                énergie = paire.rouleur
                if pion.profil == Profil.sprinteur:
                    énergie = paire.sprinteur
                self._déplacer_pion(pion, énergie)

    def _déplacer_pion(self, pion, énergie):
        # Localisation du coureur
        i = self.positions[pion]
        self.retirer(pion)

        # On ne peut pas sortir du plateau
        énergie = min(énergie, len(self.cases) - i - 1)

        # Application des règles de déplacement
        if self.cases[i].pente == Pente.descente:
            énergie = max(5, énergie)

        for j in range(énergie + 1):
            if self.cases[i + j].pente == Pente.col:
                énergie = min(énergie, max(5, j - 1))

        # Déplacement effectif
        self.poser(pion, i + énergie)

    def aspirer(self, joueurs):
        """Applique l'algorithme d'aspiration
        """
        # Détermination des cases d'aspiration
        cases_aspiration = list()
        for i in range(min(self.positions.values()) + 1,
                       max(self.positions.values())):
            if (not self.cases[i - 1].est_vide() and
                    not self.cases[i - 1].pente == Pente.col and
                    self.cases[i].est_vide() and
                    not self.cases[i + 1].est_vide() and
                    not self.cases[i + 1].pente == Pente.col):
                cases_aspiration.append(i)

        # Affichage
        if len(cases_aspiration) != 0:
            self.afficher(aspiration=cases_aspiration)

        # Application de l'aspiration
        for i in cases_aspiration:
            j = i - 1
            while not (self.cases[j].est_vide() or
                       self.cases[j].pente == Pente.col):
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

        return fatigués

    def afficher_fatigue(self, fatigués, couleur_joueur):
        for couleur in sorted(fatigués, key=lambda c: c.name):
            ligne = "Équipe {}e : fatigue ".format(couleur.name)
            coureurs = sorted(fatigués[couleur], key=str)
            ligne += " et ".join(["du {}".format(x.profil.name)
                                  for x in coureurs])
            if couleur == couleur_joueur:
                ligne += " <---"
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

        return couleurs


def principal():
    tracé, nb_tours = choisir_course("courses.json")

    joueurs = [Humain(Couleur.gris, nb_tours),
               Robourrin(Couleur.bleu, nb_tours),
               Rofinot(Couleur.noir, nb_tours),
               Robomou(Couleur.vert, nb_tours)]
    random.shuffle(joueurs)

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
        tracé.déplacer(paires)

        # Phase finale
        tracé.aspirer(joueurs)
        fatigués = tracé.fatiguer()
        tracé.afficher_fatigue(fatigués, Couleur.gris)

        # Détection de la fin de partie
        fin_de_partie = (max(tracé.positions.values()) >= tracé.arrivée)

    # Fin de la partie
    tracé.afficher()
    tracé.ordre()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    principal()
