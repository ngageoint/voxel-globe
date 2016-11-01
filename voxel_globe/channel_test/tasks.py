from voxel_globe.common_tasks import shared_task, VipTask
from voxel_globe.websockets import ws_logger
import random, time

@shared_task(base=VipTask, bind=True)
def success_task(self):
  ws_logger.debug(self, "d " + str(random.random()))
  ws_logger.info(self, "i " + str(random.random()))
  ws_logger.warn(self, "w " + str(random.random()))
  ws_logger.message(self, "Important message about task %s!!" % self.request.id)
  self.update_state(state='Initializing', meta={"site_name": "Exciting text"})
  self.update_state(state='Processing', meta={"site_name": "Exciting text"})
  return {"site_name": "Exciting text"}

@shared_task(base=VipTask, bind=True)
def fail_task(self):
  ws_logger.error(self, "e " + str(random.random()))
  ws_logger.fatal(self, "f " + str(random.random()))
  raise ValueError("Because reasons")

@shared_task(base=VipTask, bind=True)
def long_task(self):
  self.update_state(state="PROCESSING", meta={"index":0, "total": 5})
  time.sleep(5)
  ws_logger.message(self, "Important message 1")
  self.update_state(state="PROCESSING", meta={"index":1, "total": 5})
  time.sleep(5)
  ws_logger.message(self, "Important message 2")
  self.update_state(state="PROCESSING", meta={"index":2, "total": 5})
  time.sleep(5)
  ws_logger.message(self, "Important message 3")
  self.update_state(state="PROCESSING", meta={"index":3, "total": 5})
  # self.update_state(state="PROCESSING", meta={"poetry":"let us go then you and i"})
  time.sleep(5)
  ws_logger.message(self, "Important message 4")
  self.update_state(state="PROCESSING", meta={"index":4, "total": 5})
  time.sleep(5)
  ws_logger.message(self, "Important message 5")
  self.update_state(state="PROCESSING", meta={"index":5, "total": 5})
