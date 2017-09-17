# odata.org.il Kubernetes (K8S) deployment

Used to deploy https://www.odata.org.il/

## Setting up a new cluster

* Install the gcloud cli and get permissions on the project (the production environment google project id is `hasadna-odata`)
* Create the cluster
  * name = `data4dappl`
  * 1 node, v1.6.9, cos, n1-standard-1 (1 vCPU, 3.75 GB memory), us-central1-a
* edit `nginx.yaml`, `letsencrypt.yaml`, `jobs/ckan-restore-data.yaml`, `jobs/ckan-restore-db.yaml`
  * all these deployments rely on hostPath - so they must be on the same node
* Create the shared hostPath on this node
  * `gcloud compute ssh --project=hasadna-odata --zone us-central1-a gke-data4dappl-default-pool-29af7936-hdzs -- sudo mkdir -p /var/data4dappl-host`
* Create the secrets
  * Copy k8s/secrets.example.sh to k8s/secrets.sh
  * Edit `k8s/secrets.sh` - set the secrets
  * Copy k8s/etc-ckan-default-example to k8s/etc-ckan-default
  * Edit both ini files and replace the parts marked with MODIFY
  * Run `bin/k8s_recreate_secrets.sh` to update the secrets on the K8S cluster
* Create the configmaps
  * `bin/k8s_recreate_configmaps.sh`
* Deploy
  * `bin/k8s_deploy.sh`
* Create the ckan and initialize ckan DB (you can skip initialize if you are going to restore from dump)
  * `bin/k8s_apply_job.sh ckan-create-db`
  * `bin/k8s_apply_job.sh ckan-initialize-db`

## Restoring data and DB from other ckan instance
* create db dump on old server
  * `paster --plugin=ckan db dump ./ckan-db-dump-yyyy-mm-dd -c ./development.ini`
  * `gzip ./ckan-db-dump-yyyy-mm-dd`
* copy the db dump to local pc
  * `scp odata.org.il:/home/odata/ckan-db-dump-yyyy-mm-dd.gz ./ckan-dump/db.gz`
* create data dump on old server
  * `tar -zcvf ckan-data-yyyy-mm-dd.tar.gz ./ckan/data/`
* copy data dump to local pc
  * `scp 'odata.org.il:/home/odata/ckan-data-yyyy-mm-dd.tar.gz' ./ckan-dump/data.tar.gz`
* copy the data to the cluster node which the jobs are matched for
  * export NODE="main-cluster-node-name"
  * `gcloud compute ssh --project=hasadna-odata --zone us-central1-a "${NODE}"`
    * `sudo mkdir -p /var/ckan-dump/ && sudo chown $USER:$USER /var/ckan-dump`
  * `gcloud compute scp --project=hasadna-odata --zone us-central1-a ./ckan-dump/db.gz "${NODE}":/var/ckan-dump/db.gz`
  * `gcloud compute scp --project=hasadna-odata --zone us-central1-a ./ckan-dump/data.tar.gz "${NODE}":/var/ckan-dump/data.tar.gz`
* Ensure the db and data dumps are in /var/ckan-dump directory on the cluster instance:
  * `gcloud compute ssh --project=hasadna-odata --zone "${NODE}" -- ls -lah /var/ckan-dump/`
  * Should get something like:
    * `-rw-r--r--  1 ori  ori  685M Sep 15 19:53 data.tar.gz`
    * `-rw-r--r--  1 ori  ori   11M Sep 15 19:17 db.gz`
* Stop the ckan instance and pod (to prevent conflicts while loading the data)
* Run the ckan restore jobs - wait for each one to finish before starting next one, you can check status in K8S dashboard
  * `bin/k8s_apply_job.sh ckan-restore-data`
  * `bin/k8s_apply_job.sh ckan-restore-db`
* Start the ckan instance
  * `bin/k8s_apply.sh ckan`

## Using let's encrypt to issue and renew ssl certificates
* Issue certificate
  * ```kubectl exec -it `bin/k8s_get_pod_names.sh default letsencrypt` /issue_cert.sh ckan.odata.org.il```
* You can then enable the relevant nginx config under nginx-conf-d (don't forget to recreate the configmaps)
* remember to change the ckan.site_url as well - to https://
* the letsencrypt pod checks and renews certificates daily
* Let's encrypt and nginx use shared hostPath to share certificates and auth challenges
  * the relevant deployments have a selector to a specific node
  * there is a persistent volume that persists this data
  * backup script runs after cert issue or renew

## Adding cluster nodes / Restarting cluster on a new node
* You can add nodes freely in the google container engine web UI
* Kubernetes will distribute the load automatically
* If solr moves to a new node - you need to reindex the datasets
  * ```kubectl exec `bin/k8s_get_pod_names.sh default ckan` -- bash -c "source ../../bin/activate; paster --plugin=ckan search-index rebuild --config=/etc/ckan/default/development.ini"```
* Let's encrypt and nginx use a shared host path which require this procedure:
  * `bin/k8s_connect.sh`
  * ```export OLD_LETSENCRYPT_POD=`bin/k8s_get_pod_names.sh default letsencrypt````
  * get the node names using `kubectl get nodes`
  * `export NEW_NODE="new-node-name"`
  * `export OLD_NODE="old-node-name"`
  * set let's encrypt and nginx deployments selector to the new node name
  * Create the hostPath on the new node
    * gcloud compute ssh --project=hasadna-odata $NEW_NODE --zone us-central1-a -- sudo mkdir -p /var/data4dappl-host
  * run the backup script and ensure it persisted all certificates:
    * `kubectl exec -it $OLD_LETSENCRYPT_POD -- bash -c /backup.sh`
    * `kubectl exec -it $OLD_LETSENCRYPT_POD -- bash -c "ls -lah /persistent-host/letsencrypt-etc/live/*"`
  * delete the old let's encrypt deployment + pod
    * `kubectl delete deployment letsencrypt`
    * `kubectl delete pod $OLD_LETSENCRYPT_POD`
  * apply the new let's encrypt deployment
    * `bin/k8s_apply.sh letsencrypt`
  * ```export NEW_LETSENCRYPT_POD=`bin/k8s_get_pod_names.sh default letsencrypt````
  * check that the restore succeeded
    * ```kubectl exec -it $NEW_LETSENCRYPT_POD -- bash -c "ls -lah /etc/letsencrypt/live/*"```
  * apply the new nginx deployment
  * ensure nginx is running on the new node
    * ```kubectl describe pod `bin/k8s_get_pod_names.sh default nginx` | grep Node:```
  * check the site: https://ckan.odata.org.il/
* once new node is running, you can drain the old node
  * `kubectl drain --force --ignore-daemonsets $OLD_NODE`
* after you drain it, you can re-use it, or reduce node count in google container engine
