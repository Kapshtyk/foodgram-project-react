#!/bin/bash

gunicorn -w 2 -b 0:8000 backend.foodgram.wsgi
