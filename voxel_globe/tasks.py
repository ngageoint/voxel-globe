''' Master Celery Task file.
    
    Import all tasks you want the central celery daemon processing
    
    This CAN be used by other processes, but that it not the intent of this file
    Plus now with the registry, is less than friendly
'''

#import celery app
from .common_tasks import app, VipTask
#To make importing for other modules easier

from django.conf import settings

ingest_tasks = []
tasks = []

for task in settings.INGEST_TASKS:
  ingest_tasks.append(__import__(task, fromlist=[task.split('.')[-1]]))
  #Use fromlist so ingest_tasks[*].ingest_data is the ingest function

for task in settings.CELERY_TASKS:
  tasks.append(__import__(task))

#Replaced this with a task registry... controlled by the django settings file