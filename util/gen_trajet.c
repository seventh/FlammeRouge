#include <signal.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include "gpc.h"

typedef signed char i1;
typedef unsigned char u1;
typedef unsigned int u4;
typedef unsigned long long u8;
typedef size_t us;

#define SORTIE "trajets-c.bin"

/* ===========================================================================
   AIRE
   ======================================================================== */

void
aire_ecrire (FILE * sortie, u4 aire)
{
  /* Gros-boutisme */
  const u8 _masque = 0xFF;
  u1 _donnee = 0;
  us _i;

  for (_i = 0; _i < 3; ++_i)
    {
      _donnee = (aire >> (8 * (2 - _i))) & _masque;
      fwrite (&_donnee, 1, 1, sortie);
    }
}


u4
aire_lire (FILE * entree)
{
  u8 _retour = 0;
  u1 _donnees[3];
  us _i = 0;
  us _nb = 0;

  _nb = fread (&_donnees, 1, sizeof (_donnees), entree);
  if (_nb < sizeof (_donnees))
    {
      fseek (entree, -_nb, SEEK_CUR);
    }
  else
    {
      for (_i = 0; _i < 3; ++_i)
        {
          _retour <<= 8;
          _retour += _donnees[_i];
        }
    }

  return _retour;
}


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

      if (_taille < 9)
        {
          fseek (_retour, 0, SEEK_SET);
        }
      else
        {
          fseek (_retour, -(9 + (_taille % 9)), SEEK_CUR);
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


int
trajet_est_minimal (const Trajet * trajet)
{
  int _retour = 1;

  us _i;

  /* On ne fait pas la comparaison avec le trajet symétrique. Ça devrait
     normalement être une condition d'arrêt du programme */

  /* Comparaison avec le trajet parcouru en sens inverse */
  _i = 0;
  while (_i < TRAJET_LG
         && trajet->tuiles[_i] == trajet->tuiles[TRAJET_LG - 1 - _i])
    {
      _i += 1;
    }
  if (_i < TRAJET_LG
      && trajet->tuiles[_i] > trajet->tuiles[TRAJET_LG - 1 - _i])
    {
      _retour = 0;
    }

  /* Comparaison avec le trajet symétrique parcouru en sens inverse */
  _i = 0;
  while (_i < TRAJET_LG
         && trajet->tuiles[_i] == -trajet->tuiles[TRAJET_LG - 1 - _i])
    {
      _i += 1;
    }
  if (_i < TRAJET_LG
      && trajet->tuiles[_i] > -trajet->tuiles[TRAJET_LG - 1 - _i])
    {
      _retour = 0;
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
transfo0 (gpc_vertex_list * sortie, const gpc_vertex_list * entree,
          const gpc_vertex * ecart)
{
  int _i = 0;

  while (_i < entree->num_vertices)
    {
      sortie->vertex[_i].x = ecart->x + entree->vertex[_i].x;
      sortie->vertex[_i].y = ecart->y + entree->vertex[_i].y;
      ++_i;
    }
}

void
transfo1 (gpc_vertex_list * sortie, const gpc_vertex_list * entree,
          const gpc_vertex * ecart)
{
  int _i = 0;

  while (_i < entree->num_vertices)
    {
      sortie->vertex[_i].x = ecart->x - entree->vertex[_i].y;
      sortie->vertex[_i].y = ecart->y + entree->vertex[_i].x;
      ++_i;
    }
}


void
transfo2 (gpc_vertex_list * sortie, const gpc_vertex_list * entree,
          const gpc_vertex * ecart)
{
  int _i = 0;

  while (_i < entree->num_vertices)
    {
      sortie->vertex[_i].x = ecart->x - entree->vertex[_i].x;
      sortie->vertex[_i].y = ecart->y - entree->vertex[_i].y;
      ++_i;
    }
}


void
transfo3 (gpc_vertex_list * sortie, const gpc_vertex_list * entree,
          const gpc_vertex * ecart)
{
  int _i = 0;

  while (_i < entree->num_vertices)
    {
      sortie->vertex[_i].x = ecart->x + entree->vertex[_i].y;
      sortie->vertex[_i].y = ecart->y - entree->vertex[_i].x;
      ++_i;
    }
}

typedef void (Transfo) (gpc_vertex_list *, const gpc_vertex_list *,
                        const gpc_vertex *);

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
  gpc_vertex_list contour;

  contour.num_vertices = sommets->num_vertices;
  contour.vertex = malloc (sommets->num_vertices * sizeof (gpc_vertex));
  (*transfo) (&contour, sommets, ecart);

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


int
piece_fusionner (Piece * res, Piece * tuile, Piece * trajet)
{
  int _retour = 0;
  gpc_polygon _croisement;
  int _i = 0;

  memset (&_croisement, 0, sizeof (gpc_polygon));
  gpc_polygon_clip (GPC_INT, &tuile->forme, &trajet->forme, &_croisement);
  if (_croisement.num_contours != 0)
    {
      gpc_free_polygon (&_croisement);
    }
  else
    {
      _retour = 1;
      for (_i = 0; _i < tuile->forme.num_contours; ++_i)
        {
          gpc_add_contour (&res->forme, tuile->forme.contour + _i, 0);
        }
      for (_i = 0; _i < trajet->forme.num_contours; ++_i)
        {
          gpc_add_contour (&res->forme, trajet->forme.contour + _i, 0);
        }
      memcpy (&res->jalon, &tuile->jalon, sizeof (gpc_vertex));
      res->angle = tuile->angle;
    }

  return _retour;
}


/* Aire de la boite de délimitation
 */
u8
piece_aire (const Piece * piece)
{
  u8 _retour = 0;
  gpc_vertex _cinf = { 0, 0 };
  gpc_vertex _csup = { 0, 0 };
  gpc_vertex _cplus = { 0, 0 };
  gpc_vertex _cmoins = { 0, 0 };
  double _res = 0.0;
  int _i = 0;
  int _j = 0;
  int _init = 1;

  for (_i = 0; _i < piece->forme.num_contours; ++_i)
    {
      for (_j = 0; _j < piece->forme.contour[_i].num_vertices; ++_j)
        {
          const gpc_vertex *_sommet = piece->forme.contour[_i].vertex + _j;

          if (_init)
            {
              _init = 0;
              memcpy (&_cinf, _sommet, sizeof (gpc_vertex));
              memcpy (&_csup, _sommet, sizeof (gpc_vertex));
              _cplus.x = _sommet->x + _sommet->y;
              _cplus.y = _sommet->x - _sommet->y;
              memcpy (&_cmoins, &_cplus, sizeof (gpc_vertex));
            }
          else
            {
              if (_sommet->x < _cinf.x)
                {
                  _cinf.x = _sommet->x;
                }
              else if (_sommet->x > _csup.x)
                {
                  _csup.x = _sommet->x;
                }

              if (_sommet->y < _cinf.y)
                {
                  _cinf.y = _sommet->y;
                }
              else if (_sommet->y > _csup.y)
                {
                  _csup.y = _sommet->y;
                }

              _res = _sommet->x + _sommet->y;
              if (_res < _cmoins.x)
                {
                  _cmoins.x = _res;
                }
              else if (_res > _cplus.x)
                {
                  _cplus.x = _res;
                }

              _res = _sommet->x - _sommet->y;
              if (_res < _cmoins.y)
                {
                  _cmoins.y = _res;
                }
              else if (_res > _cplus.y)
                {
                  _cplus.y = _res;
                }
            }
        }
    }

  _res = (_cplus.x - _cmoins.x) * (_cplus.y - _cmoins.y) / 2.0;
  _retour = (_csup.x - _cinf.x) * (_csup.y - _cinf.y);
  if (_res < _retour)
    {
      /* fprintf (stderr, "Le quart de tour est significatif !\n"); */
      /* fprintf (stderr, "0° = %llu | 45° = %lf\n", _retour, _res); */
      /* fflush (stderr); */

      _retour = _res;
    }

  return _retour;
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
  int _retour = 0;
  Piece _piece;
  int _statut = 0;

  piece_init (&_piece, 0, origine->piece.angle, &origine->piece.jalon);
  memset (&strate->piece.forme, 0, sizeof (gpc_polygon));
  _statut = piece_fusionner (&strate->piece, &_piece, &origine->piece);
  piece_free (&_piece);
  if (_statut)
    {
      _retour = 1;
      memset (&strate->magot, 0, sizeof (Magot));
      strate->tuile = 0;
      strate->voies.lg = 0;
    }

  return _retour;
}


int
strate_poser (Strate * strate, Strate * origine)
{
  int _retour = 0;
  i1 _tuile = 0;
  Piece _piece;
  int _statut = 0;

  while (origine->voies.lg != 0)
    {
      origine->voies.lg -= 1;
      _tuile = origine->voies.tuiles[origine->voies.lg];

      piece_init (&_piece, _tuile, origine->piece.angle,
                  &origine->piece.jalon);
      memset (&strate->piece.forme, 0, sizeof (gpc_polygon));
      _statut = piece_fusionner (&strate->piece, &_piece, &origine->piece);
      piece_free (&_piece);
      if (_statut)
        {
          _retour = 1;
          magot_poser (&strate->magot, &origine->magot, _tuile);
          strate->tuile = _tuile;
          voie_init (&strate->voies, &strate->magot);
          break;
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

  /* Pour assurer l'alignement */
  aire_lire (sortie);

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


void
compacter (const char *nom)
{
  FILE *_entree = NULL;
  FILE *_sortie = NULL;
  Trajet _trajet;
  u8 _code = 0;
  u8 _aire = 0;
  u8 _position = 0;
  u8 _nb_lus = 0;
  u8 _nb_ecrits = 0;

  _entree = fopen (nom, "rb");
  if (_entree == NULL)
    {
      return;
    }

  _sortie = fopen (nom, "r+b");

  /* Compactage */
  while (1)
    {
      _code = trajet_lire_code (_entree);
      if (_code == 0)
        {
          break;
        }
      _aire = aire_lire (_entree);
      _nb_lus += 1;

      trajet_decoder (_code, &_trajet);
      if (trajet_est_minimal (&_trajet))
        {
          trajet_ecrire_code (_sortie, _code);
          aire_ecrire (_sortie, _aire);
          _nb_ecrits += 1;
        }
    }
  _position = ftell (_sortie);

  fclose (_sortie);
  fclose (_entree);

  /* Césure du fichier initial à la bonne dimension */
  truncate (nom, _position);

  /* Bilan final */
  fprintf (stdout,
           "%lld enregistrements écrits pour %lld enregistrements lus\n",
           _nb_ecrits, _nb_lus);
}


int
main (void)
{
  Contexte contexte;
  FILE *sortie = NULL;
  Trajet trajet;
  us nb = 0;
  u8 code = 0;
  u8 _aire = 0;
  struct sigaction action;

  /* Compactage (optionnel) d'une ancienne sortie issue d'un programme moins
     optimisé */
  if (0)
    {
      compacter (SORTIE);
    }

  /* Début du programme de recherche */
  memset (&action, 0, sizeof (struct sigaction));
  action.sa_handler = &gestionnaire;
  sigaction (SIGINT, &action, NULL);

  contexte.lg = 0;
  sortie = trajet_ouvrir_fichier (SORTIE);

  contexte_reprendre (&contexte, sortie);
  nb = ftell (sortie) / 9;
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

      if (trajet_est_minimal (&trajet))
        {

          _aire = piece_aire (&contexte.strates[contexte.lg - 1].piece);
          code = trajet_coder (&trajet);
          trajet_ecrire_code (sortie, code);
          aire_ecrire (sortie, _aire);

          nb += 1;
          if (nb % 1000000 == 0)
            {
              fprintf (stdout, "%zuM | ", nb / 1000000);
              trajet_afficher (stdout, &trajet);
              fprintf (stdout, "\n");
              fflush (stdout);
            }
        }
    }

  fclose (sortie);
  return 0;
}
