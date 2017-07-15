#!/usr/bin/env python3

import random
import unittest

import trajet2


class TestCombi(unittest.TestCase):

    def testCR(self):
        max_rang = trajet2._c(49, 6)
        rang = random.randrange(max_rang)
        combi = trajet2._combinaison(rang, 49, 6)
        self.assertEqual(len(combi), 6)
        rang_final = trajet2._rang(combi, 49)
        self.assertEqual(rang_final, rang)

    def testZéro(self):
        combi = [0, 1, 2, 3, 4, 5]
        rang = trajet2._rang(combi, 49)
        self.assertEqual(rang, 0)
        combi_final = trajet2._combinaison(rang, 49, 6)
        self.assertEqual(combi_final, combi)

    def testMax(self):
        combi = [43, 44, 45, 46, 47, 48]
        rang = trajet2._rang(combi, 49)
        self.assertEqual(rang, trajet2._c(49, 6) - 1)
        combi_final = trajet2._combinaison(rang, 49, 6)
        self.assertEqual(combi_final, combi)


if __name__ == "__main__":
    unittest.main()
