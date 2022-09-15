from .chain import Chain

class Tezos (Chain):
	TYPE = "tezos"
	NAME = "tezos"
	BLOCKTIME = 60
	EP = 'http://127.0.0.1:8732/'
	CUSTOM_TASKS = []

	@staticmethod
	def detect(conf):
		try:
			Tezos(conf).getVersion()
			return True
		except:
			return False

	def getLatestVersion(self):
		raise Exception('Abstract getLatestVersion()')

	def getVersion(self):
		a = self.getCall('version')
		return f'v%s.%s.0' % (a['major'], a['minor'])

	def getHeight(self):
		return self.getCall('chains/main/blocks/head/helpers/current_level')['level']

	def getBlockHash(self):
		return self.getCall('chains/main/blocks/head')['hash']

	def getPeerCount(self):
		return len(self.getCall('network/peers'))

	def getNetwork(self):
		return self.getCall('network/version')['chain_name']

	def isStaking(self):
		return False

	def isSynching(self):
		return False
