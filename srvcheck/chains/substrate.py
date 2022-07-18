from substrateinterface import SubstrateInterface
from srvcheck.tasks.task import hours, minutes
from .chain import Chain
from ..tasks import Task
from ..notification import Emoji
from ..utils import ConfItem, ConfSet

ConfSet.addItem(ConfItem('chain.collatorAddress', description='Collator address'))

class TaskSubstrateNewReferenda(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=60*10*60):
		super().__init__('TaskSubstrateNewReferenda',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
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
	def isPluggable(conf, chain):
		return chain.isParachain()

	def run(self):
		if self.prev is None:
			self.prev = self.chain.getRelayHeight()
		elif self.prev == self.chain.getRelayHeight():
			return self.notify(f'relay is stuck at block {self.prev} {Emoji.Stuck}')
		return False

class TaskWillValidateCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(10), notifyEvery=hours(1)):
		super().__init__('TaskWillValidateCheck',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isParachain()

	def run(self):
		session = self.chain.getSession()

		if self.prev is None:
			self.prev = session

		if self.prev != session:
			self.prev = session
			if self.chain.isValidator():
				return self.notify(f'will validate during the session {session + 1} {Emoji.Leader}')
			else:
				return self.notify(f'will not validate during the session {session + 1} {Emoji.NoLeader}')
		return False

class TaskBlockProductionCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(10), notifyEvery=minutes(10)):
		super().__init__('TaskBlockProductionCheck',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isParachain()

	def run(self):
		if self.chain.isCollating():
			block = self.chain.latestBlockProduced()
			if block != 0:
				if self.prev is None:
					self.prev = block
				elif self.prev == block:
					return self.notify(f'no block produced in the latest 10 minutes! Last block produced was {self.prev} {Emoji.BlockMiss}')
				self.prev = block
		return False

class TaskBlockProductionReport(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(10), notifyEvery=hours(1)):
		super().__init__('TaskBlockProductionReport',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None
		self.oc = 0

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isParachain()

	def run(self):
		if self.chain.isCollating():
			block = self.chain.latestBlockProduced()
			if block != 0:
				if self.prev is None:
					self.prev = block
					self.oc += 1

				if self.oc > 0:
					prevOc = self.oc
					self.oc = 0
					return self.notify(f'block produced in the last hour {prevOc} {Emoji.BlockProd}')

				if block != self.prev:
					self.oc += 1

				self.prev = block
		return False

class Substrate (Chain):
	TYPE = "substrate"
	NAME = ""
	BLOCKTIME = 15
	EP = 'http://localhost:9933/'
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskWillValidateCheck, TaskBlockProductionCheck, TaskBlockProductionReport] #[TaskSubstrateNewReferenda]

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
		return abs(c['currentBlock'] - c['highestBlock']) > 32

	def getRelayHeight(self):
		si = self.getSubstrateInterface()
		result = si.query(module='ParachainSystem', storage_function='ValidationData', params=[])
		return result.value["relay_parent_number"]

	def getParachainId(self):
		si = self.getSubstrateInterface()
		result = si.query(module='ParachainInfo', storage_function='ParachainId', params=[])
		return result.value

	def isParachain(self):
		try:
			self.getParachainId()
			return True
		except:
			return False

	def getSession(self):
		si = self.getSubstrateInterface()
		result = si.query(module='Session', storage_function='CurrentIndex', params=[])
		return result.value

	def isValidator(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='Session', storage_function='QueuedKeys', params=[])
			for v in result.value:
				if(v[0] == f'{collator}'):
					return True
		return False

	# Check collator on Shiden/Shibuya
	def isCollating(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='CollatorSelection', storage_function='Candidates', params=[])
			for c in result.value:
				if c['who'] == f'{collator}':
					return True
		return False

	def latestBlockProduced(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='CollatorSelection', storage_function='LastAuthoredBlock', params=[collator])
			return result.value
		return False
