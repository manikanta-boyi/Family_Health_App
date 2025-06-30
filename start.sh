#!/bin/bash

echo "Attempting to reset database migration history to head..."
flask db stamp head --no-create || {
    echo "Flask-Migrate stamp head FAILED. This means the DB might be looking for a revision not in the code."
    echo "We will proceed to try 'upgrade' but if it fails, a manual DB cleanup is needed."
}

echo "Attempting database upgrade..."
flask db upgrade || { echo "Database upgrade FAILED. Deployment aborted." ; exit 1; }
echo "Database upgrade successful. Starting Gunicorn."

gunicorn run:app