#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "gpc.h"

typedef signed char i1;
typedef unsigned char u1;
typedef unsigned long long u8;
typedef size_t us;

#define SORTIE "trajets-c.bin"

/* ===========================================================================
   TRAJET
   ======================================================================== */

#define TRAJET_LG 21
typedef struct
{
  i1 tuiles[TRAJET_LG];
} Trajet;

void
trajet_afficher (FILE * sortie, const Trajet * trajet)
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
  i1 piece;
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
magot_poser (Magot * magot, const Magot * reference, i1 type)
{
  memcpy (magot, reference, sizeof (Magot));
  magot->nombres[abs (type)] -= 1;
}


void
voie_init (Voie * voie, const Magot * magot)
{
  voie->lg = 0;

  if (magot->nombres[2] != 0)
    {
      voie->choix[voie->lg] = 2;
      voie->lg += 1;
    }
  if (magot->nombres[1] != 0)
    {
      voie->choix[voie->lg] = 1;
      voie->lg += 1;
    }
  if (magot->nombres[0] != 0)
    {
      voie->choix[voie->lg] = 0;
      voie->lg += 1;
    }
  if (magot->nombres[1] != 0)
    {
      voie->choix[voie->lg] = -1;
      voie->lg += 1;
    }
  if (magot->nombres[2] != 0)
    {
      voie->choix[voie->lg] = -2;
      voie->lg += 1;
    }
}


void
transfo0 (gpc_vertex * sortie, const gpc_vertex * entree,
          const gpc_vertex * ecart)
{
  sortie->x = ecart->x + entree->x;
  sortie->y = ecart->y + entree->y;
}

void
transfo1 (gpc_vertex * sortie, const gpc_vertex * entree,
          const gpc_vertex * ecart)
{
  sortie->x = ecart->x - entree->y;
  sortie->y = ecart->y + entree->x;
}


void
transfo2 (gpc_vertex * sortie, const gpc_vertex * entree,
          const gpc_vertex * ecart)
{
  sortie->x = ecart->x - entree->x;
  sortie->y = ecart->y - entree->y;
}


void
transfo3 (gpc_vertex * sortie, const gpc_vertex * entree,
          const gpc_vertex * ecart)
{
  sortie->x = ecart->x + entree->y;
  sortie->y = ecart->y - entree->x;
}

typedef void (Transfo) (gpc_vertex *, const gpc_vertex *, const gpc_vertex *);

Transfo *const TRANSFOS[] = { &transfo0, &transfo0,
  &transfo1, &transfo1,
  &transfo2, &transfo2,
  &transfo3, &transfo3,
};

#define VERTEX_LIST(nom, forme) const gpc_vertex_list nom = { sizeof(forme) / sizeof(gpc_vertex), (gpc_vertex*)forme }

/* Quart-droite */

const gpc_vertex FORME_m2_0[] = {
  {16, -16}, {15, -12}, {14, -8}, {11, -5}, {8, -2}, {4, -1}, {0, 0}, {0, 64},
  {9, 63}, {18, 62}, {26, 60}, {35, 56}, {43, 52}, {50, 47}, {57, 41},
  {63, 34}, {68, 27}, {72, 19}, {76, 10}, {78, 2}, {79, -7}, {80, -16},
};

VERTEX_LIST (SOMMETS_m2_0, FORME_m2_0);


const gpc_vertex FORME_m2_1[] = {
  {23, 0}, {68, 45}, {61, 51}, {54, 56}, {46, 60}, {37, 64}, {29, 66},
  {20, 67}, {11, 68}, {2, 67}, {-7, 66}, {-15, 64}, {-24, 60}, {58, 56},
  {51, 51}, {-45, 45}, {0, 0}, {3, 3}, {7, 4}, {11, 5}, {15, 4}, {19, 3},
};

VERTEX_LIST (SOMMETS_m2_1, FORME_m2_1);


/* Huitième-droite */

const gpc_vertex FORME_m1_0[] = {
  {43, -17}, {25, 0}, {0, 0}, {0, 64}, {51, 64}, {88, 28}
};

VERTEX_LIST (SOMMETS_m1_0, FORME_m1_0);


const gpc_vertex FORME_m1_1[] = {
  {43, 17}, {43, 81}, {-8, 81}, {-45, 45}, {0, 0}, {18, 17},
};

VERTEX_LIST (SOMMETS_m1_1, FORME_m1_1);


/* Rectiligne */

const gpc_vertex FORME_0_0[] = {
  {191, 0}, {191, 64}, {0, 64}, {0, 0},
};

VERTEX_LIST (SOMMETS_0_0, FORME_0_0);


const gpc_vertex FORME_0_1[] = {
  {135, 135}, {90, 180}, {-45, 45}, {0, 0},
};

VERTEX_LIST (SOMMETS_0_1, FORME_0_1);


/* Huitième-gauche */

const gpc_vertex FORME_p1_0[] = {
  {88, 36}, {43, 81}, {25, 64}, {0, 64}, {0, 0}, {51, 0},
};

VERTEX_LIST (SOMMETS_p1_0, FORME_p1_0);


const gpc_vertex FORME_p1_1[] = {
  {36, 88}, {-28, 88}, {-28, 63}, {-45, 45}, {0, 0}, {36, 36},
};

VERTEX_LIST (SOMMETS_p1_1, FORME_p1_1);


/* Quart-gauche */

const gpc_vertex FORME_p2_0[] = {
  {80, 80}, {16, 80}, {15, 76}, {14, 72}, {11, 69}, {8, 66}, {4, 65}, {0, 64},
  {0, 0}, {9, 1}, {18, 2}, {26, 4}, {35, 8}, {43, 12}, {50, 17}, {57, 23},
  {63, 30}, {68, 37}, {72, 45}, {76, 54}, {78, 62}, {79, 71},
};

VERTEX_LIST (SOMMETS_p2_0, FORME_p2_0);


const gpc_vertex FORME_p2_1[] = {
  {0, 113}, {-45, 68}, {-42, 65}, {-41, 61}, {-40, 57}, {-41, 53}, {-42, 49},
  {-45, 45}, {0, 0}, {6, 7}, {11, 14}, {15, 22}, {19, 31}, {21, 39}, {22, 48},
  {23, 57}, {22, 66}, {21, 75}, {19, 83}, {15, 92}, {11, 10}, {6, 17},
};

VERTEX_LIST (SOMMETS_p2_1, FORME_p2_1);


const gpc_vertex_list *const SOMMETS[5][2] = { {&SOMMETS_m2_0, &SOMMETS_m2_1},
{&SOMMETS_m1_0, &SOMMETS_m1_1},
{&SOMMETS_0_0, &SOMMETS_0_1},
{&SOMMETS_p1_0, &SOMMETS_p1_1},
{&SOMMETS_p2_0, &SOMMETS_p2_1},
};


void
piece_init (Piece * piece, i1 type, i1 angle, const gpc_vertex * ecart)
{
  Transfo *const transfo = TRANSFOS[angle];
  const gpc_vertex_list *const sommets = SOMMETS[type + 2][angle % 2];
  int _i = 0;

  piece->forme.num_contours = 1;
  piece->forme.hole = NULL;
  piece->forme.contour = malloc (sizeof (gpc_vertex_list));
  piece->forme.contour->num_vertices = sommets->num_vertices;
  piece->forme.contour->vertex =
    malloc (sommets->num_vertices * sizeof (gpc_vertex));
  for (_i = 0; _i < sommets->num_vertices; ++_i)
    {
      (*transfo) (piece->forme.contour->vertex + _i, sommets->vertex + _i,
                  ecart);
    }

  memcpy (&piece->jalon, piece->forme.contour->vertex, sizeof (gpc_vertex));
  piece->angle = (angle + type) % 8;
}


void
piece_free (Piece * piece)
{
  gpc_free_polygon (&piece->forme);
  piece->forme.num_contours = 0;
  piece->forme.hole = NULL;
  piece->forme.contour = NULL;
}


void
strate_depart (Strate * strate)
{
  const gpc_vertex _origine = { 0, 0 };
  Piece _piece;

  piece_init (&_piece, 0, 0, &_origine);
  strate->angle = _piece.angle;
  strate->jalon = _piece.jalon;
  strate->forme = _piece.forme;
  magot_init (&strate->magot);
  strate->piece = 0;
  voie_init (&strate->voies, &strate->magot);
}


void
strate_poser (Strate * strate, Strate * origine)
{
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
  u8 _code = lire_code (sortie);
  Trajet _trajet;
  us _i = 0;

  if (_code == 0)
    {
      /* Valeur spéciale : ce trajet n'est pas constructible */
      contexte->lg = 1;
      strate_depart (contexte->strates);

      for (_i = 1; _i < TRAJET_LG - 1; ++_i)
        {
          while (1)
            {
              strate_poser (contexte->strates + _i,
                            contexte->strates + _i - 1);
              break;
            }
        }
    }
  else
    {
      decoder (_code, &_trajet);
      trajet_afficher (stdout, &_trajet);
      fprintf (stdout, "\n");
    }
}

int
main (void)
{
  Contexte *contexte = malloc (sizeof (Contexte));
  FILE *sortie = NULL;
  Piece piece;
  const gpc_vertex origine = { 0, 0 };

  contexte->lg = 0;
  sortie = ouvrir_fichier (SORTIE);

  reprendre (contexte, sortie);
  piece_init (&piece, -2, 5, &origine);
  piece_free (&piece);

  fclose (sortie);
  free (contexte);
  return 0;
}
