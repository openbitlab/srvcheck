# MIT License

# Copyright (c) 2021-2023 Openbitlab Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import configparser
import unittest

from srvcheck.utils import Bash, ConfSet, System
from srvcheck.utils.confset import ConfItem


class TestUtilsBash(unittest.TestCase):
    def test_echo(self):
        self.assertEqual(Bash('echo "Hello World!"').value(), "Hello World!")


class TestUtilsSystem(unittest.TestCase):
    def test_getIP(self):
        pass
        # Can't test on CI
        # self.assertEqual(System().getIP().count('.'), 3)

    def test_getUsage(self):
        C = {
            "chain": {
                "name": "test",
                "endpoint": "http://localhost:8080",
                "blockTime": 10,
                "mountPoint": "/",
            }
        }

        confRawUsage = configparser.ConfigParser()
        confRawUsage.optionxform = str
        confRawUsage.read_dict(C)

        confUsage = ConfSet(confRawUsage)
        ConfSet.addItem(ConfItem("chain.mountPoint", "/", str))
        us = System(confUsage).getUsage()
        self.assertNotEqual(us.bootTime, "")
        self.assertNotEqual(us.diskSize, 0)
        self.assertNotEqual(us.diskUsed, 0)
        self.assertNotEqual(us.diskUsedByLog, 0)
        self.assertNotEqual(us.diskPercentageUsed, 0)
        self.assertNotEqual(us.ramSize, 0)
        self.assertNotEqual(us.ramUsed, 0)
        self.assertNotEqual(us.ramFree, 0)
        # self.assertNotEqual(int(us.cpuUsage), 0)


class TestUtilConfSet(unittest.TestCase):
    CONF = {
        "chain": {
            "name": "test",
            "endpoint": "http://localhost:8080",
            "type": "",
            "blockTime": 10,
            "service": "",
            "activeSet": "",
        }
    }

    confRaw = configparser.ConfigParser()
    confRaw.optionxform = str
    confRaw.read_dict(CONF)

    conf = ConfSet(confRaw)
    ConfSet.addItem(ConfItem("chain.type", "mockchain", str))
    ConfSet.addItem(ConfItem("chain.name", None, str))
    ConfSet.addItem(ConfItem("chain.endpoint", None, str))
    ConfSet.addItem(ConfItem("chain.blockTime", None, int))
    ConfSet.addItem(ConfItem("chain.service", None, str))

    def test_getFromConfExistingString(self):
        self.assertEqual(
            self.conf.getOrDefault("chain.endpoint"), "http://localhost:8080"
        )

    def test_getFromConfExistingInteger(self):
        self.assertEqual(self.conf.getOrDefault("chain.blockTime"), 10)

    def test_getFromConfNotExistingString(self):
        self.assertEqual(self.conf.getOrDefault("chain.service"), None)

    def test_getFromConfNotExistingDefault(self):
        self.assertEqual(
            self.conf.getOrDefault("chain.activeSet", failSafe=True, cast=int), None
        )

    def test_getFromConfExistingButEmptyDefault(self):
        self.assertEqual(self.conf.getOrDefault("chain.type"), "mockchain")
