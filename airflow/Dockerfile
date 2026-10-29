FROM apache/airflow:2.7.1-python3.11

COPY --chown=airflow:root airflow/requirements-airflow.txt /requirements-airflow.txt
RUN pip install --no-cache-dir -r /requirements-airflow.txt
