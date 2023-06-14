FROM python:3.9-slim

WORKDIR /app

COPY ./ .

RUN pip3 install -r backend/requirements.txt --no-cache-dir

RUN chmod +x backend/migrate_run_app.sh

ENTRYPOINT ["/app/backend/migrate_run_app.sh"]
