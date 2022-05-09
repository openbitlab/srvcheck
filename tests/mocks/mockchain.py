from srvcheck.chains import Chain


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

	def __init__(self, conf):
		super().__init__(conf)

	def detect(conf):
		return True

	def getPeerNumber(self):
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