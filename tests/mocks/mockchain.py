from srvcheck.chains import Chain
import json


class MockChain (Chain):
	NAME = "mockchain"
	BLOCKTIME = 60
	EP = "http://localhost:26657/"

	peers = 0
	hash = '0x1234567890'
	network = 'mocknet'
	version = 'v0.0.0'
	latestVersion = 'v0.0.0'
	healthOk = True
	latestProposal = """{"proposals":[{"proposal_id":"3","content":{"@type":"/ibc.core.client.v1.ClientUpdateProposal","title":"Upgrade IBC client","description":"Upgrade the expired client to an active client","subject_client_id":"07-tendermint-0","substitute_client_id":"07-tendermint-3"},
	"status":"PROPOSAL_STATUS_PASSED","final_tally_result":{"yes":"104002179704","abstain":"107000000","no":"47000000","no_with_veto":"0"},"submit_time":"2022-04-27T13:02:49.636982639Z","deposit_end_time":"2022-05-11T13:02:49.636982639Z","total_deposit":[{"denom":"ufis","amount":"1000000000"}],
	"voting_start_time":"2022-04-27T13:03:09.707806299Z","voting_end_time":"2022-04-28T13:03:09.707806299Z"}],"pagination":{"next_key":"AAAAAAAAAAI=","total":"0"}}"""

	def __init__(self, conf):
		super().__init__(conf)

	def detect(conf):
		return True

	def getPeerCount(self):
		return self.peers

	def getBlockHash(self):
		return self.hash

	def getNetwork(self):
		return self.network
		
	def getLatestVersion(self):
		return self.latestVersion
	
	def getVersion(self):
		return self.version

	## Tendermint
	
	def getHealth(self):
		if self.healthOk:
			return []
		else:
			raise Exception('Mockchain is not healthy')

	def getLatestProposal(self):
		
		return json.loads(self.latestProposal)["proposals"][0]
	
