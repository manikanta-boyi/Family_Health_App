#!/bin/bash

# This will stamp the database with your current revision ID
# Do this only once on a fresh deploy to fix the history mismatch
flask db stamp head

# Now, exit the script so the container doesn't try to start the app
exit 0
