#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
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

#define MAGOT_LG 3
typedef struct
{
  us nombres[MAGOT_LG];
} Magot;

typedef struct
{
  gpc_polygon forme;
  gpc_vertex jalon;
  i1 angle;
} Piece;

#define VOIE_LG (MAGOT_LG * 2 - 1)
typedef struct
{
  us lg;
  i1 choix[VOIE_LG];
} Voie;

typedef struct
{
  i1 angle;
  gpc_vertex jalon;
  gpc_polygon forme;
  Magot magot;
  Piece piece;
  Voie voies;
} Strate;

typedef struct
{
  us lg;
  Strate strates[TRAJET_LG];
} Contexte;

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
magot_init (Magot * magot)
{
  magot->nombres[0] = 7;
  magot->nombres[1] = 6;
  magot->nombres[2] = 6;
}


void
transfo0 (gpc_vertex * sortie, const gpc_vertex * entree)
{
  sortie->x = entree->x;
  sortie->y = entree->y;
}

void
transfo1 (gpc_vertex * sortie, const gpc_vertex * entree)
{
  sortie->x = -entree->y;
  sortie->y = entree->x;
}


void
transfo2 (gpc_vertex * sortie, const gpc_vertex * entree)
{
  sortie->x = -entree->x;
  sortie->y = -entree->y;
}


void
transfo3 (gpc_vertex * sortie, const gpc_vertex * entree)
{
  sortie->x = entree->y;
  sortie->y = -entree->x;
}

typedef void (Transfo) (gpc_vertex *, const gpc_vertex *);

Transfo *const TRANSFOS[] = { &transfo0, &transfo0,
  &transfo1, &transfo1,
  &transfo2, &transfo2,
  &transfo3, &transfo3,
};


void
piece_init (Piece * piece, i1 type, i1 angle, const gpc_vertex * ecart)
{
  Transfo *const transfo = TRANSFOS[angle];

  switch (type)
    {
    case -2:
      break;
    case -1:
      break;
    case 0:
      break;
    case 1:
      break;
    case 2:
      break;
    }
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


void
reprendre (Contexte * contexte, FILE * sortie)
{
  u8 code = lire_code (sortie);
  Trajet trajet;

  if (code == 0)
    {
      /* Valeur spéciale : ce trajet n'est pas constructible */
      contexte->lg = 1;
      contexte->strates[0].angle = 0;
    }
  else
    {
      decoder (code, &trajet);
      afficher_trajet (stdout, &trajet);
      fprintf (stdout, "\n");
    }
}

int
main (void)
{
  Contexte *contexte = malloc (sizeof (Contexte));
  FILE *sortie = NULL;

  contexte->lg = 0;
  sortie = ouvrir_fichier (SORTIE);

  reprendre (contexte, sortie);

  fclose (sortie);
  free (contexte);
  return 0;
}
