FROM apache/airflow:2.6.0

ENV AIRFLOW_HOME=/usr/local/airflow

USER root

RUN usermod -u 1025 airflow
RUN groupadd -g 992 docker
RUN usermod -G docker airflow

USER airflow

ADD requirements.txt .
RUN pip install -r requirements.txt

USER root

RUN mkdir -p ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/plugins

COPY ./dags ${AIRFLOW_HOME}/dags
COPY ./logs ${AIRFLOW_HOME}/logs

RUN chown -R airflow: ${AIRFLOW_HOME}/{logs,dags,plugins}

RUN chown -R airflow: ${AIRFLOW_HOME}

EXPOSE 8080

USER airflow

WORKDIR ${AIRFLOW_HOME}