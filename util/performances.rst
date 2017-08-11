Performance de l'encodage «trajet2»
===================================

Des bibliothèques Python de gestion des combinaisons, et plus particulièrement
permettant l'association d'un entier (dénommé «rang») à une combinaison
donnée. Le but est d'en trouver une qui soit plus performante (en temps) que
l'implémentation actuelle, même si la fonction de transfert n'est pas la même.

Comparatif
----------

Les temps mesurés sont ceux reportés par la commande suivante ::

  /usr/bin/time python3 agent.py

limité à la seule phase de conversion pour le premier million de codes.

version ad-hoc
``````````````

Déjà en place, les tests passent, nécessairement.

Temps d'exécution : 23,24s

trotter 0.8.0
`````````````

Mise-en-place aisée. Le test «test_trajet2.py» passe sans sourciller.

Temps d'exécution : 67,73s

combi 1.1.2
```````````

Mise-en-place aisée également. Par contre, deux tests ne passent pas :

  - testZéro
  - testMax

et ceci certainement parce que la fonction de transfert n'est pas la même que
celle implémentée dans «trajet2.py»

Temps d'exécution : 63,56s pour seulement 100.000 conversions !

Conclusion
----------

De façon assez décevante, mon code est le plus performant, et de loin.
