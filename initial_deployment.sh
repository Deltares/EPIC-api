#!/bin/sh
# Author : Carles S. Soriano Perez (carles.sorianoperez@deltares.nl)
if [ $# -eq 0 ]
  then
    echo "No arguments supplied, first should be True / False for DEBUG variable"
    exit
fi

if ! [[ "$1" == "True" || "$1" == "False" ]] ; then
   echo "First argument should be True or False"
   exit
fi

poetry run python -c "import secrets; from pathlib import Path; Path('.django_secrets').write_text(secrets.token_hex(16))"
poetry run python -c "from pathlib import Path; Path('.django_debug').write_text('$1')"
poetry install

echo "Generating database structure and dropping previous entries / tables."
poetry run python3 manage.py epic_setup $2
echo "Re-generate static files."
poetry run python3 manage.py collectstatic --noinput
poetry run gunicorn epic_core.wsgi &