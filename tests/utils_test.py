import unittest
from srvcheck.utils import Bash, System

class TestUtilsBash(unittest.TestCase):
    def test_echo(self):
        self.assertEqual(Bash('echo "Hello World!"').value(), 'Hello World!')


class TestUtilsSystem(unittest.TestCase):
    def test_getIP(self):
        pass 
        # Can't test on CI
        # self.assertEqual(System().getIP().count('.'), 3)

    def test_getUsage(self):
        us = System().getUsage()
        self.assertNotEqual(us.uptime, '')
        self.assertNotEqual(us.diskSize, 0)
        self.assertNotEqual(us.diskUsed, 0)
        self.assertNotEqual(us.diskUsedByLog, 0)
        self.assertNotEqual(us.diskPercentageUsed, 0)
        self.assertNotEqual(us.ramSize, 0)
        self.assertNotEqual(us.ramUsed, 0)
        self.assertNotEqual(us.ramFree, 0)
        self.assertNotEqual(us.cpuUsage, 0)

