import unittest

from srvcheck.chains.substrate import TaskSubstrateNewReferenda

from .task_test import buildTaskEnv

# class TestTaskSubstrateNewReferenda(unittest.TestCase):
#     def test(self):
#         c, n, t = buildTaskEnv(TaskSubstrateNewReferenda)
#         c.network = 'Kusama'
#         self.assertFalse(t.run())
#         self.assertGreater(t.prev, 0)
