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

from srvcheck.chains import Chain


class MockChain(Chain):
    NAME = "mockchain"
    TYPE = "testchain"
    BLOCKTIME = 60
    EP = "http://localhost:26657/"

    peers = 0

    hash = "0x1234567890"
    height = 0

    network = "mocknet"
    version = "v0.0.0"
    latestVersion = "v0.0.0"
    healthOk = True

    def __init__(self, conf):
        super().__init__(conf)

    @staticmethod
    def detect(conf):
        return True

    def getPeerCount(self):
        return self.peers

    def getBlockHash(self):
        return self.hash

    def getHeight(self):
        return self.height

    def getNetwork(self):
        return self.network

    def getLatestVersion(self):
        return self.latestVersion

    def getVersion(self):
        return self.version

    def getLocalVersion(self):
        return self.getVersion()

    def isSynching(self):
        return False

    ## Tendermint

    def getHealth(self):
        if self.healthOk:
            return []
        else:
            raise Exception("Mockchain is not healthy")


class MockChainTendermint(MockChain):
    latestProposals = [
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

    def getLatestProposals(self):
        return [
            p
            for p in self.latestProposals
            if p["status"] == "PROPOSAL_STATUS_VOTING_PERIOD"
        ]


class MockChainTendermint1(MockChain):
    latestProposals = [
        {
            "proposal_id": "2",
            "content": {
                "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                "title": "upgrade client",
                "description": "upgrade light client",
                "subject_client_id": "07-tendermint-0",
                "substitute_client_id": "07-tendermint-2",
            },
            "status": "PROPOSAL_STATUS_VOTING_PERIOD",
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
        },
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
        },
    ]

    def getLatestProposals(self):
        return [
            p
            for p in self.latestProposals
            if p["status"] == "PROPOSAL_STATUS_VOTING_PERIOD"
        ]


class MockChainTendermint2(MockChain):
    latestProposals = [
        {
            "proposal_id": "1",
            "content": {
                "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                "title": "upgrade client",
                "description": "upgrade light client",
                "subject_client_id": "07-tendermint-0",
                "substitute_client_id": "07-tendermint-2",
            },
            "status": "PROPOSAL_STATUS_VOTING_PERIOD",
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

    def getLatestProposals(self):
        return [
            p
            for p in self.latestProposals
            if p["status"] == "PROPOSAL_STATUS_VOTING_PERIOD"
        ]


class MockChainTendermint3(MockChain):
    latestProposals = [
        {
            "proposal_id": "3",
            "content": {
                "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                "title": "Increase Signed Blocks Window Parameter to 2880",
                "description": "upgrade light client",
                "subject_client_id": "07-tendermint-0",
                "substitute_client_id": "07-tendermint-2",
            },
            "status": "PROPOSAL_STATUS_VOTING_PERIOD",
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
        },
        {
            "proposal_id": "2",
            "content": {
                "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                "title": "upgrade client",
                "description": "upgrade light client",
                "subject_client_id": "07-tendermint-0",
                "substitute_client_id": "07-tendermint-2",
            },
            "status": "PROPOSAL_STATUS_VOTING_PERIOD",
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
        },
        {
            "proposal_id": "1",
            "content": {
                "@type": "/ibc.core.client.v1.ClientUpdateProposal",
                "title": "upgrade client",
                "description": "upgrade light client",
                "subject_client_id": "07-tendermint-0",
                "substitute_client_id": "07-tendermint-2",
            },
            "status": "PROPOSAL_STATUS_VOTING_PERIOD",
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
        },
    ]

    def getLatestProposals(self):
        return [
            p
            for p in self.latestProposals
            if p["status"] == "PROPOSAL_STATUS_VOTING_PERIOD"
        ]


class MockChainNear(MockChain):
    EPOCHTIME = 10000
    kicked_set = [
        {
            "account_id": "yuriinear.factory.shardnet.near",
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
    pool_id = "openbitlab.factory.shardnet.near"
    epoch = 12

    def getKickedout(self):
        return self.kicked_set

    def getPoolId(self):
        return self.pool_id

    def getEpoch(self):
        return self.epoch


class MockChainNoBlockHash(MockChain):
    def getBlockHash(self):
        raise Exception("No block hash")
