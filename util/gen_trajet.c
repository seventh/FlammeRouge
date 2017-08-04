#include <signal.h>
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


u8
trajet_coder (const Trajet * trajet)
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
trajet_decoder (u8 code, Trajet * trajet)
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


/* Ouvre le fichier de résultat et le fait pointer sur le dernier
   enregistrement disponible
 */
FILE *
trajet_ouvrir_fichier (const char *nom)
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
trajet_ecrire_code (FILE * sortie, u8 code)
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
trajet_lire_code (FILE * sortie)
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


/* ===========================================================================
   MAGOT
   ======================================================================== */

#define MAGOT_LG 3
typedef struct
{
  us nombres[MAGOT_LG];
} Magot;

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
  const us clef = abs (type);

  memcpy (magot, reference, sizeof (Magot));
  magot->nombres[clef] -= 1;
}


/* ===========================================================================
   PIÈCE
   ======================================================================== */

typedef struct
{
  gpc_polygon forme;
  gpc_vertex jalon;
  i1 angle;
} Piece;

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
  {20, 67}, {11, 68}, {2, 67}, {-7, 66}, {-15, 64}, {-24, 60}, {-32, 56},
  {-39, 51}, {-45, 45}, {0, 0}, {3, 3}, {7, 4}, {11, 5}, {15, 4}, {19, 3},
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
  {23, 57}, {22, 66}, {21, 75}, {19, 83}, {15, 92}, {11, 100}, {6, 107},
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
  gpc_vertex_list contour;

  contour.num_vertices = sommets->num_vertices;
  contour.vertex = malloc (sommets->num_vertices * sizeof (gpc_vertex));
  for (_i = 0; _i < sommets->num_vertices; ++_i)
    {
      (*transfo) (contour.vertex + _i, sommets->vertex + _i, ecart);
    }

  memset (&piece->forme, 0, sizeof (gpc_polygon));
  gpc_add_contour (&piece->forme, &contour, 0);

  memcpy (&piece->jalon, contour.vertex, sizeof (gpc_vertex));
  piece->angle = (8 + angle + type) % 8;

  free (contour.vertex);
}


void
piece_free (Piece * piece)
{
  gpc_free_polygon (&piece->forme);
}


/* ===========================================================================
   VOIE
   ======================================================================== */

#define VOIE_LG (MAGOT_LG * 2 - 1)
typedef struct
{
  us lg;
  i1 tuiles[VOIE_LG];
} Voie;

void
voie_init (Voie * voie, const Magot * magot)
{
  voie->lg = 0;

  if (magot->nombres[2] != 0)
    {
      voie->tuiles[voie->lg] = 2;
      voie->lg += 1;
    }
  if (magot->nombres[1] != 0)
    {
      voie->tuiles[voie->lg] = 1;
      voie->lg += 1;
    }
  if (magot->nombres[0] != 0)
    {
      voie->tuiles[voie->lg] = 0;
      voie->lg += 1;
    }
  if (magot->nombres[1] != 0)
    {
      voie->tuiles[voie->lg] = -1;
      voie->lg += 1;
    }
  if (magot->nombres[2] != 0)
    {
      voie->tuiles[voie->lg] = -2;
      voie->lg += 1;
    }
}


/* ===========================================================================
   STRATE
   ======================================================================== */

typedef struct
{
  Piece piece;
  Magot magot;
  i1 tuile;
  Voie voies;
} Strate;

void
strate_depart (Strate * strate)
{
  const gpc_vertex _origine = { 0, 0 };

  piece_init (&strate->piece, 0, 0, &_origine);
  magot_init (&strate->magot);
  strate->tuile = 0;
  voie_init (&strate->voies, &strate->magot);
}


int
strate_arrivee (Strate * strate, Strate * origine)
{
  int _retour = 1;
  Piece piece;
  gpc_polygon croisement;

  piece_init (&piece, 0, origine->piece.angle, &origine->piece.jalon);
  memset (&croisement, 0, sizeof (gpc_polygon));
  gpc_polygon_clip (GPC_INT, &piece.forme, &origine->piece.forme,
                    &croisement);
  if (croisement.num_contours == 0)
    {
      memset (&strate->piece.forme, 0, sizeof (gpc_polygon));
      gpc_polygon_clip (GPC_UNION, &piece.forme, &origine->piece.forme,
                        &strate->piece.forme);
      memcpy (&strate->piece.jalon, &piece.jalon, sizeof (gpc_vertex));
      strate->piece.angle = piece.angle;
      memset (&strate->magot, 0, sizeof (Magot));
      strate->tuile = 0;
      strate->voies.lg = 0;
    }
  else
    {
      _retour = 0;
      gpc_free_polygon (&croisement);
    }
  piece_free (&piece);

  return _retour;
}


int
strate_poser (Strate * strate, Strate * origine)
{
  int _retour = 0;
  i1 tuile = 0;
  Piece piece;
  gpc_polygon croisement;
  int _i = 0;

  while (origine->voies.lg != 0)
    {
      origine->voies.lg -= 1;
      tuile = origine->voies.tuiles[origine->voies.lg];

      piece_init (&piece, tuile, origine->piece.angle, &origine->piece.jalon);
      memset (&croisement, 0, sizeof (gpc_polygon));
      gpc_polygon_clip (GPC_INT, &piece.forme, &origine->piece.forme,
                        &croisement);
      if (croisement.num_contours == 0)
        {
          /* in fine, on doit pouvoir supprimer cette ligne */
          memset (&strate->piece.forme, 0, sizeof (gpc_polygon));
          for (_i = 0; _i < piece.forme.num_contours; ++_i)
            {
              gpc_add_contour (&strate->piece.forme, &piece.forme.contour[_i],
                               0);
            }
          for (_i = 0; _i < origine->piece.forme.num_contours; ++_i)
            {
              gpc_add_contour (&strate->piece.forme,
                               &origine->piece.forme.contour[_i], 0);
            }
          memcpy (&strate->piece.jalon, &piece.jalon, sizeof (gpc_vertex));
          strate->piece.angle = piece.angle;
          magot_poser (&strate->magot, &origine->magot, tuile);
          strate->tuile = tuile;
          voie_init (&strate->voies, &strate->magot);
          piece_free (&piece);
          _retour = 1;
          break;
        }
      else
        {
          _retour = 0;
          gpc_free_polygon (&croisement);
          piece_free (&piece);
        }
    }
  return _retour;
}


/* ===========================================================================
   CONTEXTE
   ======================================================================== */

typedef struct
{
  us lg;
  Strate strates[TRAJET_LG];
} Contexte;


void
contexte_trajet (Trajet * trajet, const Contexte * contexte)
{
  us _i = 0;

  for (_i = 0; _i < contexte->lg; ++_i)
    {
      trajet->tuiles[_i] = contexte->strates[_i].tuile;
    }
}


void
contexte_reprendre (Contexte * contexte, FILE * sortie)
{
  u8 _code = trajet_lire_code (sortie);
  Trajet _trajet;
  us _i = 0;

  memset (contexte, 0, sizeof (Contexte));
  contexte->lg = 1;
  strate_depart (contexte->strates);

  if (_code == 0)
    {
      /* Valeur spéciale : ce trajet n'est pas constructible */
      /* On pose deux tuiles fictives */
      strate_arrivee (contexte->strates + 1, contexte->strates);
      strate_arrivee (contexte->strates + 2, contexte->strates);
      contexte->lg += 2;
    }
  else
    {
      trajet_decoder (_code, &_trajet);

      for (_i = 1; _i < TRAJET_LG - 1; ++_i)
        {
          while (1)
            {
              strate_poser (&contexte->strates[_i],
                            &contexte->strates[_i - 1]);
              if (contexte->strates[_i].tuile != _trajet.tuiles[_i])
                {
                  piece_free (&contexte->strates[_i].piece);
                }
              else
                {
                  break;
                }
            }
        }

      strate_arrivee (&contexte->strates[TRAJET_LG - 1],
                      &contexte->strates[TRAJET_LG - 2]);
      contexte->lg = TRAJET_LG;
    }
}


int
contexte_prochain (Contexte * contexte)
{
  int _retour = 1;
  int statut = 0;

  /* Suppression de l'arrivée */
  contexte->lg -= 1;
  piece_free (&contexte->strates[contexte->lg].piece);

  /* Itérations de recherche jusqu'au prochain contexte complet */
  while (1)
    {
      /* Suppression de la dernière strate variable */
      contexte->lg -= 1;
      piece_free (&contexte->strates[contexte->lg].piece);

      while (contexte->lg > 0 && contexte->lg < TRAJET_LG - 1)
        {
          statut =
            strate_poser (&contexte->strates[contexte->lg],
                          &contexte->strates[contexte->lg - 1]);
          if (statut == 1)
            {
              contexte->lg += 1;
            }
          else
            {
              contexte->lg -= 1;
              piece_free (&contexte->strates[contexte->lg].piece);
            }
        }
      if (contexte->lg == 0)
        {
          _retour = 0;
        }
      else
        {
          /* Ajout de l'arrivée si possible */
          statut = strate_arrivee (&contexte->strates[contexte->lg],
                                   &contexte->strates[contexte->lg - 1]);
          if (statut)
            {
              contexte->lg += 1;
              break;
            }
        }
    }

  return _retour;
}


/* ===========================================================================
   PROGRAMME PRINCIPAL
   ======================================================================== */

int cont = 1;

void
gestionnaire (int signal __attribute__ ((unused)))
{
  cont = 0;
}


int
main (void)
{
  Contexte contexte;
  FILE *sortie = NULL;
  Trajet trajet;
  us nb = 0;
  u8 code = 0;
  struct sigaction action;

  memset (&action, 0, sizeof (struct sigaction));
  action.sa_handler = &gestionnaire;
  sigaction (SIGINT, &action, NULL);

  contexte.lg = 0;
  sortie = trajet_ouvrir_fichier (SORTIE);

  contexte_reprendre (&contexte, sortie);
  nb = ftell (sortie) / 6;
  if (nb != 0)
    {
      contexte_trajet (&trajet, &contexte);
      fprintf (stdout, "%zu | ", nb);
      trajet_afficher (stdout, &trajet);
      fprintf (stdout, "\n");
      fflush (stdout);
    }

  while (contexte_prochain (&contexte) && cont != 0)
    {
      contexte_trajet (&trajet, &contexte);
      code = trajet_coder (&trajet);
      trajet_ecrire_code (sortie, code);

      nb += 1;
      if (nb % 100000 == 0)
        {
          fprintf (stdout, "%.1fM | ", (float) nb / 1000000);
          trajet_afficher (stdout, &trajet);
          fprintf (stdout, "\n");
          fflush (stdout);
        }
    }

  fclose (sortie);
  return 0;
}
