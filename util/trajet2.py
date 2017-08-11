"""Codage alternatif d'un trajet, pour tenir sur 38 bits
"""

NB_BITS = 38
CODE_GARDE = 190703665152


class memoize(dict):

    def __init__(self, func):
        self._func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        retour = self._func(*key)
        self[key] = retour
        return retour


@memoize
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

    lg = len(combinaison)
    i = 0
    v = 0
    while i < lg:
        if v < combinaison[i]:
            retour += _c(n - v - 1, lg - i - 1)
        else:
            i += 1
        v += 1

    return retour

def coder(trajet):
    uns = 6 * [-1]
    deux = 6 * [-1]
    code1 = 0
    code2 = 0

    j = 0
    k = 0
    for i in range(1, 21):
        if trajet[i] == -2:
            deux[k] = i - j - 1
            k += 1
            code2 *= 2
        elif trajet[i] == -1:
            uns[j] = i - 1
            j += 1
            code1 *= 2
        elif trajet[i] == 1:
            uns[j] = i - 1
            j += 1
            code1 *= 2
            code1 += 1
        elif trajet[i] == 2:
            deux[k] = i - j - 1
            k += 1
            code2 *= 2
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
