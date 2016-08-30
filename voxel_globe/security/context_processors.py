from .tools import websocket_token_from_session_key

def websocket_token(request):
  token = websocket_token_from_session_key(request.session.session_key)
  if token:
    return {'websocket_token': token}
  else:
    return {'websocket_token': ''}