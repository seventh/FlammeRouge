#!/usr/bin/python3

import agent
import trajet


ENTRÉE = "trajets2.bin"
SORTIE = "trajets2-net.bin"


if __name__ == "__main__":
    dernier_code = None
    dernier_trajet = None
    with open(ENTRÉE, "r+b") as entrée:
        l = agent.Lecteur(entrée, trajet.NB_BITS)
        with open(SORTIE, "w+b") as sortie:
            m = agent.Metteur(sortie, trajet.NB_BITS)

            while True:
                code = l.lit()
                if code is None:
                    m.met(dernier_code)
                    break
                else:
                    t = trajet.décoder(code)
                    if dernier_code is None:
                        dernier_code = code
                        dernier_trajet = t
                    elif dernier_trajet < t:
                        m.met(dernier_code)
                        dernier_code = code
                        dernier_trajet = t
                    else:
                        print("Suppression de {}".format(t))
