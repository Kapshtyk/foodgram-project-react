#!/bin/bash

while ! nc -z db 5432; do
    sleep 0.5
    echo "Waiting for the database..."
done
echo "Connected to the database"


python manage.py migrate
python manage.py loaddata database.json
python manage.py collectstatic --noinput
gunicorn -w 2 -b 0:8000 foodgram.wsgi
