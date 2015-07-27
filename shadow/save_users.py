import django
import os
import django.contrib.auth.models as models
import pickle

def save_users():
  users = models.User.objects.all();
  shadow = []
  for user in users:
    shadow.append([user.username, user.password, user.is_superuser]);
  with open(os.environ['VIP_DJANGO_PASSWD'], 'wb') as fid:
    pickle.dump(shadow, fid)

if __name__ == '__main__':
  django.setup()
  save_users()