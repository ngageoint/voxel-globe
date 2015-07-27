import os
os.environ.data.pop('', None);
#see wsgi.py why

from Cookie import SimpleCookie
import datetime
import pytz

from django.contrib.auth import SESSION_KEY
from django.conf import settings

#from django.contrib.auth.models import User
from django import db
from django.contrib.sessions.models import Session
from django import setup;
setup();

def allow_access(environ, host):
  #print '\n'.join(map(lambda x: '%s:  %s' % x, zip(environ.keys(), environ.values())))
  #print environ['REQUEST_URI'], environ['SCRIPT_NAME']
  try:
    cookie = SimpleCookie(environ['HTTP_COOKIE'])
  except KeyError:
    #No cookie == no permission
    return False;
  
  #Special overide for INTERAL services, NOT FOR WEB SERVICES!!!
  #There should be no way they have the secret key!
  try:
    secret = cookie['secretkey'].value
    #print 'is "%s" == "%s"?' % (secret, settings.SECRET_KEY) 
    if secret == settings.SECRET_KEY:
      return True;
  except KeyError:
    pass;
  
  try:
    sessionId = cookie[settings.SESSION_COOKIE_NAME].value;
  except KeyError:
    #No session id -> not logged in -> immediate access denied
    return False
  now = datetime.datetime.now(tz=pytz.utc);

  if now > allow_access.nextCheck:
    #if checkFrequency has passed, clear the list
    allow_access.validSessions = {}
    #print 'Cleared cache'
    allow_access.nextCheck = now + allow_access.checkFrequency;
  
  try: 
    #print 'Check in cache'
    #Check if in list
    expireTime = allow_access.validSessions[sessionId]
    #Get index
    #print 'In cache'
  except KeyError: #Session not in dictionary
    #print 'Not in cache', allow_access.validSessions
    try:
      #print 'check in session db', sessionId
      db.reset_queries()
      session = Session.objects.get(pk=sessionId)
      if not SESSION_KEY in session.get_decoded():
        #If session KEY is not in the data stream there this is not a logged in SESSION
        return False
    except Session.DoesNotExist:
      #Not in session DB
      #print 'Not in session db'
      return False;
    finally:
      db.connection.close()
  
    #if it's in the database
    allow_access.validSessions[sessionId] = session.expire_date;
    #Add to cache
    expireTime = session.expire_date;
    #print 'in session db'


  if expireTime > now:
    #Valid session by expire time
    #print 'Valid time'
    return True
  else:
    #print 'Invalid time'
    return False
  
allow_access.validSessions = {}
allow_access.nextCheck = datetime.datetime.now(tz=pytz.utc);
allow_access.checkFrequency = datetime.timedelta(seconds=10); 