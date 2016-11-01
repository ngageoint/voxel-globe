#!/usr/bin/env bash

_=''''
exec $(dirname $0)/../wrap python $0 "${@}"
' '''
#!/usr/bin/env python

from os import environ as env
import pickle

def django():
  import django
  django.setup()
  from django.contrib.auth.models import User as DjangoUser; 

  print '********** Creating Djanjo Users **********'

  with open(env['VIP_DJANGO_PASSWD'], 'rb') as fid:
    shadows = pickle.load(fid)
    #Loads a list of lists consisting of [username, hashed_password,
    #                                     is_superuser]

    for shadow in shadows:
      try: #Get user if already exists
        user = DjangoUser.objects.get(username=shadow[0])
      except: #else create new user
        user = DjangoUser.objects.create_user(shadow[0], env['VIP_EMAIL']);

      user.is_staff = shadow[2] #set super user permissions
      user.is_superuser = shadow[2] #set super user permissions
      user.password = shadow[1] #set password hash
      user.save()

if __name__=='__main__':
  django();