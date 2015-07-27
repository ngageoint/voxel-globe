from voxel_globe.common_tasks import app, VipTask

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__);

@app.task(base=VipTask, bind=True)
def success(self):
  import time
  time.sleep(0.5)
  return 123

@app.task(base=VipTask, bind=True)
def python_crash(self):
  import time
  x = 15
  time.sleep(0.5)
  x += 5
  ok()
  return -321

@app.task(base=VipTask, bind=True)
def run_ocl_info(self):
  import boxm2_adaptor as b
  b.ocl_info()

@app.task(base=VipTask, bind=True)
def load_scene(self):
  import boxm2_scene_adaptor as b
  b.boxm2_scene_adaptor(r'D:\vip\tmp\tmptdnhd4\model\uscene.xml')