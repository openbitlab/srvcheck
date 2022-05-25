import unittest
from srvcheck.utils import Bash, System, confGetOrDefault

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

class TestUtilGetConfOrDefault(unittest.TestCase):
    CONF = {
        'id': 1,
        'name': 'Test',
        'chain': {
            'endpoint': 'http://localhost:8080',
            'type': '',
        }
    }

    def test_getFromConfExistingString(self):
        self.assertEqual(confGetOrDefault(self.CONF, 'chain.endpoint'), 'http://localhost:8080')

    def test_getFromConfExistingInteger(self):
        self.assertEqual(confGetOrDefault(self.CONF, 'id', cast=int), 1)

    def test_getFromConfNotExistingString(self):
        self.assertEqual(confGetOrDefault(self.CONF, 'chain.id'), None)

    def test_getFromConfNotExistingDefault(self):
        self.assertNotEqual(confGetOrDefault(self.CONF, 'chain.id', 3, int), None)
        self.assertEqual(confGetOrDefault(self.CONF, 'type', 'tendermint'), 'tendermint')

    def test_getFromConfExistingButEmptyDefault(self):
        self.assertNotEqual(confGetOrDefault(self.CONF, 'chain.type', 'mockchain'), '')
        self.assertEqual(confGetOrDefault(self.CONF, 'chain.type', 'mockchain'), 'mockchain')