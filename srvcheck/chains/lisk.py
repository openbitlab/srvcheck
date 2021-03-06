import json
from .chain import Chain
from ..utils import Bash

class Lisk (Chain):
	TYPE = "lisk"
	NAME = "lisk"
	BLOCKTIME = 15
	EP = 'http://localhost:9933/'
	CUSTOM_TASKS = []

	@staticmethod
	def detect(conf):
		try:
			Lisk(conf).getVersion()
			return True
		except:
			return False

	def _nodeInfo(self):
		return json.loads(Bash('sudo -u lisk lisk-core node:info').value())

	def _forgingStatus(self):
		return json.loads(Bash('sudo -u lisk lisk-core forging:info').value())

	def getLatestVersion(self):
		raise Exception('Abstract getLatestVersion()')

	def getLocalVersion(self):
		return self.getVersion()

	def getVersion(self):
		return self._nodeInfo()['version']

	def getHeight(self):
		return self._nodeInfo()['height']

	def getBlockHash(self):
		return self._nodeInfo()['lastBlockID']

	def getPeerCount(self):
		return len(self._nodeInfo()['network']['seedPeers'])

	def getNetwork(self):
		return self._nodeInfo()['genesisConfig']['communityIdentifier']

	def isStaking(self):
		return len(self._forgingStatus()) > 0

	def isSynching(self):
		return self._nodeInfo()['syncing']
