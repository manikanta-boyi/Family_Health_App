#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo ">>> Applying database migrations..."
# This command will create tables if the database is empty and apply any new migrations.
flask db upgrade

echo ">>> Starting the Gunicorn server..."
# The 'exec' command replaces the current shell with gunicorn, which is more efficient.
exec gunicorn -w 4 -b 0.0.0.0:10000 run:app
