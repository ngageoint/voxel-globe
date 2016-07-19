from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def eventTriggerCreator(request):
    return render(request, 'view_event_trigger/html/eventTriggerCreator.html')

