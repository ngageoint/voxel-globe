import hashlib

def websocket_token_from_session_key(session_key):
  if session_key:
    m = hashlib.sha256()
    m.update(session_key)
    return m.hexdigest()
  else:
    return None