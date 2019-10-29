FROM jupyter/base-notebook
USER jovyan
COPY *.ipynb ./
RUN jupyter-nbconvert --to=python "*.ipynb"

FROM frictionlessdata/datapackage-pipelines
RUN python3 -m pip install ipython
RUN apk update && apk add bash
COPY --from=0 /home/jovyan/*.py ./
COPY *.sh ./
COPY crontabs /var/spool/cron/crontabs/root
RUN chmod +x *.sh

VOLUME ["/pipelines/data"]
ENV CKAN_API_KEY "zzz"

ENTRYPOINT crond -f -L /dev/stderr -d 6
