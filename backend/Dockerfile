FROM python:3.9-slim

WORKDIR /app

COPY ./ .

RUN cd backend

RUN pip3 install -r backend/requirements.txt --no-cache-dir

CMD ["gunicorn", "backend/foodgram.wsgi:application", "--bind", "0:8000" ]
