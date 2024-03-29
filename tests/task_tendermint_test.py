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

from srvcheck.chains.tendermint import (
    TaskTendermintHealthError,
    TaskTendermintNewProposal,
)
from srvcheck.notification.notification import Emoji
from tests.mocks.mockchain import (
    MockChainTendermint,
    MockChainTendermint1,
    MockChainTendermint2,
    MockChainTendermint3,
)

from .task_test import buildTaskEnv


class TestTaskTendermintHealthError(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskTendermintHealthError, MockChainTendermint)
        c.healthOk = True
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskTendermintHealthError, MockChainTendermint)
        c.healthOk = False
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.getFirstEvent()[0], urllib.parse.quote("#health error! 🚨 "))


class TestTaskTendermintNewProposal(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s, p = buildTaskEnv(TaskTendermintNewProposal, MockChainTendermint)
        t.prev = [
            {
                "id": "1",
                "messages": [
                    {
                        "@type": "/cosmos.gov.v1.MsgExecLegacyContent",
                        "content": {
                            "@type": "/cosmos.params.v1beta1.ParameterChangeProposal",
                            "title": "Increase Signed Blocks Window Parameter to 2880",
                            "description": "Mamaki Testnet initially started with very strict slashing conditions. This proposal changes the signed_blocks_window to about 24 hours.",
                            "changes": [
                                {
                                    "subspace": "slashing",
                                    "key": "SignedBlocksWindow",
                                    "value": '"2880"',
                                }
                            ],
                        },
                        "authority": "celestia10d07y265gmmuvt4z0w9aw880jnsr700jtgz4v7",
                    }
                ],
                "status": "PROPOSAL_STATUS_VOTING_PERIOD",
                "final_tally_result": {
                    "yes_count": "0",
                    "abstain_count": "0",
                    "no_count": "0",
                    "no_with_veto_count": "0",
                },
                "submit_time": "2022-06-10T13:43:02.649255900Z",
                "deposit_end_time": "2022-06-12T13:43:02.649255900Z",
                "total_deposit": [{"denom": "utia", "amount": "100100000"}],
                "voting_start_time": "2022-06-10T13:49:16.069169911Z",
                "voting_end_time": "2022-06-12T13:49:16.069169911Z",
                "metadata": "",
            }
        ]
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s, p = buildTaskEnv(TaskTendermintNewProposal, MockChainTendermint1)
        t.prev = [
            {
                "proposal_id": "1",
                "content": {
                    "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                    "title": "upgrade client",
                    "description": "upgrade light client",
                    "subject_client_id": "07-tendermint-0",
                    "substitute_client_id": "07-tendermint-2",
                },
                "status": "PROPOSAL_STATUS_FAILED",
                "final_tally_result": {
                    "yes": "103022468704",
                    "abstain": "56100000",
                    "no": "115992000",
                    "no_with_veto": "90000000",
                },
                "submit_time": "2022-04-25T06:22:25.564973762Z",
                "deposit_end_time": "2022-05-09T06:22:25.564973762Z",
                "total_deposit": [{"denom": "ufis", "amount": "1000000000"}],
                "voting_start_time": "2022-04-25T06:23:01.163682205Z",
                "voting_end_time": "2022-04-26T06:23:01.163682205Z",
            }
        ]
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#got 1 new proposal: upgrade client " + Emoji.Proposal + " "
            ),
        )

    def test_alert_first_run(self):
        c, n, t, s, p = buildTaskEnv(TaskTendermintNewProposal, MockChainTendermint2)
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#got latest proposal: \nupgrade client " + Emoji.Proposal + " "
            ),
        )

    def test_alert_multiple_proposals(self):
        c, n, t, s, p = buildTaskEnv(TaskTendermintNewProposal, MockChainTendermint3)
        t.prev = [
            {
                "proposal_id": "1",
                "content": {
                    "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                    "title": "upgrade client",
                    "description": "upgrade light client",
                    "subject_client_id": "07-tendermint-0",
                    "substitute_client_id": "07-tendermint-2",
                },
                "status": "PROPOSAL_STATUS_FAILED",
                "final_tally_result": {
                    "yes": "103022468704",
                    "abstain": "56100000",
                    "no": "115992000",
                    "no_with_veto": "90000000",
                },
                "submit_time": "2022-04-25T06:22:25.564973762Z",
                "deposit_end_time": "2022-05-09T06:22:25.564973762Z",
                "total_deposit": [{"denom": "ufis", "amount": "1000000000"}],
                "voting_start_time": "2022-04-25T06:23:01.163682205Z",
                "voting_end_time": "2022-04-26T06:23:01.163682205Z",
            }
        ]
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(
            n.getFirstEvent()[0],
            urllib.parse.quote(
                "#got 2 new proposal: Increase Signed Blocks Window Parameter to 2880"
                + "\n"
                + "upgrade client "
                + Emoji.Proposal
                + " "
            ),
        )
