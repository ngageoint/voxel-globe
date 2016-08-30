from channels import Group
from voxel_globe.vip.exceptions import AccessViolation

from channels.generic.websockets import WebsocketConsumer

class LoggerConsumer(WebsocketConsumer):
  http_user=True #turns on channel_session_user_from_htt
  #slight_ordering=True
  #disabled for now, until it's an issue and I need this

  def connection_groups(self, websocket_key):
    if not self.message.user or not self.message.user.id: #No anonymous!
      raise AccessViolation("Connection is not authenticated!")

    return ['ws_logger_%d' % self.message.user.id]

  # def connect(self, message, websocket_key):
  #   self.session_id = message.http_session.session_key
  #   #As I suspected, this doesn't work. receive is called in a different 
  #   #instance, an instance "per message", as the docs say

  def receive(self, websocket_key, text=None, bytes=None):
    ''' Now that session has been removed from the url path, there is no way to
        know if the user is still logged in when sending a message. This means 
        a user can log out, and then send a message. And without that, there is
        no way to know the session has ended. IF this is needed, here's how to.

        1. Create a web socket token easiest idea is sha256 of the real token.
           I've already done this actually, it's websocket_key
        2. Store these keys in a database with the session_key so they can be
           looked up later. I did not do this, nor will I until this is needed
        3. Verify the websocket key is still good by checking that the matching
           session_key is still valid. I would never do this by sha-ing ALL the
           session keys. That is NOT the idea behind the sha, that's just me
           being lazy. http://stackoverflow.com/q/5030984/4166604
        4. Check this for EVERY message, or every x seconds. Both are a pain on
           a per message basis. But that's how I'd do it.'''

    #basic echo back example
    self.send(text="Re: "+text)

  def disconnect(self, message, websocket_key, **kwargs):
    super(LoggerConsumer, self).disconnect(message, **kwargs)

