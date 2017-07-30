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
decoder (u8 code, Trajet * trajet)
{
  us _i = 0;

  trajet->tuiles[TRAJET_LG - 1] = 0;
  for (_i = TRAJET_LG - 2; _i > 0; --_i)
    {
      trajet->tuiles[_i] = code % 5 - 2;
      code /= 5;
    }
  trajet->tuiles[0] = 0;
}


void
afficher_trajet (FILE * sortie, const Trajet * trajet)
{
  us _i = 0;

  fprintf (sortie, "[");
  for (_i = 0; _i < TRAJET_LG; ++_i)
    {
      fprintf (sortie, "%d", trajet->tuiles[_i]);
      if (_i == TRAJET_LG - 1)
        {
          fprintf (sortie, "]");
        }
      else
        {
          fprintf (sortie, ", ");
        }
    }
}


/* Ouvre le fichier de résultat et le fait pointer sur le dernier
   enregistrement disponible
 */
FILE *
ouvrir_fichier (const char *nom)
{
  FILE *_retour = NULL;
  us _taille = 0;

  _retour = fopen (nom, "r+b");
  if (_retour == NULL)
    {
      _retour = fopen (nom, "w+b");
    }
  else
    {
      fseek (_retour, 0, SEEK_END);
      _taille = ftell (_retour);

      if (_taille < 6)
        {
          fseek (_retour, 0, SEEK_SET);
        }
      else
        {
          fseek (_retour, -(6 + (_taille % 6)), SEEK_CUR);
        }
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
  u1 _donnees[6];
  us _i = 0;
  us _nb = 0;

  _nb = fread (&_donnees, 1, sizeof (_donnees), sortie);
  if (_nb < sizeof (_donnees))
    {
      fseek (sortie, -_nb, SEEK_CUR);
    }
  else
    {
      for (_i = 0; _i < 6; ++_i)
        {
          _retour <<= 8;
          _retour += _donnees[_i];
        }
    }

  return _retour;
}


int
main (void)
{
  const Trajet t = { {0, -2, -2, -2, -2, -2, -2,
                      -1, -1, -1, -1, -1, -1, 0,
                      0, 0, 0, 0, 0, 0, 0}
  };
  Trajet t2 = { {1, 2, 3, 4, 5, 6, 7,
                 8, 9, 10, 11, 12, 13, 14,
                 15, 16, 17, 18, 19, 20, 21}
  };

  u8 code = coder (&t);
  FILE *sortie = ouvrir_fichier (SORTIE);

  code = lire_code (sortie);
  printf ("%llu\n", code);

  code = coder (&t);
  ecrire_code (sortie, code);

  afficher_trajet (stdout, &t);
  fprintf (stdout, "\n");

  decoder (code, &t2);
  afficher_trajet (stdout, &t2);
  fprintf (stdout, "\n");

  fclose (sortie);
  return 0;
}
