from .chain import Chain
from ..tasks import Task

class TaskSubstrateNewReferenda(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=60*60, notifyEvery=60*10*60):
		super().__init__('TaskSubstrateNewReferenda',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		pass 

class Substrate (Chain):
	TYPE = "substrate"
	NAME = ""
	BLOCKTIME = 15 
	EP = 'http://localhost:9933/'

	def __init__(self, conf):
		super().__init__(conf)
		self.TASKS = []
		self.TASKS.append(TaskSubstrateNewReferenda)

	def detect(conf):
		try:
			Substrate(conf).getVersion()
			return True
		except:
			return False

	def getLatestVersion(self):
		raise Exception('Abstract getLatestVersion()')

	def getVersion(self):
		return self.rpcCall('system_version')

	def getHeight(self):
		raise Exception('Abstract getHeight()')

	def getBlockHash(self):
		return self.rpcCall('chain_getBlockHash')

	def getPeerCount(self):
		return self.rpcCall('system_health')['peers']

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		raise Exception('Abstract isStaking()')