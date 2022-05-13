import unittest
from .task_test import buildTaskEnv
from srvcheck.chains.substrate import TaskSubstrateNewReferenda


# class TestTaskSubstrateNewReferenda(unittest.TestCase):
#     def test(self):
#         c, n, t = buildTaskEnv(TaskSubstrateNewReferenda)
#         c.network = 'Kusama'
#         self.assertFalse(t.run())
#         self.assertGreater(t.prev, 0)
