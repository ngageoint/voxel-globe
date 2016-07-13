from django.test import TestCase

class VoxelGlobeTestCase(TestCase):
  from voxel_globe.common_tasks import VipTask
  # a = VipTask.apply_async
  # VipTask.apply_async=VipTask.apply
  # VipTask.apply = a