from django.contrib.auth.hashers import make_password
from os import environ as env
from getpass import getpass
import re
import pickle

class User(object):
  def __init__(self, name, password=None, isAdmin=False):
    self.name = name;
    self.password = password;
    self.isAdmin = isAdmin;
  def inputPassword(self):
    password=None;
    while not password:
      password=get_pass()
    self.password = password;
  def inputAdmin(self):
    q = ''
    while q not in 'yn':
      q = raw_input('Is Admin? (y/n) ');
    if q == 'y':
      self.isAdmin = True;
    else:
      self.isAdmin = False; 
      
def get_pass():
  pw1=getpass("Please enter the password you would like to use for Django:")
  pw2=getpass("Please verify:")
  
  if pw1==pw2:
    return make_password(pw1);
  print 'Passwords do not much, please try again\n'
  return None
  
if __name__=='__main__':
  user = User(env['VIP_DJANGO_ADMIN_USER'], isAdmin=True)
  print 'Admin user %s:' % user.name
  user.inputPassword();
  
  shadow = [[user.name, user.password, user.isAdmin]]
  
  user = 1;
  while user:
    print
    user = raw_input('Enter additional username (blank when done): ')
    
    if user and re.match(r'^[a-zA-Z0-9_]*$', user): #Valid a-z, A-Z, 0-9, and _
      user = User(user);
      user.inputPassword()
      user.inputAdmin()
    
      shadow.append([user.name, user.password, user.isAdmin])

  with open(env['VIP_DJANGO_PASSWD'], 'wb') as fid:
    pickle.dump(shadow, fid)
  
  print '\nIs is done, best not forget the passwords now...';