"""Codage alternatif d'un trajet, pour tenir sur 38 bits
"""

import random


NB_BITS = 38


def _c(n, k):
    retour = 1

    if k < n - k:
        nb = k + 1
        v = n - k
    else:
        nb = n - k + 1
        v = k

    for i in range(1, nb):
        v += 1
        retour = (retour * v) // i

    return retour


def _rang(combinaison, n):
    retour = 0

    i = 0
    v = 0
    while i < len(combinaison):
        if v < combinaison[i]:
            retour += _c(n - v - 1, len(combinaison) - i - 1)
        else:
            i += 1
        v += 1

    return retour


def coder(trajet):
    uns = list()
    deux = list()
    code1 = 0
    code2 = 0

    for i in range(1, 21):
        if abs(trajet[i]) == 1:
            uns.append(i - 1)
            code1 *= 2
            if trajet[i] > 0:
                code1 += 1
        elif abs(trajet[i]) == 2:
            deux.append(i - 1 - len(uns))
            code2 *= 2
            if trajet[i] > 0:
                code2 += 1

    retour = _rang(uns, 19)
    retour *= _c(13, 6)
    retour += _rang(deux, 13)
    retour *= 64
    retour += code1
    retour *= 64
    retour += code2

    return retour


def _combinaison(rang, n, p):
    retour = list()

    v = 0
    i = 0
    while i < p - 1:
        mur = _c(n - v - 1, p - i - 1)
        if rang >= mur:
            rang -= mur
        else:
            retour.append(v)
            i += 1
        v += 1
    if p > 0:
        retour.append(v + rang)

    return retour


def décoder(code):
    reste, code2 = divmod(code, 64)
    reste, code1 = divmod(reste, 64)
    rang1, rang2 = divmod(reste, _c(13, 6))
    pos1 = _combinaison(rang1, 19, 6)
    pos2 = _combinaison(rang2, 13, 6)

    val1 = list()
    val2 = list()
    for i in range(6):
        if code1 % 2 == 0:
            val1.append(-1)
        else:
            val1.append(1)
        code1 >>= 1

        if code2 % 2 == 0:
            val2.append(-2)
        else:
            val2.append(2)
        code2 >>= 1
    val1.reverse()
    val2.reverse()

    # Construction
    retour = [0]
    j = 0
    k = 0
    for i in range(20):
        if j < 6 and pos1[j] == i:
            retour.append(val1[j])
            j += 1
        elif k < 6 and pos2[k] + j == i:
            retour.append(val2[k])
            k += 1
        else:
            retour.append(0)

    return retour


if __name__ == "__main__":
    rang_max = _c(19, 6) * _c(13, 6) * 2**6 * 2**6
    code = random.randrange(rang_max)
    trajet = décoder(code)
    print(code, code == coder(trajet))
    print(trajet)
