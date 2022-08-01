from substrateinterface import SubstrateInterface
from substrateinterface.exceptions import StorageFunctionNotFound
from srvcheck.tasks.task import hours, minutes
from .chain import Chain
from ..tasks import Task
from ..notification import Emoji
from ..utils import ConfItem, ConfSet, Bash

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
			storage_function='ReferendumCount',
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

class TaskBlockProductionCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(20), notifyEvery=minutes(20)):
		super().__init__('TaskBlockProductionCheck',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isParachain()

	def run(self):
		if self.chain.isCollating():
			block = self.chain.latestBlockProduced()
			if block > 0:
				if self.prev is None:
					self.prev = block
				elif self.prev == block:
					return self.notify(f'no block produced in the latest 20 minutes! Last block produced was {self.prev} {Emoji.BlockMiss}')
				self.prev = block
		return False

class TaskBlockProductionReport(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(10), notifyEvery=hours(1)):
		super().__init__('TaskBlockProductionReport',
			  conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None
		self.prevBlock = None
		self.lastBlockChecked = None
		self.totalBlockChecked = 0
		self.oc = 0

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isParachain()

	def run(self):
		s = self.chain.getSession()
		session = s['current'] if isinstance(s, dict) and 'current' in s else s

		if self.prev is None:
			self.prev = session

		block = 0
		orb = self.chain.moonbeamAssignedOrbiter()
		if self.chain.isCollating():
			block = self.chain.latestBlockProduced()
			if block > 0:
				if self.prevBlock is None:
					self.prevBlock = block
					self.oc += 1

				if block != self.prevBlock:
					self.oc += 1

				self.prevBlock = block
			elif block == -1:
				startingRoundBlock = s['first']
				currentBlock = self.chain.getHeight()
				blocksToCheck = [b for b in self.chain.getExpectedBlocks() if b <= currentBlock and (self.lastBlockChecked is None or b > self.lastBlockChecked) and b >= startingRoundBlock]
				for b in blocksToCheck:
					a = self.chain.getBlockAuthor(b)
					collator = orb if orb != '0x0' and orb is not None else self.conf.getOrDefault('chain.collatorAddress')
					if a.lower() == collator.lower():
						self.oc += 1
					self.lastBlockChecked = b
					self.totalBlockChecked += 1

		if self.prev != session:
			self.prev = session
			report = f'{self.oc} block produced last {"round" if isinstance(s, dict) and "current" in s else "session"}'
			if self.totalBlockChecked > 0:
				report = f'{report} out of {self.totalBlockChecked} ({self.oc / self.totalBlockChecked * 100:.2f} %)'
				self.totalBlockChecked = 0
			report = f'{report} {Emoji.BlockProd}'
			self.oc = 0
			if self.chain.isValidator():
				return self.notify(f'will validate during the session {session + 1} {Emoji.Leader}\n{report}')
			elif orb != '0x0':
				if orb is None:
					return self.notify(f'is not the selected orbiter for the session {session + 1} {Emoji.NoOrbiter}\n{report}')
				else:
					return self.notify(f'is the selected orbiter for the session {session + 1} {Emoji.Orbiter}\n{report}')
			elif block != -1:
				return self.notify(f'will not validate during the session {session + 1} {Emoji.NoLeader}\n{report}')
			else:
				return self.notify(report)
		return False

class Substrate (Chain):
	TYPE = "substrate"
	NAME = ""
	BLOCKTIME = 15
	EP = 'http://localhost:9933/'
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskSubstrateNewReferenda, TaskBlockProductionCheck, TaskBlockProductionReport]

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
		try:
			# Check session on Moonbase/Moonriver, Mangata
			result = si.query(module='ParachainStaking', storage_function='Round', params=[])
			return result.value
		except StorageFunctionNotFound:
			# Check session on Shiden/Shibuya
			result = si.query(module='Session', storage_function='CurrentIndex', params=[])
			return result.value

	def isValidator(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			try:
				# Check validator on Shiden/Shibuya, Mangata
				si = self.getSubstrateInterface()
				result = si.query(module='Session', storage_function='QueuedKeys', params=[])
				for v in result.value:
					if v[0].lower() == f'{collator}'.lower():
						return True
			except StorageFunctionNotFound:
				return False
		return False

	def isCollating(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			try:
				# Check collator on Shiden/Shibuya
				result = si.query(module='CollatorSelection', storage_function='Candidates', params=[])
				for c in result.value:
					if c['who'].lower() == f'{collator}'.lower():
						return True
				result = si.query(module='CollatorSelection', storage_function='Invulnerables', params=[])
				for c in result.value:
					if c.lower() == f'{collator}'.lower():
						return True
			except StorageFunctionNotFound:
				# Check collator on Moonbase/Moonriver, Mangata
				c = self.moonbeamAssignedOrbiter()
				if c != '0x0' and c is not None:
					collator = c
				result = si.query(module='ParachainStaking', storage_function='SelectedCandidates', params=[])
				for c in result.value:
					if c.lower() == collator.lower():
						return True
		return False

	def latestBlockProduced(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			try:
				# Check last block produced on Shiden/Shibuya
				si = self.getSubstrateInterface()
				result = si.query(module='CollatorSelection', storage_function='LastAuthoredBlock', params=[collator])
				return result.value
			except StorageFunctionNotFound:
				return -1
		return 0

	def getExpectedBlocks(self):
		serv = self.conf.getOrDefault('chain.service')
		if serv:
			blocks = Bash(f"journalctl -u {serv} --no-pager --since '60 min ago' | grep -Eo 'Prepared block for proposing at [0-9]+' | sed 's/[^0-9]'//g").value().split("\n")
			blocks = [int(b) for b in blocks if b != '']
			return blocks
		return []

	def getBlockAuthor(self, block):
		try:
			return self.rpcCall('eth_getBlockByNumber', [hex(block), True])['author']
		except:
			# Check block author Mangata
			return self.checkAuthoredBlock(block)

	def moonbeamAssignedOrbiter(self):
		collator = self.conf.getOrDefault('chain.collatorAddress')
		if collator:
			try:
				si = self.getSubstrateInterface()
				result = si.query(module='MoonbeamOrbiters', storage_function='AccountLookupOverride', params=[collator])
				return result.value
			except StorageFunctionNotFound:
				return "0x0"
		return "0x0"

	def getSeals(self, block):
		seals = Bash("grep -Eo 'Pre-sealed block for proposal at {}. Hash now 0x[0-9a-fA-F]+' /var/log/syslog | rev | cut -d ' ' -f1 | rev".format(block)).value().split("\n")
		return seals

	def checkAuthoredBlock(self, block):
		bh = self.rpcCall('chain_getBlockHash', [block])
		seals = self.getSeals(block)
		for b in seals:
			if b == bh:
				return self.conf.getOrDefault('chain.collatorAddress')
		return "0x0"
