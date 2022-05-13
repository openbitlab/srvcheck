import unittest

from ..srvcheck.tasks.tasknewrelease import TaskNewRelease
from .mocks import MockNotification, MockChain, MockSystem
from ..srvcheck.tasks import TaskChainLowPeer, TaskChainStuck, TaskSystemCpuAlert, TaskSystemDiskAlert, minutes, hours
from ..srvcheck.notification.notification import Emoji, Notification

CONF = {
    'name': 'Test',
    'chain': {
        'endpoint': 'http://localhost:8080',
    }
}

def buildTaskEnv(tt):
    c = MockChain(CONF)
    n = MockNotification({})
    s = MockSystem(CONF)
    t = tt(CONF, n, s, c)
    return (c, n, t, s)

class TestTimingUtilities(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(minutes(13), 13*60)

    def test_hours(self):
        self.assertEqual(hours(13), 13*60*60)


class TestTaskSystemCpuAlert(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskSystemCpuAlert)
        s.usage.cpuUsage = 10
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskSystemCpuAlert)
        s.usage.cpuUsage = 99
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'CPU usage is above 90% (99%) ⚠')


class TestTaskSystemDiskAlert(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskSystemDiskAlert)
        s.usage.diskPercentageUsed = 10
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskSystemDiskAlert)
        s.usage.diskPercentageUsed = 99
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'Disk usage is above 90% (99%) (/var/log: 0.0G) 💾')


class TestTaskChainLowPeer(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskChainLowPeer)
        c.peers = 12
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskChainLowPeer)
        c.peers = 0
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'Chain has only 0 peers' + ' ' + Emoji.Peers)



class TestTaskChainStuck(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskChainStuck)
        c.hash = '0x1234567890'
        t.run()
        c.hash = '0x1234567891'
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskChainStuck)
        c.hash = '0x1234567890'
        t.run()
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'Chain is stuck at block 0x1234567890' + ' ' + Emoji.Stuck)

class TestTaskNewRelease(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskNewRelease)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskNewRelease)
        c.latestVersion = 'v0.0.1'
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'has new release: %s %s' % (c.latestVersion, Emoji.Rel))

