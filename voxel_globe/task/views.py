from django.shortcuts import render, HttpResponse
from voxel_globe.meta.models import ServiceInstance
import json

def mark_as_read(request):
  from voxel_globe.websockets.models import LogMessage
  log_ids = json.loads(request.POST['log_ids'])
  for log_id in log_ids:
    log_message = LogMessage.objects.get(id=int(log_id))
    log_message.read = True
    log_message.save()
  return HttpResponse('')

def revoke(request):
  from celery.task.control import revoke
  from voxel_globe.websockets import ws_logger
  import voxel_globe.meta.models

  task_id = request.POST['task_id']
  revoke(task_id, terminate=True)
  
  service_instance = voxel_globe.meta.models.ServiceInstance.objects.get(
        id=int(task_id))
  service_instance.status = 'Revoked'
  service_instance.save()
  
  ws_logger.send_status_update(task_id, service_instance.service_name, \
    "Revoked", None)
  return HttpResponse('')
  
def status(request):
  json_data = request.POST.get('json_data')
  task = json.loads(json_data)

  if task["state"] == "Failure":
    task["traceback_html"] = traceback_to_html(task["result"]["traceback"])

  # TODO user? entry time? finish time? from get_service_instance

  try_template_name = template_name(task["path"])
  fallback_template_name = 'task/html/default_status.html'

  # render w/ correct template, falling back to default if none available
  return render(request, [try_template_name, fallback_template_name],
                {'task': task})

def traceback_to_html(txt):
  html = str(txt).replace(' '*2, '&nbsp;'*4)
  html = html.decode('string_escape')
  html = html.split('\n')

  if html[0].startswith('"'):
    html[0] = html[0][1:]
  if html[len(html) - 1] == '"':
    html = html[:len(html) - 1]

  html = map(lambda x: '<div style="text-indent: -4em; padding-left: 4em">' + \
                       x + '</div>', html)
  html = '\n'.join(html)
  return html

def pretty_name(path):
  if path is None:
    return "None"
  import re
  import string
  pretty_name = re.search('.([A-Za-z_]+)$', path).group(0)
  pretty_name = string.replace(pretty_name, '.', '')
  pretty_name = string.replace(pretty_name, '_', ' ').title()
  return pretty_name

def template_name(path):
  if path is None:
    return "None"
  import string
  short_name = string.replace(path, '.', '_')
  short_name = string.replace(short_name, 'voxel_globe_', '')
  template_name = 'task/html/%s.html' % (short_name)
  return template_name
