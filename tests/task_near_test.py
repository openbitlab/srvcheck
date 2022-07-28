import unittest

from srvcheck.notification.notification import Emoji
from srvcheck.chains.near import TaskCheckKicked
from tests.mocks.mockchain import MockChainNear
from .task_test import buildTaskEnv


class TestTaskNearKickedout(unittest.TestCase):
    def test_chunk(self):
        c, n, t, s = buildTaskEnv(TaskCheckKicked, MockChainNear)
        c.kicked_set = [{
            "account_id": "openbitlab.factory.shardnet.near",
            "reason": {
                "NotEnoughChunks": {
                    "expected": 1,
                    "produced": 0
                }
            }
        },
            {
                "account_id": "zarola.factory.shardnet.near",
                "reason": {
                    "NotEnoughChunks": {
                        "expected": 1,
                        "produced": 0
                    }
                }
            },
            {
                "account_id": "zetsi.factory.shardnet.near",
                "reason": {
                    "NotEnoughBlocks": {
                        "expected": 4,
                        "produced": 0
                    }
                }
            }
        ]
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'kicked out for not producing enough chunks, produced only 0 / 1 chunks ' + Emoji.BlockMiss)

    def test_blocks(self):
        c, n, t, s = buildTaskEnv(TaskCheckKicked, MockChainNear)
        c.kicked_set = [{
            "account_id": "openbitlab.factory.shardnet.near",
            "reason": {
                "NotEnoughBlocks": {
                    "expected": 1,
                    "produced": 0
                }
            }
        },
            {
                "account_id": "zarola.factory.shardnet.near",
                "reason": {
                    "NotEnoughChunks": {
                        "expected": 1,
                        "produced": 0
                    }
                }
            },
            {
                "account_id": "zetsi.factory.shardnet.near",
                "reason": {
                    "NotEnoughBlocks": {
                        "expected": 4,
                        "produced": 0
                    }
                }
            }
        ]
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'kicked out for not producing enough blocks, produced only 0 / 1 chunks ' + Emoji.BlockMiss)

    def test_notenoughstake(self):
        c, n, t, s = buildTaskEnv(TaskCheckKicked, MockChainNear)
        c.kicked_set = [{
            "account_id": "openbitlab.factory.shardnet.near",
            "reason": {
                "NotEnoughStake": {
                    "stake_u128": "95812130118219522152726186666",
                    "threshold_u128": "95829541958075649131178786912"
                }
            }
        },
            {
                "account_id": "zarola.factory.shardnet.near",
                "reason": {
                    "NotEnoughChunks": {
                        "expected": 1,
                        "produced": 0
                    }
                }
            },
            {
                "account_id": "zetsi.factory.shardnet.near",
                "reason": {
                    "NotEnoughBlocks": {
                        "expected": 4,
                        "produced": 0
                    }
                }
            }
        ]
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'kicked out, missing 17 to stake threshold ' + Emoji.LowBal)

    def test_no_kick(self):
        c, n, t, s = buildTaskEnv(TaskCheckKicked, MockChainNear)
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)
