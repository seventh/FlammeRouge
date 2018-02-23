#!/bin/bash -x

CFLAGS="-W -Wall -O3"
CPPFLAGS=""

gcc $CPPFLAGS $CFLAGS modif_trajet.c -o modif_trajet
