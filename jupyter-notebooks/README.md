# Jupyter Notebooks

* Install Jupyter Lab: `python3 -m pip install jupyterlab`
* Run (from the directory): `cd jupyter-notebooks; jupyter lab`
* Open and run the notebooks

# Scheduled tasks from notebooks

Build/push the dockerfile:

```
docker build -f jupyter-notebooks/Dockerfile jupyter-notebooks/ -t data4dappl-notebooks
```

Deploy the dockerfile, setting any required env vars and VOLUMES (check the Dockerfile)
