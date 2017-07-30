#!/bin/bash

PYS=$( find . -type f -name '*.py' )

txtnet $PYS
python3-autopep8 -i $PYS
python3-flake8 $PYS

CS=$( find . -type f -name '*.[ch]' )
indent -nut $CS
txtnet $CS
