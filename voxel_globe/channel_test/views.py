from django.shortcuts import render, redirect
import os

def channel_test(request):
  if request.method == 'POST':
    from voxel_globe.channel_test import tasks
    task = request.POST['task']

    if task == 'success':
      task = tasks.success_task.apply_async(user=request.user)
    elif task == 'fail':
      task = tasks.fail_task.apply_async(user=request.user)
    elif task == 'long':
      task = tasks.long_task.apply_async(user=request.user)

    auto_open = True

    # return render(request, 'ingest/html/ingest_started.html', 
    #           {'task_id':task.task_id})
  else:
    auto_open = False

  return render(request, 'channel_test/html/channel_test.html',
                {'title': 'Voxel Globe - Channels',
                 'page_title': 'Channels, Proof of Concept',
                 'task_menu_auto_open': auto_open})