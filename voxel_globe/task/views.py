from django.shortcuts import render, HttpResponse
import os

# Create your views here.
def status(request, task_id):
  from celery.result import AsyncResult
  
  task = AsyncResult(task_id);
  
  task.traceback_html = tracebackToHtml(task.traceback)
   
  return render(request, 'task/html/task_status.html',
                {'task': task})

def tracebackToHtml(txt):
  html = str(txt).replace(' '*2, '&nbsp;'*4)
  html = html.split('\n')
  html = map(lambda x: '<div style="text-indent: -4em; padding-left: 4em">'+x+'</div>', html)
  html = '\n'.join(html)
  return html  

def listQueues(request):
  def safe_int(i):
    try:
      return int(i)
    except ValueError:
      return None
  import pyrabbit

  #These values need to be unhardcoded...
  client = pyrabbit.api.Client('localhost:15672', 'guest', 'guest')
  names = [x['name'] for x in client.get_queues()]
  tasks = [x for x in map(safe_int, names) if x is not None]
  return render(request, 'task/html/task_list.html',
                {'tasks': tasks})