import unittest
from .task_test import buildTaskEnv
from srvcheck.chains.tendermint import TaskTendermintHealthError


class TestTaskTendermintHealthError(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskTendermintHealthError)
        c.healthOk = True
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskTendermintHealthError)
        c.healthOk = False
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'Health error! 🚨')
