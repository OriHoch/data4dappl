# Contributing to מידע לעם

* Welcome to מידע לעם
* Contributions of any kind are welcome.

## odata pipelines development workflow

```
conda env create -f pipelines-environment.yaml
conda activate data4dappl-pipelines
python3 -m pip install -U https://github.com/OriHoch/datapackage-pipelines/archive/dataflows-http-headers.zip &&\
python3 -m pip install -U https://github.com/OriHoch/datapackage-pipelines-ckan/archive/support-multiple-datasets-headers-translated-error-message.zip &&\
python3 -m pip install -U dataflows
```
