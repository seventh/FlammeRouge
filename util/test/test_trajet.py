#!/usr/bin/env python3

import random
import unittest

import trajet


class TestCombi(unittest.TestCase):

    def testCR(self):
        max_rang = trajet._c(49, 6)
        rang = random.randrange(max_rang)
        combi = trajet._combinaison(rang, 49, 6)
        self.assertEqual(len(combi), 6)
        rang_final = trajet._rang(combi, 49)
        self.assertEqual(rang_final, rang)

    def testZéro(self):
        combi = [0, 1, 2, 3, 4, 5]
        rang = trajet._rang(combi, 49)
        self.assertEqual(rang, 0)
        combi_final = trajet._combinaison(rang, 49, 6)
        self.assertEqual(combi_final, combi)

    def testMax(self):
        combi = [43, 44, 45, 46, 47, 48]
        rang = trajet._rang(combi, 49)
        self.assertEqual(rang, trajet._c(49, 6) - 1)
        combi_final = trajet._combinaison(rang, 49, 6)
        self.assertEqual(combi_final, combi)

    def testTout(self):
        pred = None
        for rang in range(trajet._c(10, 5)):
            combi = trajet._combinaison(rang, 10, 5)
            self.assertEqual(len(combi), 5)
            if pred is not None:
                self.assertTrue(combi > pred)
            pred = combi
            rang_final = trajet._rang(combi, 10)
            self.assertEqual(rang_final, rang)


class TestCodage(unittest.TestCase):

    def testAléatoire(self):
        code = random.randrange(trajet.CODE_GARDE)
        t = trajet.décoder(code)
        self.assertEqual(len(t), 21)
        self.assertEqual(t.count(2) + t.count(-2), 6)
        self.assertEqual(t.count(1) + t.count(-1), 6)

        code_final = trajet.coder(t)
        self.assertEqual(code_final, code)


if __name__ == "__main__":
    unittest.main()
