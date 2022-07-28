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
        self.assertEqual(n.events[0], 'kicked out for not producing enough chunks, produced only 0 / 1 chunks' + Emoji.BlockMiss)

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
        self.assertEqual(n.events[0], 'kicked out for not producing enough blocks, produced only 0 / 1 chunks' + Emoji.BlockMiss)

    def test_no_kick(self):
        c, n, t, s = buildTaskEnv(TaskCheckKicked, MockChainNear)
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)
