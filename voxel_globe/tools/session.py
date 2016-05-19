from uuid import uuid4

from django.http import HttpResponse

from vsi.tools.python import BasicDecorator
import voxel_globe.task.models as models

#TODO: add some form of checking to make sure you don't go back a page?

class StartSession(BasicDecorator):
  def __init__(self, cookie='voxel_globe_order_session', max_age=15*60):
    self.cookie_name = cookie
    self.max_age = max_age

  def __inner_call__(self, request, *args, **kwargs):
    uuid = uuid4()
    session = models.Session(uuid=uuid, owner=request.user)
    session.save()

    response = self.fun(request, *args, **kwargs)

    response.set_cookie(self.cookie_name, uuid, max_age=self.max_age)

    return response

class CheckSession(BasicDecorator):
  def __init__(self, cookie='voxel_globe_order_session',
               error_response=lambda self: HttpResponse('Session Expired')):
    self.cookie_name = cookie
    self.error_response = error_response.__get__(self, CheckSession)
    #bind error_response
  def __inner_call__(self, request, *args, **kwargs):
    try:
      models.Session.objects.get(uuid=request.COOKIES[self.cookie_name])
    except:
      response = self.error_response()
      response.delete_cookie(self.cookie_name)
      return response

    return self.fun(request, *args, **kwargs)

class EndSession(CheckSession):
  def __inner_call__(self, request, *args, **kwargs):
    try:
      models.Session.objects.get(uuid=request.COOKIES[self.cookie_name]).delete()
    except:
      response = self.error_response()
    else:
      response = self.fun(request, *args, **kwargs)

    response.delete_cookie(self.cookie_name)

    return response


# def start_session_old(fun):
#   def inner(request, *args, **kwargs):
#     uuid = uuid4()
#     session = models.Session(uuid=uuid, owner=request.user)
#     session.save()

#     response = fun(request, *args. **kwargs)

#     response.set_cookie('voxel_globe_order_session', uuid, max_age=max_age)

#     return response


# def start_session_old2(response, request,  max_age=15*60):
#   ''' Start an ordering session

#   Usage: return (start_session(response, request)

#   This is meant to ease the setup of a session'''

#   uuid = uuid4()
#   session = models.Session(uuid=uuid, owner=request.user)
#   session.save()

#   response.set_cookie('voxel_globe_order_session', uuid, max_age=max_age)

#   return response

# def just_check_session(request, delete=False, 
#                        cookie_name='voxel_globe_order_session'):
#   '''Check if session is valid

#      In a django view, function, simply call:
#        just_check_session(request)

#      and it returns a boolean if the session is still good'''

#   try:
#     uuid = request.COOKIES[cookie_name]
#     session = models.Session.objects.get(uuid=uuid)
#     if delete:
#       session.delete()
#   except:
#     return False
#   return True

# def check_session(response, request, 
#                   cookie_name='voxel_globe_order_session',
#                   error_response=lambda: HttpResponse('Session Expired')):
#   ''' Shortcut if for just_check_session

#   Useful if you don't care if the rest of the function is executed, and just
#   want to check at the end of the function. 

#   Usage:
#     return check_session(response, request) '''

#   if not just_check_session(request, cookie_name=cookie_name):
#     response = error_response()
#     #This is already an error. So delete the cookie if it exists
#     response.delete_cookie(cookie_name)
#     #This sets the cookie to '' which I think is means delete it on the client
#   return response

# def just_end_session(request, cookie_name='voxel_globe_order_session'):
#   return just_check_session(request, True, cookie_name)

# def clear_session(response, cookie_name='voxel_globe_order_session'):
#   ''' Removed the cookie from the response.

#   Response returned for convenience, even thought it is in-place modifies'''

#   response.delete_cookie(cookie_name)
#   return response

# def end_session(response, request,
#                 cookie_name='voxel_globe_order_session',
#                 error_response=lambda: HttpResponse('Session Expired')):
#   ''' Shortcut if for just_check_session+clear_session

#   Useful if you don't care if the rest of the function is executed, and just
#   want to check at the end of the function. 

#   Usage:
#     return end_session(response, request) 

#   Not as useful as check_session shortcut, because you often do not want to 
#   run the rest of the function if this session is expired.

#   It's probably better to:
#     #at the beginning
#     if not just_end_session(request):
#       blah
#     #and at the end
#     return clear_session(response) 
#   '''
#   if not just_end_session(request, cookie_name=cookie_name):
#     response = error_response()

#   clear_session(response)

#   return response  