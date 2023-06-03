FROM python:3.9-slim

RUN apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]