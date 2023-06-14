FROM python:3.9-slim

RUN apt-get update \
    && apt-get install -y locales netcat && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen

WORKDIR /app

COPY . .

RUN pwd

RUN ls -la

RUN pip3 install -r backend/requirements.txt --no-cache-dir

RUN chmod +x backend/migrate_run_app.sh

ENTRYPOINT ["/app/migrate_run_app.sh"]
