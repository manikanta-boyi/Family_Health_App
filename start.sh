echo "Attempting database upgrade..."
flask db upgrade || { echo "Database upgrade FAILED. Deployment aborted." ; exit 1; }
echo "Database upgrade successful. Starting Gunicorn."

gunicorn run:app