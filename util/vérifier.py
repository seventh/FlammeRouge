#!/usr/bin/python3

import agent
import trajet2


ENTRÉE = "trajets2.bin"
SORTIE = "trajets2-net.bin"


if __name__ == "__main__":
    dernier_code = None
    dernier_trajet = None
    with open(ENTRÉE, "r+b") as entrée:
        l = agent.Lecteur(entrée, trajet2.NB_BITS)
        with open(SORTIE, "w+b") as sortie:
            m = agent.Metteur(sortie, trajet2.NB_BITS)

            while True:
                code = l.lit()
                if code is None:
                    m.met(dernier_code)
                    break
                elif code >= trajet2.CODE_GARDE:
                    print("Code erroné : {}".format(code))
                    break
                else:
                    t = trajet2.décoder(code)
                    if dernier_code is None:
                        dernier_code = code
                        dernier_trajet = t
                    elif dernier_trajet < t:
                        m.met(dernier_code)
                        dernier_code = code
                        dernier_trajet = t
                    else:
                        print("Suppression de {}".format(t))
                        break
