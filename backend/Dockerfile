FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

RUN chmod +x migrate_run_app.sh

ENTRYPOINT ["/app/migrate_run_app.sh"]
