from __future__ import absolute_import

import os
from os import environ as env

from celery import Celery

from django.conf import settings

#Thanks ask https://groups.google.com/forum/#!msg/celery-users/QTCf6T4QnUE/z7nvZUuS-NUJ
import logging
from celery import signals
import requests.packages.urllib3.connectionpool as httplib
@signals.worker_process_init.connect
def configure_pool_process_loglevel(**kwargs):
  httplib.HTTPConnection.debuglevel = 1
  logging.getLogger().setLevel(getattr(logging, 
                                       env['VIP_CELERY_WORKER_LOG_LEVEL']))

#Disable that ANNOYING DEBUG/MainProcess pidbox received method enable_events() [reply_to:None ticket:None]
logging.getLogger("kombu.pidbox").setLevel(logging.WARNING)

# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', env['VIP_DJANGO_SETTINGS_MODULE'])
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "vip.settings")
#Really set by vip.bsh...

try:
  import brl_init
  brl_init.set_smart_register(True)
  #This need to me imported before other boxm2 because of how it's designed
  #This should take care of all boxm2 calls in Django and celery alike
except ImportError:
  if os.environ.get('VIP_VXL_SILENT_FAIL_IMPORT', "0") != "1":
    print "Cannot load brl_init... This should ONLY happen when building"
    print "voxel_globe for the first time, and probably only during initialize"
    print "database. YOU SHOULD NOT BE SEEING THIS FREQUENTLY!!!"

#app = Celery(env['VIP_CELERY_APP'], backend='rpc://', broker=env['VIP_CELERY_BROKER_URL'])
app = Celery(env['VIP_CELERY_APP'])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
#app.config_from_object('django.conf:settings', namespace='CELERY') 
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
