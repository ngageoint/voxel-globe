from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from celery import current_app
import os
class VoxelGlobeTestCase(TestCase):

  def setupVoxelGlobeTestCase(self):
    os.environ['VIP_IMAGE_DIR'] = '/tmp/image'
    os.environ['VIP_STORAGE_DIR'] = '/tmp/storage'
    if not os.path.exists(os.environ['VIP_IMAGE_DIR']):
      os.makedirs(os.environ['VIP_IMAGE_DIR'])
    if not os.path.exists(os.environ['VIP_STORAGE_DIR']):
      os.makedirs(os.environ['VIP_STORAGE_DIR'])
    # set celery always eager so tasks execute synchronously
    current_app.conf.CELERY_ALWAYS_EAGER = True

    # create a new test client and log in
    user = User.objects.create_user('test', 'test@t.est', 'testy')
    user.save()
    client = Client()
    assert client.login(username='test', password='testy')

    # return the test client so the rest of the test class can use it
    return client

  def tearDownVoxelGlobeTestCase(self):
    current_app.conf.CELERY_ALWAYS_EAGER = False