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

import unittest
import urllib.parse

from srvcheck.chains.near import TaskNearCheckKicked
from srvcheck.notification.notification import Emoji
from tests.mocks.mockchain import MockChainNear

from .task_test import buildTaskEnv


class TestTaskNearKickedout(unittest.TestCase):
    def test_chunk(self):
        c, n, t, s, p = buildTaskEnv(TaskNearCheckKicked, MockChainNear)
        c.epoch = 18
        t.run()
        c.kicked_set = [
            {
                "account_id": "openbitlab.factory.shardnet.near",
                "reason": {"NotEnoughChunks": {"expected": 1, "produced": 0}},
            },
            {
                "account_id": "zarola.factory.shardnet.near",
                "reason": {"NotEnoughChunks": {"expected": 1, "produced": 0}},
            },
            {
                "account_id": "zetsi.factory.shardnet.near",
                "reason": {"NotEnoughBlocks": {"expected": 4, "produced": 0}},
            },
        ]
        c.epoch = 21
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#kicked out for not producing enough chunks, produced only 0 / 1 chunks "
                + Emoji.BlockMiss
                + " "
            ),
        )

    def test_blocks(self):
        c, n, t, s, p = buildTaskEnv(TaskNearCheckKicked, MockChainNear)
        c.epoch = 18
        t.run()
        c.kicked_set = [
            {
                "account_id": "openbitlab.factory.shardnet.near",
                "reason": {"NotEnoughBlocks": {"expected": 1, "produced": 0}},
            },
            {
                "account_id": "zarola.factory.shardnet.near",
                "reason": {"NotEnoughChunks": {"expected": 1, "produced": 0}},
            },
            {
                "account_id": "zetsi.factory.shardnet.near",
                "reason": {"NotEnoughBlocks": {"expected": 4, "produced": 0}},
            },
        ]
        c.epoch = 21
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#kicked out for not producing enough blocks, produced only 0 / 1 blocks "
                + Emoji.BlockMiss
                + " "
            ),
        )

    def test_notenoughstake(self):
        c, n, t, s, p = buildTaskEnv(TaskNearCheckKicked, MockChainNear)
        c.epoch = 21
        t.run()
        c.kicked_set = [
            {
                "account_id": "openbitlab.factory.shardnet.near",
                "reason": {
                    "NotEnoughStake": {
                        "stake_u128": "95812130118219522152726186666",
                        "threshold_u128": "95829541958075649131178786912",
                    }
                },
            },
            {
                "account_id": "zarola.factory.shardnet.near",
                "reason": {"NotEnoughChunks": {"expected": 1, "produced": 0}},
            },
            {
                "account_id": "zetsi.factory.shardnet.near",
                "reason": {"NotEnoughBlocks": {"expected": 4, "produced": 0}},
            },
        ]
        c.epoch = 30
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#kicked out, missing 17 Near to stake threshold " + Emoji.LowBal + " "
            ),
        )

    def test_no_kick(self):
        c, n, t, s, p = buildTaskEnv(TaskNearCheckKicked, MockChainNear)
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)
