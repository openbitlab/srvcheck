# MIT License

# Copyright (c) 2021-2026 Openbitlab Team

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

import unittest
import urllib.parse

from srvcheck.chains.octra import (
    TaskOctraBalanceReport,
    TaskOctraConsensusPeers,
    TaskOctraNewRelease,
    TaskOctraValidatorActive,
    TaskOctraVotingStatus,
)
from srvcheck.notification.notification import Emoji
from tests.mocks.mockchain import MockChainOctra

from .task_test import buildTaskEnv


class TestTaskOctraVotingStatus(unittest.TestCase):
    def test_voting_ok(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraVotingStatus, MockChainOctra)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_voting_disabled_needs_consecutive_checks(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraVotingStatus, MockChainOctra)
        c.voting = False
        c.votingReason = "not_ready"
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#voting is disabled (reason: not_ready) since 2 checks " + Emoji.NoLeader + " "
            ),
        )

    def test_voting_transient_disabled_resets(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraVotingStatus, MockChainOctra)
        c.voting = False
        t.run()
        c.voting = True
        t.run()
        c.voting = False
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_voting_recovery(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraVotingStatus, MockChainOctra)
        c.voting = False
        t.run()
        t.run()
        n.flush()
        c.voting = True
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 2)
        self.assertEqual(
            n.getLastEvent()[0],
            urllib.parse.quote("#voting enabled again " + Emoji.SyncOk + " "),
        )


class TestTaskOctraValidatorActive(unittest.TestCase):
    def test_active(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraValidatorActive, MockChainOctra)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_not_active(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraValidatorActive, MockChainOctra)
        c.membership = {"active": False, "scheduled": False, "activateEpoch": None, "setSize": 12}
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#validator is not in the active set (12 validators) " + Emoji.Delinq + " "
            ),
        )

    def test_scheduled(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraValidatorActive, MockChainOctra)
        c.membership = {"active": False, "scheduled": True, "activateEpoch": 1348560, "setSize": 12}
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#validator is not active yet, scheduled for activation at epoch 1348560 "
                + Emoji.Slow
                + " "
            ),
        )

    def test_recovery(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraValidatorActive, MockChainOctra)
        c.membership = {"active": False, "scheduled": False, "activateEpoch": None, "setSize": 12}
        t.run()
        n.flush()
        c.membership = {"active": True, "scheduled": False, "activateEpoch": None, "setSize": 13}
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 2)
        self.assertEqual(
            n.getLastEvent()[0],
            urllib.parse.quote("#validator is back in the active set " + Emoji.SyncOk + " "),
        )


class TestTaskOctraConsensusPeers(unittest.TestCase):
    def test_ok(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraConsensusPeers, MockChainOctra)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_low(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraConsensusPeers, MockChainOctra)
        c.consensusPeers = 2
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote("#node has only 2 consensus peers " + Emoji.Peers + " "),
        )

    def test_zero(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraConsensusPeers, MockChainOctra)
        c.consensusPeers = 0
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote("#node has 0 consensus peers " + Emoji.Peers + " "),
        )


class TestTaskOctraNewRelease(unittest.TestCase):
    def test_up_to_date(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraNewRelease, MockChainOctra)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 0)

    def test_new_release(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraNewRelease, MockChainOctra)
        c.latestVersion = "dd342e754c91df55a41b515c510369d637af2385"
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote("#has new release: dd342e75 (running 75d9ed1d) " + Emoji.Rel + " "),
        )


class TestTaskOctraBalanceReport(unittest.TestCase):
    def test_report(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraBalanceReport, MockChainOctra)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#balance: 10145.250000 OCT, weight: 1.000000 " + Emoji.ActStake + " "
            ),
        )

    def test_delta(self):
        c, n, t, s, p = buildTaskEnv(TaskOctraBalanceReport, MockChainOctra)
        t.run()
        n.flush()
        t.lastNotify = 0
        c.balance = 10146.75
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 2)
        self.assertEqual(
            n.getLastEvent()[0],
            urllib.parse.quote(
                "#balance: 10146.750000 OCT (+1.500000 since last report), weight: 1.000000 "
                + Emoji.ActStake
                + " "
            ),
        )
