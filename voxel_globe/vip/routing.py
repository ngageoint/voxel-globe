from channels.routing import route, include

channel_routing = [
  #UNLIKE urls.py, path starts with /
  include('voxel_globe.websockets.routing.channel_routing', path=r'^/ws')
]