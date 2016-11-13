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
import json
import logging
import pickle
import random
import socket
import sys
import threading
import time


def charger_parcours(chemin):
    # Lecture du fichier
    parcours = None
    with open(chemin, "rt") as entrée:
        parcours = json.load(entrée)

    # Vérification
    for nom_case, case in parcours["cases"].items():
        if not ("angle" in case and
                "pente" in case):
            logging.error("Case {} inchoérente".format(nom_case))

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

    for nom_tracé, tracé in parcours["tracés"].items():
        for nom_tronçon in tracé:
            if nom_tronçon not in parcours["tronçons"]:
                logging.error(
                    "Tronçon inconnu dans tracé {}".format(nom_tracé))
            elif parcours["tronçons"][nom_tronçon] is None:
                logging.error(
                    "Le tracé «{}» référence le tronçon «{}»".format(
                        nom_tracé, nom_tronçon))

    # Choix du tracé par le joueur
    noms = sorted(parcours["tracés"])
    for i, nom_tracé in enumerate(noms):
        print("{}) {}".format(i + 1, nom_tracé))
    while True:
        try:
            i = int(input("Choix du parcours ? ")) - 1
            if 0 <= i < len(noms):
                nom_tracé = noms[i]
                break
        except ValueError:
            pass

    # Construction du tracé choisi
    cases = list()
    départ = None
    arrivée = None
    tracé = parcours["tracés"][nom_tracé]
    for nom_tronçon in tracé:
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

    tracé = Tracé(cases, départ, arrivée)
    return tracé


class Couleur(enum.Enum):

    bleu = 1
    noir = 2
    gris = 3
    vert = 4


Paire = collections.namedtuple("Paire", ["sprinteur", "rouleur"])


class ClientServeur:

    def send(self, socket_tx, msg):
        socket_tx.send('{}:'.format(len(msg)).encode('utf-8'))
        socket_tx.send(msg)
        return socket_tx

    def recv(self, socket_rx):
        longueur = 0
        while True:
            message = socket_rx.recv(1).decode('utf-8')
            if message == ':' or message < '0' or message > '9':
                break
            longueur = longueur * 10 + int(message)

        fragments = []
        while longueur > 0:
            fragment = socket_rx.recv(longueur)
            fragments.append(fragment)
            longueur -= len(fragment)

        return b''.join(fragments)


class Client:

    def __getstate__(self):
        None

    def afficher(self, tracé, début=None, garde=None, aspiration=list()):
        raise NotImplementedError

    def afficher_fatigue(self, tracé, fatigués):
        raise NotImplementedError

    def demander_positions(self, tracé, libres):
        raise NotImplementedError

    def demander_jeu(self, choix_sprinteur, choix_rouleur):
        raise NotImplementedError

    def ordre(self, couleurs):
        raise NotImplementedError

    def attente(self, couleurs):
        raise NotImplementedError

    def couleur(self, couleur):
        self.couleur = couleur.name


class ClientNul(Client):

    def afficher(self, tracé, début=None, garde=None, aspiration=list()):
        pass

    def afficher_fatigue(self, tracé, fatigués):
        pass

    def demander_positions(self, tracé, libres):
        pass

    def demander_jeu(self, choix_sprinteur, choix_rouleur):
        pass

    def ordre(self, couleurs):
        pass

    def attente(self, couleurs):
        pass


class ServeurConsole(Client, ClientServeur):

    def __init__(self):
        serveur = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serveur.bind((socket.gethostname(), 0))
        print(serveur.getsockname()[1])
        serveur.listen(1)
        self.socket = serveur.accept()[0]

    def afficher(self, tracé, début=None, garde=None, aspiration=list()):
        message = pickle.dumps({"commande": "afficher",
                                "tracé": tracé,
                                "début": début,
                                "garde": garde,
                                "aspiration": aspiration})
        self.send(self.socket, message)

    def afficher_fatigue(self, tracé, fatigués):
        message = pickle.dumps(
            {"commande": "afficher_fatigue",
             "tracé": tracé,
             "fatigués": fatigués})
        self.send(self.socket, message)

    def demander_positions(self, tracé, libres):
        message = pickle.dumps(
            {"commande": "demander_positions",
             "tracé": tracé,
             "libres": libres})
        while True:
            self.send(self.socket, message)
            try:
                réponse = self.recv(self.socket)
                positions = pickle.loads(réponse)
                libres_temp = list(libres)
                sprinteur = positions.sprinteur
                rouleur = positions.rouleur
                libres_temp.remove(sprinteur)
                libres_temp.remove(rouleur)
                break
            except ValueError as err:
                pass

        # message = pickle.dumps({"commande": "position_ok"})
        # self.send(self.socket, message)

        return Paire(sprinteur, rouleur)

    def demander_jeu(self, énergies_sprinteur, énergies_rouleur):
        message = pickle.dumps({"commande": "demander_jeu",
                                "énergies_sprinteur": énergies_sprinteur,
                                "énergies_rouleur": énergies_rouleur})
        while True:
            self.send(self.socket, message)
            try:
                réponse = self.recv(self.socket)
                énergies = pickle.loads(réponse)
                sprinteur = énergies.sprinteur
                rouleur = énergies.rouleur
                énergies_sprinteur_temp = list(énergies_sprinteur)
                énergies_sprinteur_temp.remove(sprinteur)
                énergies_rouleur_temp = list(énergies_rouleur)
                énergies_rouleur_temp.remove(rouleur)
                break
            except ValueError:
                pass

        # message = pickle.dumps({"commande": "jeu_ok"})
        # self.send(self.socket, message)

        return Paire(sprinteur, rouleur)

    def ordre(self, couleurs):
        message = pickle.dumps({"commande": "ordre", "couleurs": couleurs})
        self.send(self.socket, message)

    def attente(self, couleurs):
        message = pickle.dumps({"commande": "attente", "couleurs": couleurs})
        self.send(self.socket, message)

    def couleur(self, couleur):
        message = pickle.dumps({"commande": "couleur", "couleur": couleur})
        self.send(self.socket, message)


class Console(Client):

    def afficher(self, tracé, début=None, garde=None, aspiration=list()):
        if début is None:
            print("\n")

        tracé.afficher(début, garde, aspiration)

    def afficher_fatigue(self, tracé, fatigués):
        tracé.afficher_fatigue(fatigués, self.couleur)

    def demander_positions(self, tracé, libres):
        while True:
            try:
                sprinteur = (tracé.arrivée -
                             int(input("Position du sprinteur {} ? ".format(
                                 self.couleur))))
                if sprinteur in libres:
                    libres.remove(sprinteur)
                    break
            except ValueError:
                pass

        while True:
            try:
                rouleur = (tracé.arrivée -
                           int(input("Position du rouleur {} ? ".format(
                               self.couleur))))
                if rouleur in libres:
                    libres.remove(rouleur)
                    break
            except ValueError:
                pass

        return Paire(sprinteur, rouleur)

    def demander_jeu(self, énergies_sprinteur, énergies_rouleur):
        print("Choix du sprinteur : {}".format(
            ", ".join(map(str, énergies_sprinteur))))
        print("Choix du rouleur : {}".format(
            ", ".join(map(str, énergies_rouleur))))

        while True:
            try:
                sprinteur = int(
                    input(
                        "Énergie du sprinteur {} ? ".format(
                            self.couleur)))
                énergies_sprinteur.remove(sprinteur)
                break
            except ValueError:
                pass

        while True:
            try:
                rouleur = int(
                    input(
                        "Énergie du rouleur {} ? ".format(
                            self.couleur)))
                énergies_rouleur.remove(rouleur)
                break
            except ValueError:
                pass

        return Paire(sprinteur, rouleur)

    def ordre(self, couleurs):
        for i in range(len(couleurs)):
            ligne = "Équipe n°{} : {}".format(i + 1, couleurs[i].name)
            if couleurs[i].name == self.couleur:
                ligne += " <---"
            print(ligne)

    def attente(self, couleurs):
        print("Attente joueur{} : {}".format(
            "s" if len(couleurs) > 1 else "",
            ", ".join(couleurs)))

    def couleur(self, couleur):
        self.couleur = couleur.name
        print("Vous êtes le joueur {}".format(couleur.name))


class ClientConsole(Console, ClientServeur):

    def __init__(self, adresse, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((adresse, port))

    def jouer(self):
        while True:
            try:
                message = self.recv(self.socket)
                msg = pickle.loads(message)
                if msg['commande'] == "afficher":
                    Console.afficher(
                        self,
                        msg['tracé'],
                        msg['début'],
                        msg['garde'],
                        msg['aspiration'])
                elif msg['commande'] == "afficher_fatigue":
                    Console.afficher_fatigue(
                        self, msg['tracé'], msg['fatigués'])
                elif msg['commande'] == "demander_positions":
                    positions = Console.demander_positions(
                        self, msg['tracé'], msg['libres'])
                    réponse = pickle.dumps(positions)
                    self.socket = self.send(self.socket, réponse)
                elif msg['commande'] == "demander_jeu":
                    énergies = Console.demander_jeu(
                        self, msg['énergies_sprinteur'],
                        msg['énergies_rouleur'])
                    réponse = pickle.dumps(énergies)
                    self.socket = self.send(self.socket, réponse)
                elif msg['commande'] == "ordre":
                    Console.ordre(self, msg['couleurs'])
                    break
                elif msg['commande'] == "attente":
                    Console.attente(self, msg['couleurs'])
                elif msg['commande'] == "couleur":
                    Console.couleur(self, msg['couleur'])
            except ValueError as err:
                print(err)
                pass

        self.socket.close()


class Joueur:

    def __init__(self, couleur):
        self.couleur = couleur
        self.client = ClientNul()
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
        if len(tas) == 0:
            tas.append(2)

        retour = tas[:4]
        tas[:] = tas[4:]

        return retour


class Humain(Joueur):

    def __init__(self, couleur, client):
        Joueur.__init__(self, couleur)
        self.client = client

    def placer(self, tracé):
        libres = list()
        for i in range(tracé.départ):
            case = tracé.cases[i]
            if case.gauche is None:
                libres.append(i)
            if case.droite is None:
                libres.append(i)

        while True:
            positions = self.client.demander_positions(tracé, libres)
            try:
                libres_temp = list(libres)
                sprinteur = int(positions.sprinteur)
                rouleur = int(positions.rouleur)
                libres_temp.remove(sprinteur)
                libres_temp.remove(rouleur)
            except ValueError:
                pass
            break

        return positions

    def jouer(self, tracé):
        self.client.afficher(tracé)
        énergies_sprinteur = sorted(self._piocher(
            self.sprinteur, self.défausse_sprinteur))
        énergies_rouleur = sorted(self._piocher(
            self.rouleur, self.défausse_rouleur))

        while True:
            choix = self.client.demander_jeu(list(énergies_sprinteur),
                                             list(énergies_rouleur))
            try:
                sprinteur = int(choix.sprinteur)
                rouleur = int(choix.rouleur)
                énergies_sprinteur.remove(sprinteur)
                énergies_rouleur.remove(rouleur)
            except ValueError:
                pass
            break

        self.défausse_sprinteur.extend(énergies_sprinteur)
        self.défausse_rouleur.extend(énergies_rouleur)

        return choix


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

    def __init__(self, cases, départ, arrivée):
        self.cases = cases
        self._départ = départ
        self._arrivée = arrivée

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
                segments.append("----")
            elif case.pente == Pente.col:
                segments.append("<<<<")
            else:  # case.pente == Pente.descente
                segments.append(">>>>")
        segments.append("")
        print("+".join(segments))

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
            if i == self.départ or i == self.arrivée:
                ligne += "‖ {:>2} ".format(self.arrivée - i)
            else:
                ligne += "| {:>2} ".format(self.arrivée - i)
        if garde == self.départ or garde == self.arrivée:
            ligne += "‖"
        else:
            ligne += "|"
        print(ligne)

        # Changement de pente
        for i in range(garde, len(self.cases)):
            if self.cases[garde - 1].pente != self.cases[i].pente:
                if self.cases[i].pente == Pente.col:
                    print("Prochain col au point {}".format(self.arrivée - i))
                elif self.cases[i].pente == Pente.plat:
                    print("Retour au plat au point {}".format(
                        self.arrivée - i))
                else:
                    print("Prochaine descente au point {}".format(
                        self.arrivée - i))
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
            for joueur in joueurs:
                joueur.client.afficher(self, aspiration=cases_aspiration)

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
            if couleur.name == couleur_joueur:
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


def principal(nb_humains):
    couleurs = [Couleur.gris, Couleur.bleu, Couleur.noir, Couleur.vert]
    joueurs = list()
    joueurs.append(Humain(couleurs[0], Console()))
    tâches = list()
    for i in range(1, nb_humains):
        tâche = threading.Thread(
            target=lambda j, c: j.append(Humain(c, ServeurConsole())),
            args=(joueurs, couleurs[i]))
        tâche.start()
        tâches.append(tâche)
    for tâche in tâches:
        tâche.join()
    for i in range(nb_humains, min(4, nb_humains + 1)):
        joueurs.append(Robourrin(couleurs[i]))
    for i in range(min(4, nb_humains + 1), 4):
        joueurs.append(Robot(couleurs[i]))
    random.shuffle(joueurs)
    tracé = charger_parcours("parcours.json")

    for joueur in joueurs:
        joueur.client.couleur(joueur.couleur)
    # Placement initial
    joueurs[0].client.afficher(tracé, 0, tracé.départ)
    for joueur in joueurs:
        for joueur_en_attente in joueurs:
            if joueur_en_attente is not joueur:
                joueur_en_attente.client.attente(list([joueur.couleur.name]))
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
        for joueur_en_attente in joueurs:
            joueur_en_attente.client.afficher(tracé, 0, tracé.départ)

    # Course !
    fin_de_partie = False
    while not fin_de_partie:

        # Phase énergie
        paires = dict()
        tâches = dict()

        for joueur in joueurs:
            if (joueur not in paires and
                (joueur not in tâches or
                 not tâches[joueur].is_alive())):
                tâches[joueur] = threading.Thread(
                    target=lambda t, j, p: p.update([(j, j.jouer(t))]),
                    args=(tracé, joueur, paires))
                tâches[joueur].start()

        attendre_couleurs_precedentes = list(
            map(lambda j: j.couleur.name, joueurs))
        while True:
            time.sleep(1)
            attendre_couleurs = list()
            for joueur in joueurs:
                if joueur not in paires:
                    attendre_couleurs.append(joueur.couleur.name)
            if not attendre_couleurs:
                break
            else:
                if len([c for c in attendre_couleurs_precedentes
                        if c not in attendre_couleurs]):
                    for joueur in paires.keys():
                        joueur.client.attente(attendre_couleurs)
                    attendre_couleurs_precedentes = list(attendre_couleurs)

        # Phase de déplacement
        tracé.déplacer(paires)

        # Phase finale
        tracé.aspirer(joueurs)
        fatigués = tracé.fatiguer()
        for joueur in joueurs:
            joueur.client.afficher_fatigue(tracé, fatigués)

        # Détection de la fin de partie
        fin_de_partie = (max(tracé.positions.values()) >= tracé.arrivée)

    # Fin de la partie
    for joueur in joueurs:
        joueur.client.afficher(tracé)
        joueur.client.ordre(tracé.ordre())


def client_console(adresse, port):
    client = ClientConsole(adresse, port)
    client.jouer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    if len(sys.argv) == 2 or (len(sys.argv) > 2 and sys.argv[1] == '-c'):
        if len(sys.argv) == 3:
            client_console(socket.gethostname(), int(sys.argv[2]))
        elif len(sys.argv) == 4:
            client_console(sys.argv[2], int(sys.argv[3]))
        else:
            client_console(socket.gethostname(), int(sys.argv[1]))

    else:
        nb_humains = 1
        if len(sys.argv) > 2 and sys.argv[1] == '-h':
            nb_humains = min(4, max(1, int(sys.argv[2])))
        principal(nb_humains)
