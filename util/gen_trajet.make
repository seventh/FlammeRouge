#!/bin/bash -x

# CFLAGS="-W -Wall -g -ggdb"
CFLAGS="-W -Wall -O3"

CPPFLAGS="-Igpc"

gcc $CPPFLAGS $CFLAGS gpc/gpc.c gen_trajet.c -o gen_trajet
