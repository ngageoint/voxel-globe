from channels import Group
from channels.sessions import enforce_ordering
from channels.auth import channel_session_user, channel_session_user_from_http
from voxel_globe.vip.exceptions import AccessViolation

@enforce_ordering(slight=True)
@channel_session_user_from_http
def ws_connect(message, websocket_key):
  #The channel_session_user_from_http checks is authenticated already
  print 'c', message.user

  if not message.user:
    raise AccessViolation("Connection is not authenticated!")
    return

  Group("ws_logger_%d" % message.user.id).add(message.reply_channel)

@enforce_ordering(slight=True)
@channel_session_user
def ws_message(message, websocket_key):

  ''' Now that session has been removed from the url path, there is no way to
      know if the user is still logged in when sending a message. This means a
      user can log out, and then send a message. And without that, there is no
      way to know the session has ended. IF this is needed, here's how to.

      1. Create a web socket token easiest idea is sha256 of the real token.
         I've already done this actually, it's websocket_key
      2. Store these keys in a database with the session_key so they can be
         looked up later. I did not do this, nor will I until this is needed
      3. Verify the websocket key is still good by checking that the matching
         session_key is still valid. I would never do this by sha-ing ALL the
         session keys. That is NOT the idea behind the sha, that's just me
         being lazy.
      4. Check this for EVERY message, or every x seconds. Both are a pain on
         a per message basis. But that's how I'd do it.'''

  print 'm', message['text']

  #Is this even necessary?
  if not message.user:
    raise AccessViolation("Message is not authenticated!")
    return

  Group("ws_logger_%d" % message.user.id).send({"text": message['text']})

@enforce_ordering(slight=True)
@channel_session_user
def ws_disconnect(message, websocket_key):
  print 'dc'

  #Is this even possible?
  if not message.user:
    raise AccessViolation("Disconnect is not authenticated?")
    return

  Group("ws_logger_%d" % message.user.id).discard(message.reply_channel)