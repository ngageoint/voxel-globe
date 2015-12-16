from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.contrib.gis.measure import Distance

from pprint import pformat;

from voxel_globe.world.models import WorldBorder

import voxel_globe.world.tasks as tasks

# Create your views here.

#def error400(request):
#  HttpResponse('Error 400, yo', status=400)
#AEN: THIS DOESN'T WORK

def index(request):
  return HttpResponse(('Request keys are\n'+'\n'.join(request.REQUEST.keys())+
                       '\n\nGet keys are\n'+'\n'.join(request.GET.keys())+
                       '\n\nPost keys are\n'+'\n'.join(request.POST.keys())+
                       '\n\nHi world.\nYou get NOTHING! Well except some '+'\n'.join(dir(request))+'\n\n'+pformat(repr(request))).replace('\\n', '\n').replace('\n', '<BR>'))

def search(request):
  return render(request, 'world/search.html', {});

def result(request):
  lat = request.POST['lat'];
  lon = request.POST['lon'];
  #Optional try/cat to check GET too? But WHY woudl I do THAT?! :-P
  
  return result2(request, lat, lon);

def result2(request, lat, lon='33.00'):

  if float(lat)<-180 or float(lat)>180:
    return HttpResponseBadRequest('Error 400');
    #return HttpResponse(status=400);
    #AEN: THIS DOESN'T WORK! Maybe it was, but was just sending an empty page. I WANT THE DEFAULT!
    #raise Http404; #This SHOULD be 400

  pt = 'POINT(%s %s)' % (lon, lat)
  country = WorldBorder.objects.filter(mpoly__contains=pt);

  countriesNearUS = filter(lambda x:x.closeToUS(), WorldBorder.objects.all())
  
  if not country:
    context = {'lat':lat, 'lon':lon,
               'countriesNearUnitedStates':countriesNearUS}
    return render(request, 'world/result.html', context);

  d=Distance(m=500);
  touching = WorldBorder.objects.filter(mpoly__touches=country[0].mpoly)
  neighbors = WorldBorder.objects.filter(mpoly__distance_lte=(country[0].mpoly, d))
  neighbors = filter(lambda x: x.id!=country[0].id, neighbors);

  t = tasks.getArea.delay(country[0].id);
  t.wait(); #This should be something far more complicated, like a long pull,Perhaps USING rabbitmq to check based on the task.id!
  area = str(t.result);

  context = {'country':country, 'lat':lat, 'lon':lon,
             'touching':touching, 'neighbors':neighbors, 
             'distance':d, 'area':area,
             'countriesNearUnitedStates':countriesNearUS}
  
  return render(request, 'world/result.html', context);
 
  '''if not country:
    s+= "{None}\n\n"
  else:
    s+= '%s' % (''.join(map(lambda x:x.name, country)));
    s+='\n\n';

    country = country[0]
    touching = WorldBorder.objects.filter(mpoly__touches=country.mpoly)
    s+= "Countries touching %s are:\n%s" % (country.name, '\n'.join(map(lambda x:x.name, touching)));
    s+='\n\n'

    neighbors = WorldBorder.objects.filter(mpoly__distance_lte=(country.mpoly, Distance(m=500)))
    s+= "The neighbors (within 500 meters of border) of %s are:\n" % (country.name) + '\n'.join(map(lambda x:x.name, neighbors));
    s+='\n\n';

  countriesNearUS = filter(lambda x:x.closeToUS(), WorldBorder.objects.all())
  s += "&lt;static query&gt; Countries near the United States\n"
  s += '\n'.join(map(lambda x:x.name, countriesNearUS))'''

#  return HttpResponse(s)

def area(request, id=1):
  if request.REQUEST.has_key('id'):
    id=int(request.REQUEST['id'])
  t = tasks.getAreaLong.delay(id);
  t.wait(); 
  area2 = t.result;
  return HttpResponse('%d is %d (whatever units)' % (id, area2))


