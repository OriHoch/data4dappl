FROM python:2.7-alpine

RUN apk update &&\
    apk add --no-cache git ca-certificates openssh-client libressl-dev \
                       libxslt-dev libxml2-dev linux-headers build-base bash libffi-dev \
                       postgresql-dev python2-dev py-egenix-mx-base-dev &&\
    pip install --upgrade pip &&\
    pip install --upgrade gunicorn 'lxml>=3.2' psycopg2

RUN mkdir -p /usr/lib/ckan/datapusher/src &&\
    cd /usr/lib/ckan/datapusher/src &&\
    # git clone -b 0.0.14 https://github.com/ckan/datapusher.git &&\
    git clone -b master https://github.com/OriHoch/datapusher.git &&\
    cd datapusher &&\
    pip install -r requirements.txt &&\
    python setup.py develop

RUN pip install --upgrade requests[security]

COPY wsgi.py /usr/lib/ckan/datapusher/src/datapusher/

WORKDIR /usr/lib/ckan/datapusher/src/datapusher

RUN echo "import os; MAX_CONTENT_LENGTH = int(os.environ.get('DATAPUSHER_MAX_CONTENT_LENGTH', '102400000'))" \
        >> deployment/datapusher_settings.py &&\
    echo "SQLALCHEMY_DATABASE_URI = os.environ.get('DATAPUSHER_SQLALCHEMY_URI', 'sqlite:////tmp/job_store.db')" \
        >> deployment/datapusher_settings.py

RUN adduser -h /usr/lib/ckan/datapusher/src/datapusher -s /bin/false -u 908 -D datapusher &&\
    chown -R datapusher:datapusher /usr/lib/ckan/datapusher/src/datapusher &&\
    touch /tmp/job_store.db && chown datapusher:datapusher /tmp/job_store.db

ENTRYPOINT ["gunicorn" ,"-b", "0.0.0.0:8800", "wsgi"]

USER datapusher
EXPOSE 8800
