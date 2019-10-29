FROM jupyter/base-notebook
USER jovyan
COPY *.ipynb ./
RUN jupyter-nbconvert --to=python "*.ipynb"

FROM frictionlessdata/datapackage-pipelines
RUN python3 -m pip install ipython
COPY --from=0 /home/jovyan/*.py ./
COPY ./export_all_groups.sh /etc/periodic/daily/
RUN chmod +x /etc/periodic/daily/*.sh

VOLUME ["/pipelines/data"]
ENV CKAN_API_KET "zzz"

ENTRYPOINT crond -f
