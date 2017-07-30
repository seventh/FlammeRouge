#include <stdio.h>
#include <stddef.h>
#include "gpc.h"

typedef signed char i1;
typedef unsigned char u1;
typedef unsigned long long u8;
typedef size_t us;

#define SORTIE "trajets-c.bin"

#define TRAJET_LG 21
typedef struct
{
  i1 tuiles[TRAJET_LG];
} Trajet;


u8
coder (const Trajet * trajet)
{
  u8 _retour = 0;
  us _i = 0;

  for (_i = 1; _i < TRAJET_LG - 1; ++_i)
    {
      _retour *= 5;
      _retour += 2 + trajet->tuiles[_i];
    }

  return _retour;
}


void
ecrire_code (FILE * sortie, u8 code)
{
  /* RAPPELS :

     - Un code tient sur 6 octets
     - Il est écrit au format gros-boutisme
   */
  const u8 _masque = 0xFF;
  u1 _donnee = 0;
  us _i;

  for (_i = 0; _i < 6; ++_i)
    {
      _donnee = (code >> (8 * (5 - _i))) & _masque;
      fwrite (&_donnee, 1, 1, sortie);
    }
}


u8
lire_code (FILE * sortie)
{
  u8 _retour = 0;
  u1 _donnee = 0;
  us _i = 0;

  for (_i = 0; _i < 6; ++_i)
    {
      fread (&_donnee, 1, 1, sortie);
      _retour <<= 8;
      _retour += _donnee;
    }

  return _retour;
}


u8
dernier_code (void)
{
  u8 _retour = 0;
  FILE *sortie = fopen (SORTIE, "rb");
  us taille = 0;

  fseek (sortie, 0, SEEK_END);
  taille = ftell (sortie);

  fseek (sortie, -(6 + (taille % 6)), SEEK_CUR);

  _retour = lire_code (sortie);
  fclose (sortie);

  return _retour;
}

int
main (void)
{
  const Trajet t = { {0, -2, -2, -2, -2, -2, -2,
                      -1, -1, -1, -1, -1, -1, 0,
                      0, 0, 0, 0, 0, 0, 0}
  };
  u8 code = coder (&t);
  FILE *sortie = fopen (SORTIE, "w");

  ecrire_code (sortie, code);
  printf ("%llu\n", code);

  fclose (sortie);

  code = dernier_code ();
  printf ("%llu\n", code);

  return 0;
}
