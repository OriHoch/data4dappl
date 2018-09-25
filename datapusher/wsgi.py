import os
import sys
import hashlib
import ckanserviceprovider.web as web
os.environ['JOB_CONFIG'] = '/usr/lib/ckan/datapusher/src/datapusher/deployment/datapusher_settings.py'
web.init()
import datapusher.jobs as jobs
application = web.app
