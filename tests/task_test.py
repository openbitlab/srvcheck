import unittest
from .mocks import MockNotification, MockChain
from srvcheck.tasks import TaskChainLowPeer, TaskChainStuck, minutes, hours
from srvcheck.notification.notification import Notification

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

class TestTimingUtilities(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(minutes(13), 13*60)

    def test_hours(self):
        self.assertEqual(hours(13), 13*60*60)

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
        self.assertEqual(n.events[0], 'Chain has only 0 peers' + ' ' + n.PEERS_EMOJI)



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
        self.assertEqual(n.events[0], 'Chain is stuck at block 0x1234567890' + ' ' + n.STUCK_EMOJI)

