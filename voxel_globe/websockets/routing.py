from channels.routing import route
from voxel_globe.websockets.consumers import ws_connect, ws_message, ws_disconnect

channel_routing = [
  route("websocket.receive", ws_message),
  route("websocket.connect", ws_connect),
  route("websocket.disconnect", ws_disconnect),
]