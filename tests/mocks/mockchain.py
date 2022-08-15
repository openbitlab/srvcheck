from srvcheck.chains import Chain


class MockChain(Chain):
    NAME = "mockchain"
    TYPE = "testchain"
    BLOCKTIME = 60
    EP = "http://localhost:26657/"

    peers = 0

    hash = '0x1234567890'
    height = 0

    network = 'mocknet'
    version = 'v0.0.0'
    latestVersion = 'v0.0.0'
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
            raise Exception('Mockchain is not healthy')


class MockChainTendermint(MockChain):
    latestProposals = [{"proposal_id":"2","content":{"@type":"/ibc.core.client.v1.ClientUpdateProposal","title":"upgrade client","description":"upgrade light client","subject_client_id":"07-tendermint-0","substitute_client_id":"07-tendermint-2"},
		"status":"PROPOSAL_STATUS_VOTING_PERIOD","final_tally_result":{"yes":"103022468704","abstain":"56100000","no":"115992000","no_with_veto":"90000000"},"submit_time":"2022-04-25T06:22:25.564973762Z","deposit_end_time":"2022-05-09T06:22:25.564973762Z","total_deposit":[{"denom":"ufis","amount":"1000000000"}],
		"voting_start_time":"2022-04-25T06:23:01.163682205Z","voting_end_time":"2022-04-26T06:23:01.163682205Z"}, {"proposal_id":"1","content":{"@type":"/ibc.core.client.v1.ClientUpdateProposal","title":"upgrade client","description":"upgrade light client","subject_client_id":"07-tendermint-0","substitute_client_id":"07-tendermint-2"},
		"status":"PROPOSAL_STATUS_FAILED","final_tally_result":{"yes":"103022468704","abstain":"56100000","no":"115992000","no_with_veto":"90000000"},"submit_time":"2022-04-25T06:22:25.564973762Z","deposit_end_time":"2022-05-09T06:22:25.564973762Z","total_deposit":[{"denom":"ufis","amount":"1000000000"}],
		"voting_start_time":"2022-04-25T06:23:01.163682205Z","voting_end_time":"2022-04-26T06:23:01.163682205Z"}]

    def getLatestProposals(self):
        return self.latestProposals

class MockChainTendermint1(MockChain):
    latestProposals = [{"iproposal_idd":"2","content":{"@type":"/ibc.core.client.v1.ClientUpdateProposal","title":"upgrade client","description":"upgrade light client","subject_client_id":"07-tendermint-0","substitute_client_id":"07-tendermint-2"},
		"status":"PROPOSAL_STATUS_FAILED","final_tally_result":{"yes":"103022468704","abstain":"56100000","no":"115992000","no_with_veto":"90000000"},"submit_time":"2022-04-25T06:22:25.564973762Z","deposit_end_time":"2022-05-09T06:22:25.564973762Z","total_deposit":[{"denom":"ufis","amount":"1000000000"}],
		"voting_start_time":"2022-04-25T06:23:01.163682205Z","voting_end_time":"2022-04-26T06:23:01.163682205Z"}, {"proposal_id":"1","content":{"@type":"/ibc.core.client.v1.ClientUpdateProposal","title":"upgrade client","description":"upgrade light client","subject_client_id":"07-tendermint-0","substitute_client_id":"07-tendermint-2"},
		"status":"PROPOSAL_STATUS_FAILED","final_tally_result":{"yes":"103022468704","abstain":"56100000","no":"115992000","no_with_veto":"90000000"},"submit_time":"2022-04-25T06:22:25.564973762Z","deposit_end_time":"2022-05-09T06:22:25.564973762Z","total_deposit":[{"denom":"ufis","amount":"1000000000"}],
		"voting_start_time":"2022-04-25T06:23:01.163682205Z","voting_end_time":"2022-04-26T06:23:01.163682205Z"}]

    def getLatestProposals(self):
        return self.latestProposals

class MockChainNear(MockChain):
    EPOCHTIME = 10000
    kicked_set = [{
        "account_id": "yuriinear.factory.shardnet.near",
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
        raise Exception('No block hash')
