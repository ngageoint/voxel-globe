from django.http import HttpResponse
from channels.handler import AsgiHandler
from channels import Channel, Group
from channels.sessions import channel_session, enforce_ordering
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
import os

@enforce_ordering(slight=True)
@channel_session_user_from_http
def ws_connect(message):
  prefix, user, session = message.content['path'].strip('/').split('/')
  prefix = str(prefix)

  if (prefix != "ws_logger"):
    return

  user = str(user)
  session = str(session)
  message.channel_session['user'] = user
  message.channel_session['session_key'] = session

  if user != str(message.user.id):
    raise ValueError("That's not you! %s : %s" % (user, str(message.user.id)))
    return
  if session != str(message.http_session.session_key):
    raise ValueError("That's not your session! %s : %s" % (session, str(message.http_session.session_key)))
    return

  Group("ws_logger_%s" % user).add(message.reply_channel)

@enforce_ordering(slight=True)
@channel_session_user
def ws_message(message):
  try:
    user = message.channel_session['user']
    session = message.channel_session['session_key']
  except KeyError:
    return

  if user != str(message.user.id):
    raise ValueError("That's not you! %s : %s" % (user, str(message.user.id)))
    return

  Group("ws_logger_%s" % user).send({
    "text": message['text'],
  })

@enforce_ordering(slight=True)
@channel_session_user
def ws_disconnect(message):
  try:
    user = message.channel_session['user']
  except KeyError:
    Group("ws_logger").discard(message.reply_channel)
    return

  if user != str(message.user.id):
    raise ValueError("That's not you! %s : %s" % (user, str(message.user.id)))
    return

  Group("ws_logger_%s" % user).discard(message.reply_channel)