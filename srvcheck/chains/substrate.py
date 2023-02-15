from substrateinterface import SubstrateInterface
from srvcheck.tasks.task import hours, minutes
from .chain import Chain
from ..tasks import Task
from ..notification import Emoji
from ..utils import ConfItem, ConfSet, Bash, savePlots, PlotsConf, SubPlotConf

ConfSet.addItem(ConfItem('chain.validatorAddress', description='Validator address'))

class TaskSubstrateNewReferenda(Task):
	def __init__(self, services, checkEvery=hours(1), notifyEvery=60*10*60):
		super().__init__('TaskSubstrateNewReferenda',
			  services, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		n = self.s.chain.getNetwork()
		if n not in ['Kusama', 'Polkadot']:
			return False

		si = self.s.chain.getSubstrateInterface()
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
	def __init__(self, services, checkEvery=30, notifyEvery=60*5):
		super().__init__('TaskRelayChainStuck',
			  services, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(services):
		return services.chain.isParachain()

	def run(self):
		if self.prev is None:
			self.prev = self.s.chain.getRelayHeight()
		elif self.prev == self.s.chain.getRelayHeight():
			return self.notify(f'relay is stuck at block {self.prev} {Emoji.Stuck}')
		return False

class TaskBlockProductionReport(Task):
	def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(1)):
		super().__init__('TaskBlockProductionReport',
			  services, checkEvery, notifyEvery)
		self.prev = None
		self.lastBlockChecked = None
		self.totalBlockChecked = 0
		self.oc = 0

	@staticmethod
	def isPluggable(services):
		return not services.chain.isParachain()

	def run(self):
		era = self.s.chain.getEra()
		if self.prev is None:
			self.prev = era

		if self.s.chain.isStaking():
			currentBlock = self.s.chain.getHeight()
			blocksToCheck = [b for b in self.s.chain.getExpectedBlocks() if b <= currentBlock and (self.lastBlockChecked is None or b > self.lastBlockChecked)]
			for b in blocksToCheck:
				a = self.s.chain.getBlockAuthor(b)
				collator = self.s.conf.getOrDefault('chain.validatorAddress')
				if a.lower() == collator.lower():
					self.oc += 1
				self.lastBlockChecked = b
				self.totalBlockChecked += 1

		if self.prev != era:
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_sessionBlocksProduced', self.prev)
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksChecked', self.totalBlockChecked)
			self.prev = era
			perc = 0
			if self.totalBlockChecked > 0:
				perc = self.oc / self.totalBlockChecked * 100
				self.totalBlockChecked = 0
				self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksProduced', self.oc)
				self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksPercentageProduced', perc)
				self.oc = 0
		return False

class TaskBlockProductionReportParachain(Task):
	def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(1)):
		super().__init__('TaskBlockProductionReportParachain',
                    services, checkEvery, notifyEvery)
		self.prev = None
		self.prevBlock = None
		self.lastBlockChecked = None
		self.totalBlockChecked = 0
		self.oc = 0

	@staticmethod
	def isPluggable(services):
		return services.chain.isParachain()

	def run(self):
		session = self.s.chain.getSessionWrapped()
        
		if self.prev is None:
			self.prev = session

		if self.s.chain.isCollating():
			startingRoundBlock = self.s.chain.getStartingRoundBlock()
			currentBlock = self.s.chain.getHeight()
			blocksToCheck = [b for b in self.s.chain.getExpectedBlocks() if b <= currentBlock and (self.lastBlockChecked is None or b > self.lastBlockChecked) and b >= startingRoundBlock]
			for b in blocksToCheck:
				a = self.s.chain.getBlockAuthor(b)
				collator = self.s.conf.getOrDefault('chain.validatorAddress')
				if a.lower() == collator.lower():
					self.oc += 1
				self.lastBlockChecked = b
				self.totalBlockChecked += 1

		if self.prev != session:
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_sessionBlocksProduced', self.prev)
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksChecked', self.totalBlockChecked)
			self.prev = session
			perc = 0
			if self.totalBlockChecked > 0:
				perc = self.oc / self.totalBlockChecked * 100
				self.totalBlockChecked = 0
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksProduced', self.oc)
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksPercentageProduced', perc)
			self.oc = 0
		return False

class TaskBlockProductionReportCharts(Task):
	def __init__(self, services, checkEvery=hours(24), notifyEvery=hours(24)):
		super().__init__('TaskBlockProductionReportCharts',
                    services, checkEvery, notifyEvery)

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		pc = PlotsConf()
		pc.title = self.s.conf.getOrDefault('chain.name') + " - Block production"
		
		sp = SubPlotConf()
		sp.data = self.s.persistent.getN(self.s.conf.getOrDefault('chain.name') + '_blocksProduced', 30)
		sp.label = 'Produced'
		sp.data_mod = lambda y: y
		sp.color = 'y'
		
		sp.label2 = 'Produced'
		sp.data2 = self.s.persistent.getN(self.s.conf.getOrDefault('chain.name') + '_blocksChecked', 30)
		sp.data_mod2 = lambda y: y
		sp.color2 = 'r'
		
		sp.share_y = True
		sp.set_bottom_y = True
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.getN(self.s.conf.getOrDefault('chain.name') + '_blocksPercentageProduced', 30)
		sp.label = 'Produced (%)'
		sp.data_mod = lambda y: y
		sp.color = 'b'
		
		sp.set_bottom_y = True
		pc.subplots.append(sp)

		pc.fpath = '/tmp/p.png'

		lastSessions = self.s.persistent.getN(self.s.conf.getOrDefault('chain.name') + '_sessionBlocksProduced', 30)
		if lastSessions and len(lastSessions) >= 3:
			savePlots(pc, 1, 2)
			self.s.notification.sendPhoto('/tmp/p.png')

class Substrate(Chain):
	TYPE = "substrate"
	NAME = ""
	BLOCKTIME = 15
	EP = 'http://localhost:9933/'
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskSubstrateNewReferenda, TaskBlockProductionReport, TaskBlockProductionReportCharts]

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
			return not Substrate(conf).isParachain()
		except:
			return False

	def getVersion(self):
		return self.rpcCall('system_version')

	def getHeight(self):
		return int(self.rpcCall('chain_getHeader', [self.getBlockHash()])['number'], 16)

	def getBlockHash(self):
		return self.rpcCall('chain_getBlockHash')

	def getPeerCount(self):
		return int(self.rpcCall('system_health')['peers'])

	def getNetwork(self):
		return self.rpcCall('system_chain')

	def isStaking(self):
		si = self.getSubstrateInterface()
		collator = self.conf.getOrDefault('chain.validatorAddress')
		era = self.getEra()
		result = si.query(module='Staking', storage_function='ErasStakers', params=[era, collator])
		if result.value["total"] > 0:
			return True

	def isSynching(self):
		c = self.rpcCall('system_syncState')['currentBlock']
		h = self.getHeight()
		return abs(c - h) > 32

	def getRelayHeight(self):
		si = self.getSubstrateInterface()
		result = si.query(module='ParachainSystem', storage_function='ValidationData', params=[])
		return result.value["relay_parent_number"]

	def getParachainId(self):
		si = self.getSubstrateInterface()
		result = si.query(module='ParachainInfo', storage_function='ParachainId', params=[])
		return result.value

	def getNodeName(self):
		return self.rpcCall('system_name')

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

	def getEra(self):
		si = self.getSubstrateInterface()
		result = si.query(module='Staking', storage_function='ActiveEra', params=[])
		return result.value['index']

	def isValidator(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='Session', storage_function='QueuedKeys', params=[])
			for v in result.value:
				if v[0].lower() == f'{collator}'.lower():
					return True
		return False

	def getExpectedBlocks(self, since=60):
		serv = self.conf.getOrDefault('chain.service')
		if serv:
			blocks = Bash(f"journalctl -u {serv} --no-pager --since '{since} min ago' | grep -Eo 'Prepared block for proposing at [0-9]+' | sed 's/[^0-9]'//g").value().split("\n")
			blocks = [int(b) for b in blocks if b != '']
			return blocks
		return []

	def getBlockAuthor(self, block):
		return self.checkAuthoredBlock(block)

	def getSeals(self, block):
		seals = Bash("grep -Eo 'block for proposal at {}. Hash now 0x[0-9a-fA-F]+' /var/log/syslog | rev | cut -d ' ' -f1 | rev".format(block)).value().split("\n")
		return seals

	def checkAuthoredBlock(self, block):
		bh = self.rpcCall('chain_getBlockHash', [block])
		seals = self.getSeals(block)
		for b in seals:
			if b == bh:
				return self.conf.getOrDefault('chain.validatorAddress')
		return "0x0"

	def getSessionWrapped(self):
		return self.getSession()