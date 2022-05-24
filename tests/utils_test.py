import unittest
from srvcheck.utils import Bash, System, ConfSet

class TestUtilsBash(unittest.TestCase):
    def test_echo(self):
        self.assertEqual(Bash('echo "Hello World!"').value(), 'Hello World!')


class TestUtilsSystem(unittest.TestCase):
    def test_getIP(self):
        pass 
        # Can't test on CI
        # self.assertEqual(System().getIP().count('.'), 3)

    def test_getUsage(self):
        us = System({}).getUsage()
        self.assertNotEqual(us.uptime, '')
        self.assertNotEqual(us.diskSize, 0)
        self.assertNotEqual(us.diskUsed, 0)
        self.assertNotEqual(us.diskUsedByLog, 0)
        self.assertNotEqual(us.diskPercentageUsed, 0)
        self.assertNotEqual(us.ramSize, 0)
        self.assertNotEqual(us.ramUsed, 0)
        self.assertNotEqual(us.ramFree, 0)
        self.assertNotEqual(us.cpuUsage, 0)

class TestUtilConfSet(unittest.TestCase):
    CONF = {
        'id': 1,
        'name': 'Test',
        'chain': {
            'endpoint': 'http://localhost:8080',
            'type': '',
        }
    }
    CONFS = ConfSet(CONF)

    def test_getFromConfExistingString(self):
        self.assertEqual(self.CONFS.getOrDefault('chain.endpoint'), 'http://localhost:8080')

    def test_getFromConfExistingInteger(self):
        self.assertEqual(self.CONFS.getOrDefault('id', type=int), 1)

    def test_getFromConfNotExistingString(self):
        self.assertEqual(self.CONFS.getOrDefault('chain.id'), None)

    def test_getFromConfNotExistingDefault(self):
        self.assertNotEqual(self.CONFS.getOrDefault('chain.id', 3, type=int), None)
        self.assertEqual(self.CONFS.getOrDefault('type', 'tendermint'), 'tendermint')

    def test_getFromConfExistingButEmptyDefault(self):
        self.assertNotEqual(self.CONFS.getOrDefault('chain.type', 'mockchain'), '')
        self.assertEqual(self.CONFS.getOrDefault('chain.type', 'mockchain'), 'mockchain')