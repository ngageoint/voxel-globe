from channels.routing import route
from voxel_globe.websockets.consumers import ws_connect, ws_message, ws_disconnect

channel_routing = [
  route("websocket.connect", ws_connect, path=r'^/logger/(?P<websocket_key>[a-z0-9]+)/$'),
  route("websocket.receive", ws_message, path=r'^/logger/(?P<websocket_key>[a-z0-9]+)/$'),
  route("websocket.disconnect", ws_disconnect, path=r'^/logger/(?P<websocket_key>[a-z0-9]+)/$'),
]