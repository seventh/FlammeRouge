#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gpc.h"

int
main (void)
{
  gpc_polygon p1;
  gpc_polygon p2;
  gpc_polygon p3;
  gpc_vertex_list contour;

  memset (&p1, 0, sizeof (gpc_polygon));
  contour.num_vertices = 4;
  contour.vertex = malloc (4 * sizeof (gpc_vertex));
  contour.vertex[0].x = 0;
  contour.vertex[0].y = 0;
  contour.vertex[1].x = 7;
  contour.vertex[1].y = 0;
  contour.vertex[2].x = 7;
  contour.vertex[2].y = 7;
  contour.vertex[3].x = 0;
  contour.vertex[3].y = 7;
  gpc_add_contour (&p1, &contour, 0);
  free (contour.vertex);

  memset (&p2, 0, sizeof (gpc_polygon));
  contour.num_vertices = 3;
  contour.vertex = malloc (3 * sizeof (gpc_vertex));
  contour.vertex[0].x = 5;
  contour.vertex[0].y = 5;
  contour.vertex[1].x = 5;
  contour.vertex[1].y = 9;
  contour.vertex[2].x = 7;
  contour.vertex[2].y = 8;
  gpc_add_contour (&p2, &contour, 0);
  free (contour.vertex);

  memset (&p3, 0, sizeof (gpc_polygon));
  gpc_polygon_clip (GPC_XOR, &p1, &p2, &p3);
  gpc_write_polygon (stdout, 1, &p3);

  gpc_free_polygon (&p1);
  gpc_free_polygon (&p2);
  gpc_free_polygon (&p3);

  return 0;
}
