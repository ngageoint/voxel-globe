from voxel_globe.common_tasks import shared_task, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@shared_task(base=VipTask, bind=True)
def success(self):
  import time
  time.sleep(0.5)
  return 123

@shared_task(base=VipTask, bind=True)
def vxl(self):
  import boxm2_adaptor as ba
  from StringIO import StringIO
  from vsi.tools.redirect import Redirect
  stdout = StringIO()
  with Redirect(stdout_c=stdout):
    ba.ocl_info()
  stdout.seek(0)
  return stdout.read()

@shared_task(base=VipTask, bind=True)
def python_crash(self):
  import time
  x = 15
  time.sleep(0.5)
  x += 5
  ok()
  return -321

@shared_task(base=VipTask, bind=True)
def python_segfault(self):
  import time
  time.sleep(0.5)
  from types import CodeType as code
  #Guarneteed segfault https://wiki.python.org/moin/CrashingPython
  exec code(0, 5, 8, 0, "hello moshe", (), (), (), "", "", 0, "")
  return -111

@shared_task(base=VipTask, bind=True)
def run_ocl_info(self):
  import boxm2_adaptor as b
  b.ocl_info()

@shared_task(base=VipTask, bind=True)
def load_scene(self):
  import boxm2_scene_adaptor as b
  b.boxm2_scene_adaptor(r'D:\vip\tmp\tmptdnhd4\model\uscene.xml')