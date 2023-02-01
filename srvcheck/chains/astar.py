from srvcheck.tasks.task import hours, minutes
from ..tasks import Task
from .substrate import Substrate
from .substrate import TaskRelayChainStuck, TaskBlockProductionReportCharts
from ..notification import Emoji

class TaskBlockProductionCheck(Task):
	def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
		super().__init__('TaskBlockProductionCheck',
			  services, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(services):
		return services.chain.isParachain()

	def run(self):
		if self.s.chain.isCollating():
			block = self.s.chain.latestBlockProduced()
			if block > 0:
				if self.prev is None:
					self.prev = block
				elif self.prev == block:
					return self.notify(f'no block produced in the latest 30 minutes! Last block produced was {self.prev} {Emoji.BlockMiss}')
				self.prev = block
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
		session = self.s.chain.getSession()
        
		if self.prev is None:
			self.prev = session

		block = 0
		if self.s.chain.isCollating():
			block = self.s.chain.latestBlockProduced()
			if block > 0:
				if self.prevBlock is None:
					self.prevBlock = block
					self.oc += 1

				if block != self.prevBlock:
					self.oc += 1

				self.prevBlock = block

		if self.prev != session:
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_sessionBlocksProduced', self.prev)
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksChecked', self.totalBlockChecked)
			self.prev = session
			report = f'{self.oc} block produced last session'
			perc = 0
			if self.totalBlockChecked > 0:
				perc = self.oc / self.totalBlockChecked * 100
				report = f'{report} out of {self.totalBlockChecked} ({perc:.2f} %)'
				self.totalBlockChecked = 0
			report = f'{report} {Emoji.BlockProd}'
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksProduced', self.oc)
			self.s.persistent.timedAdd(self.s.conf.getOrDefault('chain.name') + '_blocksPercentageProduced', perc)
			self.oc = 0
			if self.s.chain.isValidator():
				return self.notify(f'will validate during the session {session + 1} {Emoji.Leader}\n{report}')
			elif block != -1:
				return self.notify(f'will not validate during the session {session + 1} {Emoji.NoLeader}\n{report}')
			else:
				return self.notify(report)
		return False

class Amplitude(Substrate):
	TYPE = "parachain"
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts, TaskBlockProductionCheck]

	def __init__(self, conf):
		super().__init__(conf)

	@staticmethod
	def detect(conf):
		try:
			Amplitude(conf).getVersion()
			return Amplitude(conf).isParachain() and Amplitude(conf).getParachainId() == conf.getOrDefault('chain.parachainId')
		except:
			return False

	def isCollating(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='CollatorSelection', storage_function='Candidates', params=[])
			for c in result.value:
				if c['who'].lower() == f'{collator}'.lower():
					return True
			result = si.query(module='CollatorSelection', storage_function='Invulnerables', params=[])
			for c in result.value:
				if c.lower() == f'{collator}'.lower():
					return True
		return False

	def latestBlockProduced(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='CollatorSelection', storage_function='LastAuthoredBlock', params=[collator])
			return result.value
		return 0

	def getBlockAuthor(self, block):
		return self.rpcCall('eth_getBlockByNumber', [hex(block), True])['author']