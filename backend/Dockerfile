FROM python:3.9-slim

WORKDIR /app

COPY ./backend/ /app/backend/

RUN pip3 install -r /app/backend/requirements.txt --no-cache-dir

WORKDIR /app/backend

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
