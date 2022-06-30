from substrateinterface import SubstrateInterface


from srvcheck.tasks.task import hours
from .chain import Chain
from ..tasks import Task
from ..notification import Emoji
from ..utils import Bash


class TaskSubstrateNewReferenda(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=60*10*60):
		super().__init__('TaskSubstrateNewReferenda',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		n = self.chain.getNetwork()
		if not (n in ['Kusama', 'Polkadot']):
			return False

		si = self.chain.getSubstrateInterface()
		result = si.query(
			module='Referenda',
			storage_function='referendumCount',
			params=[]
		)

		count = result.value

		if self.prev is None:
			self.prev = count
			return False

		if count > self.prev:
			self.prev = count
			return self.notify(f'New referendum found on {n}: {n, count - 1}')

class TaskRelayChainStuck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=30, notifyEvery=60*5):
		super().__init__('TaskRelayChainStuck',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf):
		service = conf.getOrDefault('chain.service')
		s = Bash('systemctl cat '+service).value()
		if "--parachain-id" in s:
			return True
		return False

	def run(self):
		if self.prev is None:
			self.prev = self.chain.getRelayHeight()
		elif self.prev == self.chain.getRelayHeight():
			return self.notify(f'Relay is stuck at block {self.prev} {Emoji.Stuck}')
		return False


class Substrate (Chain):
	TYPE = "substrate"
	NAME = ""
	BLOCKTIME = 15
	EP = 'http://localhost:9933/'
	CUSTOM_TASKS = ['TaskRelayChainStuck'] #[TaskSubstrateNewReferenda]

	def __init__(self, conf):
		super().__init__(conf)
		self.rpcMethods = super().rpcCall('rpc_methods', [])['methods']

	def rpcCall(self, method, params=[]):
		if method in self.rpcMethods:
			return super().rpcCall(method, params)
		return None

	def getSubstrateInterface(self):
		return SubstrateInterface(url=self.EP)

	@staticmethod
	def detect(conf):
		try:
			Substrate(conf).getVersion()
			return True
		except:
			return False

	def getVersion(self):
		return self.rpcCall('system_version')

	def getLocalVersion(self):
		return self.getVersion()

	def getHeight(self):
		return int(self.rpcCall('chain_getHeader', [self.getBlockHash()])['number'], 16)

	def getBlockHash(self):
		return self.rpcCall('chain_getBlockHash')

	def getPeerCount(self):
		return int(self.rpcCall('system_health')['peers'])

	def getNetwork(self):
		return self.rpcCall('system_chain')

	def isStaking(self):
		c = self.rpcCall('babe_epochAuthorship')
		if len(c.keys()) == 0:
			return False

		cc = c[c.keys()[0]]
		return (len(cc['primary']) + len(cc['secondary']) + len(cc['secondary_vrf'])) > 0

	def isSynching(self):
		c = self.rpcCall('system_syncState')
		return c['highestBlock'] < c['currentBlock']

	def getRelayHeight(self):
		c = self.rpcCall('chain_getBlock')['extrinsics'][0]['method']['args']['data']['validationData']['relayParentNumber']
		return c
