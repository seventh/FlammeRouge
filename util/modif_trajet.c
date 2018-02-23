#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

static const char *ENTREE = "trajets-c.bin";

typedef char Enregistrement[10];

#define N 838860

int
verifier (const char *entree)
{
  int _retour = 1;
  FILE *_flux = fopen (entree, "rb");
  long _n = 0;
  size_t _i = 0;
  Enregistrement *_enregistrements = malloc (N * sizeof (Enregistrement));
  size_t _nb_lus = 0;

  while (1)
    {
      _nb_lus = fread (_enregistrements, sizeof (Enregistrement), N, _flux);
      if (_nb_lus == 0)
        {
          fprintf (stderr, "Fin de vérification\n");
          fflush (stderr);
          break;
        }
      for (_i = 0; _i < _nb_lus; ++_i)
        {
          if (_enregistrements[_i][6] != 0)
            {
              fprintf (stderr, "Octet utile ! %u\n", _enregistrements[_i][6]);
              fflush (stderr);
              _retour = 0;
              break;
            }
          _n += 1;
          if (_n % 10000000 == 0)
            {
              fprintf (stderr, "%zuM enregistrements vérifiés\n",
                       _n / 1000000);
              fflush (stderr);
            }
        }
    }

  fclose (_flux);
  free (_enregistrements);
  return _retour;
}


void
modifier (const char *chemin)
{
  FILE *_entree = fopen (chemin, "rb");
  FILE *_sortie = fopen (chemin, "r+b");
  Enregistrement _enregistrement;
  size_t _nb_lus = 0;
  long _n = 0;
  size_t _taille = 0;

  fseek (_entree, 7, SEEK_SET);
  fseek (_sortie, 6, SEEK_SET);

  // Parties conservées :
  // - fin de l'enregistrement N
  // - début de l'enregistrement N+1
  while (1)
    {
      _nb_lus = fread (_enregistrement, sizeof (Enregistrement), 1, _entree);
      if (_nb_lus != 1)
        {
          break;
        }
      fwrite (_enregistrement, 9, 1, _sortie);

      _n += 1;
      if (_n % 10000000 == 0)
        {
          fprintf (stderr, "%zuM enregistrements modifiés\n", _n / 1000000);
          fflush (stderr);
        }
    }

  // Fin du dernier enregistrement
  fread (_enregistrement, 3, 1, _entree);
  fwrite (_enregistrement, 3, 1, _sortie);

  // Troncature
  _taille = ftell (_sortie);
  fclose (_sortie);
  fclose (_entree);
  truncate (chemin, _taille);
}


int
main (void)
{
  if (verifier (ENTREE))
    {
      modifier (ENTREE);
    }

  return 0;
}
