import unittest
import urllib.parse

from srvcheck.tasks.tasknewrelease import TaskNewRelease, versionCompare
from srvcheck.utils.confset import ConfSet
from srvcheck.tasks import TaskChainLowPeer, TaskChainStuck, TaskSystemCpuAlert, TaskSystemDiskAlert, minutes, hours
from srvcheck.notification.notification import Emoji
from .mocks import MockNotification, MockChain, MockSystem, MockChainNoBlockHash

CONFRAW = {
	'name': 'Test',
	'chain': {
		'endpoint': 'http://localhost:8080',
	}
}
CONF = ConfSet(CONFRAW)

def buildTaskEnv(tt, chainClass=MockChain):
	c = chainClass(CONF)
	n = MockNotification(CONF)
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
		self.assertEqual(n.events[0], urllib.parse.quote('#CPU usage is above 90% (99%) ⚠ '))


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
		self.assertEqual(n.events[0], urllib.parse.quote('#disk usage is above 90% (99%) (/var/log: 0.0G, /: 0.0G) 💾 '))


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
		self.assertEqual(n.events[0], urllib.parse.quote('#chain has only 0 peers' + ' ' + Emoji.Peers + ' '))



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
		self.assertEqual(n.events[0], urllib.parse.quote('#chain is stuck at block 0x1234567890 since 0 seconds (1)' + ' ' + Emoji.Stuck + ' '))


	def test_noblockhash(self):
		c, n, t, s = buildTaskEnv(TaskChainStuck, MockChainNoBlockHash)
		c.height = 0
		t.run()
		c.height = 1
		t.run()
		n.flush()
		self.assertEqual(len(n.events), 0)

	def test_noblockhash_alert(self):
		c, n, t, s = buildTaskEnv(TaskChainStuck, MockChainNoBlockHash)
		c.height = 1
		t.run()
		t.run()
		n.flush()
		self.assertEqual(len(n.events), 1)
		self.assertEqual(n.events[0], urllib.parse.quote('#chain is stuck at block 1 since 0 seconds (1)' + ' ' + Emoji.Stuck + ' '))


class TestTaskNewRelease(unittest.TestCase):
	def test_VersionCompare(self):
		self.assertEqual(versionCompare('v1.0.0', 'v1.0.0'), 0)
		self.assertEqual(versionCompare('v1.0.0', 'v1.0.1'), -1)
		self.assertEqual(versionCompare('v1.2.0', 'v1.0.1'), 1)
		self.assertEqual(versionCompare('v1.1.0-rc.2', 'v1.1.0-rc.3'), -1)
		self.assertEqual(versionCompare('v1.1.0', 'v1.1.0-rc.3'), 1)

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
		self.assertEqual(n.events[0], urllib.parse.quote(f'#has new release: {c.latestVersion} {Emoji.Rel} '))

