from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@shared_task(base=VipTask, bind=True)
def vxl(self):
  import boxm2_adaptor as ba
  from StringIO import StringIO
  from vsi.tools.redirect import Redirect
  import sys
  stdout = StringIO()
  py_stdout=StringIO()
  sys.stdout.flush()

  #Using Redirect is not considered a failed experiment... However this is just
  #a test
  with Redirect(stdout_c=stdout, stdout_py=py_stdout):
    ba.ocl_info()
  py_stdout.seek(0)
  print py_stdout.read()
  stdout.seek(0)
  return stdout.read()
