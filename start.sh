#!/bin/bash

echo ">>> Setting up database..."

echo ">>> Faking migration history..."
flask db stamp head

echo ">>> Attempting upgrade..."
flask db upgrade

echo ">>> Starting the app..."
exec gunicorn -w 4 -b 0.0.0.0:10000 run:app  # or however you start Flask
