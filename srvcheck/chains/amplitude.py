from srvcheck.tasks.task import hours, minutes
from ..tasks import Task
from .substrate import Substrate
from .substrate import TaskRelayChainStuck, TaskBlockProductionReportCharts
from ..notification import Emoji

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

		if self.s.chain.isCollating():
			startingRoundBlock = session
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
			else:
				return self.notify(f'will not validate during the session {session + 1} {Emoji.NoLeader}\n{report}')
		return False

class Amplitude(Substrate):
	TYPE = "parachain"
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts]

	def __init__(self, conf):
		super().__init__(conf)

	@staticmethod
	def detect(conf):
		try:
			Amplitude(conf).getVersion()
			return Amplitude(conf).isParachain() and int(Amplitude(conf).getParachainId()) == int(conf.getOrDefault('chain.parachainId'))
		except:
			return False

	def isCollating(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='ParachainStaking', storage_function='TopCandidates', params=[])
			for c in result.value:
				if c["owner"].lower() == collator.lower():
					return True
		return False
