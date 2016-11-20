Flamme Rouge
============

This is a quick-and-dirty implementation of the `Flamme Rouge`_ board game.

It is distributed under the terms of the `CeCILL 2.1`_ license.

.. _Flamme Rouge: http://www.lautapelit.fi

.. _CeCILL 2.1: http://www.cecill.info

Requirements
------------

You'll need a running `Python 3`_ interpreter.

.. _Python 3: http://www.python.org

Command line arguments
----------------------

-c port            Launch as client, connecting to server at specified port.
                   If required, a network address may be prepended.
-h nb_humans       Launch as server, specifies number of humans players
                   (including playing on the server command line).

How to play
-----------

You are the **grey** (gris) player. Your team competes against three other
ones: the blue (bleu) one, the green (vert) one and the black (noir) one.

::

    +~~~~+<<<<+<<<<+<<<<+<<<<+<<<<+<<<<+<<<<+>>>>+>>>>+>>>>+>>>>+>>>>+~~~~+
    | Sn |    |    |    |    |    |    |    |    |    | →→ |    | →→ |    |
    +----+----+----+----+----+----+----+----+----+----+----+----+----+----+
    | Sv |    |    | Rn |    |    |    | Sg | Rv | Rg | →→ | Rb | →→ | Sb |
    +====+<<<<+<<<<+<<<<+<<<<+<<<<+<<<<+<<<<+>>>>+>>>>+>>>>+>>>>+>>>>+====+
    | 35 | 36 | 37 | 38 | 39 | 40 | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 |
     Prochain point d'étape au km 62 : ascension de 12 km
    Équipe bleue : fatigue du sprinteur
    Équipe grise : fatigue du sprinteur <---
    Équipe noire : fatigue du rouleur et du sprinteur
    Équipe verte : fatigue du sprinteur

Each team is composed of a Sprinteur and a Rouleur, so that each member of a
team is shown as a digram. For example, 'Rb' stands for the blue Runner, 'Sg'
for the grey Sprinter, and so on.

The first team to reach the finish line end the race!

For more information, read the `rules`_ of the board game.

.. _rules: http://www.lautapelit.fi/documents/key20161105180137/pelien%20liitetiedostoja/flamme-rouge-rulebook-eng-2016-06-23-web.pdf
