import os


from celery.utils.log import get_task_logger
import numpy as np


from voxel_globe.common_tasks import shared_task, VipTask
from voxel_globe.ingest.metadata.tools import load_voxel_globe_metadata

logger = get_task_logger(__name__)

### These need to be CLASSES actually, and call common parts via methods! :(

#New idea, add "get_focal_length(filename)" to BaseMetadata. It will use the json_config
#to either look for a fixed focal length, or a per image filename  focal length
#from the json config file, just like how matching works. 
#Then add "get_focal_length(filename)" it to a specific metadata parser, this do it's best
#and then call super... Remember, the json_config should always overwrite EVERYTHING else
#do same for date, time_of_day, etc... 

class BaseControlPoints(object):
  def __init__(self, task, upload_session_id, ingest_dir):
    from voxel_globe.ingest.models import UploadSession

    self.task = task
    self.upload_session = UploadSession.objects.get(id=upload_session_id)
    self.ingest_dir = ingest_dir
  
  @classmethod
  def task(cls, fn):
    #fn isn't ACTUALLY used
    def run(self, upload_session_id, ingest_dir):
      obj = cls(self, upload_session_id, ingest_dir)
      return obj.run()
    wrapper1 = shared_task(base=VipTask, bind=True, 
                           name='.'.join((__name__, fn.__name__)))
    wrapper2 = wrapper1(run)
    wrapper2.dbname = cls.dbname
    wrapper2.description = cls.description
    wrapper2.controlpoint_ingest=True
    return wrapper2

  def parse_json(self):
    self.json_config = load_voxel_globe_metadata(self.ingest_dir)
    #Place holder

class Csv(BaseControlPoints):
  dbname = 'csv'
  description = 'Comma separated value file'
  meta_name='CSV'

  def run(self):
    import csv
    from django.contrib.gis.geos import Point
    from vsi.iglob import glob
    from voxel_globe.meta.models import ControlPoint

    csv_files = glob(os.path.join(self.ingest_dir, '*.csv'), False)
    for csv_file in csv_files:
      with open(csv_file, 'r') as fid:
        reader = csv.reader(fid, delimiter=',')
        for line in reader:
          try:
            point = Point(float(line[2]),float(line[3]), float(line[4]),
                          srid=int(line[1]))
            ControlPoint(name=line[0], description="Ingested point", 
                         point=point, apparentPoint=point, 
                         service_id=self.task.request.id).save()
          except:
            pass

@Csv.task
def csv():
  pass
