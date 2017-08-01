#include <stdio.h>
#include <string.h>
#include "json.h"

int
main (void)
{
  json_object *jobj = NULL;
  char mystring[12];
  int stringlen = 0;
  struct json_tokener *tok = json_tokener_new ();
  enum json_tokener_error jerr;
  FILE *entree = NULL;
  int n = 0;

  entree = fopen ("formes.json", "rt");
  do
    {
      n = fread (mystring, sizeof (mystring) - 1, 1, entree);
      mystring[sizeof (mystring) - 1] = '\0';
      stringlen = strlen (mystring);
      jobj = json_tokener_parse_ex (tok, mystring, stringlen);
    }
  while ((jerr = json_tokener_get_error (tok)) == json_tokener_continue);
  if (jerr != json_tokener_success)
    {
      fprintf (stderr, "Error: %s\n", json_tokener_error_desc (jerr));
      // Handle errors, as appropriate for your application.
    }
  if (tok->char_offset < stringlen)     // XXX shouldn't access internal fields
    {
      // Handle extra characters after parsed object as desired.
      // e.g. issue an error, parse another object from that point, etc...
    }
// Success, use jobj here.
  json_tokener_free (tok);
  fclose (entree);

  /* autre version */
  json_object *jobj2 = json_object_from_file ("formes.json");

  fprintf (stdout, json_object_to_json_string (jobj));
  return 0;
}
