#!/bin/bash
set -e
echo ">>> Applying database migrations..."
flask db upgrade
echo ">>> Starting the Gunicorn server..."
exec gunicorn -w 4 -b 0.0.0.0:10000 run:app