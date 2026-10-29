FROM python:3.11-slim

WORKDIR /usr/app/dbt

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir dbt-postgres==1.7.*

COPY dbt/ .

ENV DBT_PROFILES_DIR=/usr/app/dbt

# Reste actif pour permettre "docker-compose exec dbt dbt run"
CMD ["tail", "-f", "/dev/null"]
