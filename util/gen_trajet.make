#!/bin/bash -x

CFLAGS="-W -Wall -g"
CPPFLAGS="-Igpc"

gcc $CPPFLAGS $CFLAGS gpc/gpc.c gen_trajet.c -o gen_trajet
