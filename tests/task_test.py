import unittest
from .mocks import MockNotification, MockChain
from srvcheck.tasks import TaskChainLowPeer, TaskChainStuck

CONF = {
    'name': 'Test',
    'chain': {
        'endpoint': 'http://localhost:8080',
    }
}

def buildTaskEnv(tt):
    c = MockChain(CONF)
    n = MockNotification({})
    t = tt(CONF, n, None, c)
    return (c, n, t)



class TestTaskChainLowPeer(unittest.TestCase):
    def test_noalert(self):
        c, n, t = buildTaskEnv(TaskChainLowPeer)
        c.peers = 12
        t.run()
        n.flush()
        self.assertEqual(n.events, [])

    def test_alert(self):
        c, n, t = buildTaskEnv(TaskChainLowPeer)
        c.peers = 0
        t.run()
        n.flush()
        self.assertEqual(n.events[0], 'Chain has only 0 peers')



class TestTaskChainStuck(unittest.TestCase):
    def test_noalert(self):
        c, n, t = buildTaskEnv(TaskChainStuck)
        c.hash = '0x1234567890'
        t.run()
        c.hash = '0x1234567891'
        t.run()
        n.flush()
        self.assertEqual(n.events, [])

    def test_alert(self):
        c, n, t = buildTaskEnv(TaskChainStuck)
        c.hash = '0x1234567890'
        t.run()
        t.run()
        n.flush()
        self.assertEqual(n.events[0], 'Chain is stuck at block 0x1234567890')

