FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN ls -la

RUN cd backend

RUN ls -la
RUN pwd

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram/foodgram.wsgi:application", "--bind", "0:8000" ]
