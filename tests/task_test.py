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
import urllib.parse

from srvcheck.main import Services
from srvcheck.notification.notification import Emoji
from srvcheck.tasks import (
    TaskChainLowPeer,
    TaskChainStuck,
    TaskSystemCpuAlert,
    TaskSystemDiskAlert,
    hours,
    minutes,
)
from srvcheck.tasks.tasknewrelease import TaskNewRelease, versionCompare
from srvcheck.utils.confset import ConfItem, ConfSet

from .mocks import MockChain, MockChainNoBlockHash, MockNotification, MockSystem

CONFRAW = {
    "name": "Test",
    "chain": {
        "endpoint": "http://localhost:8080",
    },
}
CONF = ConfSet(CONFRAW)


def buildTaskEnv(tt, chainClass=MockChain):
    c = chainClass(CONF)
    n = MockNotification(CONF)
    s = MockSystem(CONF)
    p = None
    services = Services(CONF, n, s, c, p)
    t = tt(services)
    return (c, n, t, s, p)


class TestTimingUtilities(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(minutes(13), 13 * 60)

    def test_hours(self):
        self.assertEqual(hours(13), 13 * 60 * 60)


class TestTaskSystemCpuAlert(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskSystemCpuAlert)
        s.usage.cpuUsage = 10
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskSystemCpuAlert)
        s.usage.cpuUsage = 99
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#CPU average usage is above 90% (99% in the last 2 checks) ⚠ "
            ),
        )


class TestTaskSystemDiskAlert(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskSystemDiskAlert)
        s.usage.diskPercentageUsed = 10
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskSystemDiskAlert)
        s.usage.diskPercentageUsed = 99
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#disk usage is above 90% (99%) (/var/log: 0.0G, /: 0.0G) 💾 "
            ),
        )


class TestTaskChainLowPeer(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskChainLowPeer)
        c.peers = 12
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert_error(self):
        c, n, t, s, p = buildTaskEnv(TaskChainLowPeer)
        c.peers = 0
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote("#chain has 0 peers" + " " + Emoji.Peers + " "),
        )

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskChainLowPeer)
        c.peers = 1
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote("#chain has only 1 peers" + " " + Emoji.Peers + " "),
        )


class TestTaskChainStuck(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskChainStuck)
        c.hash = "0x1234567890"
        t.run()
        c.hash = "0x1234567891"
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskChainStuck)
        c.hash = "0x1234567890"
        t.run()
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#chain is stuck at block 0x1234567890 since 0 seconds (1)"
                + " "
                + Emoji.Stuck
                + " "
            ),
        )

    def test_noblockhash(self):
        c, n, t, s, p = buildTaskEnv(TaskChainStuck, MockChainNoBlockHash)
        c.height = 0
        t.run()
        c.height = 1
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_noblockhash_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskChainStuck, MockChainNoBlockHash)
        c.height = 1
        t.run()
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#chain is stuck at block 1 since 0 seconds (1)"
                + " "
                + Emoji.Stuck
                + " "
            ),
        )


class TestTaskNewRelease(unittest.TestCase):
    CONF = {
        "chain": {
            "name": "test",
            "endpoint": "http://localhost:8080",
            "type": "",
            "blockTime": 10,
            "service": "",
            "activeSet": "",
            "localVersion": "v0.0.1",
        }
    }

    confRaw = configparser.ConfigParser()
    confRaw.optionxform = str
    confRaw.read_dict(CONF)

    conf = ConfSet(confRaw)
    cf = "/etc/srvcheck.conf"
    conf.addItem(ConfItem("configFile", cf, str))
    conf.addItem(ConfItem("chain.localVersion", "v0.0.1", str))

    def test_VersionCompare(self):
        self.assertEqual(versionCompare("v1.0.0", "v1.0.0"), 0)
        self.assertEqual(versionCompare("v1.0.0", "v1.0.1"), -1)
        self.assertEqual(versionCompare("v1.2.0", "v1.0.1"), 1)
        self.assertEqual(versionCompare("v1.1.0-rc.2", "v1.1.0-rc.3"), -1)
        self.assertEqual(versionCompare("v1.1.0", "v1.1.0-rc.3"), 1)

    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskNewRelease)
        t.conf = self.conf
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskNewRelease)
        t.conf = self.conf
        c.latestVersion = "v1.1.1"
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(f"#has new release: {c.latestVersion} {Emoji.Rel} "),
        )
