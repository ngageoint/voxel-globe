from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from celery import current_app

class VoxelGlobeTestCase(TestCase):

  def setupVoxelGlobeTestCase(self):
    # set celery always eager so tasks execute synchronously
    current_app.conf.CELERY_ALWAYS_EAGER = True

    # create a new test client and log in
    user = User.objects.create_user('test', 'test@t.est', 'testy')
    user.save()
    client = Client()
    client.login(username='test', password='testy')

    # return the test client so the rest of the test class can use it
    return client

  def tearDownVoxelGlobeTestCase(self):
    current_app.conf.CELERY_ALWAYS_EAGER = False