from srvcheck.tasks.task import hours, minutes
from ..tasks import Task
from .substrate import Substrate
from .substrate import TaskRelayChainStuck, TaskBlockProductionReportCharts

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
		s = self.s.chain.getSession()
		session = s['current']
        
		if self.prev is None:
			self.prev = session

		orb = self.s.chain.moonbeamAssignedOrbiter()
		if self.s.chain.isCollating():
			startingRoundBlock = s['first']
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

class Moonbeam(Substrate):
	TYPE = "parachain"
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts]

	def __init__(self, conf):
		super().__init__(conf)

	@staticmethod
	def detect(conf):
		try:
			Moonbeam(conf).getVersion()
			return Moonbeam(conf).isParachain() and Moonbeam(conf).getNodeName() == "Moonbeam Parachain Collator"
		except:
			return False

	def getSession(self):
		si = self.getSubstrateInterface()
		result = si.query(module='ParachainStaking', storage_function='Round', params=[])
		return result.value

	def isValidator(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='ParachainStaking', storage_function='SelectedCandidates', params=[])
			for c in result.value:
				if c.lower() == collator.lower():
					return True
		return False

	def isCollating(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			c = self.moonbeamAssignedOrbiter()
			if c != '0x0' and c is not None:
				collator = c
			result = si.query(module='ParachainStaking', storage_function='SelectedCandidates', params=[])
			for c in result.value:
				if c.lower() == collator.lower():
					return True
		return False

	def moonbeamAssignedOrbiter(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='MoonbeamOrbiters', storage_function='AccountLookupOverride', params=[collator])
			return result.value
		return "0x0"
