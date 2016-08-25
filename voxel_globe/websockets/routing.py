from channels.routing import route_class
from .consumers import LoggerConsumer

channel_routing = [
  route_class(LoggerConsumer, path=r'^/logger/(?P<websocket_key>[a-z0-9]+)/$'),
]