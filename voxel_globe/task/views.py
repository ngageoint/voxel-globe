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
  from subprocess import Popen, PIPE
  
  #This needs to be replace with a rabbitmq python library
  pid = Popen([os.environ['VIP_WRAP_SCRIPT'], 'rabbitmqctl', 'list_queues', 'name', 'durable', 'messages'], stdout=PIPE);
  data = pid.communicate()[0];
  pid.wait();
  
  data = map(lambda x: x.split('\t'), data.split('\n'))[1:-2];
  data = filter(lambda x:x[1]=='true' and int(x[2])>0, data);
  tasks = map(lambda x:int(x[0]), data)
  return render(request, 'task/html/task_list.html',
                {'tasks': tasks})