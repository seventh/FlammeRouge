#!/bin/bash

txtnet *.py */*.py
python3-autopep8 -i *.py */*.py
python3-flake8 *.py */*.py
