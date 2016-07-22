from django.shortcuts import render, redirect

def event_trigger(request):
  if request.method == 'POST':
    pass
  else:
    return render(request, 'event_trigger/html/event_trigger.html',
                  {'title': 'Voxel Globe - Event Trigger Results',
                   'page_title': 'Event Trigger Results'})

# Create your views here.
def eventTriggerCreator(request):
    return render(request, 'view_event_trigger/html/eventTriggerCreator.html')

