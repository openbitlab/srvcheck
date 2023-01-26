from srvcheck.tasks.task import hours, minutes
from ..tasks import Task
from .substrate import Substrate
from .substrate import TaskRelayChainStuck
from ..notification import Emoji
from ..utils import savePlots, PlotsConf, SubPlotConf

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
		if self.s.persistent.hasPassedNHoursSinceLast(self.name + '_sessionBlocksProduced', 24):
			pc = PlotsConf()
			pc.title = self.s.conf.getOrDefault('chain.name') + " - Block production"
			
			sp = SubPlotConf()
			sp.data = self.s.persistent.getN(self.name + '_blocksProduced', 30)
			sp.label = 'Produced'
			sp.data_mod = lambda y: y
			sp.color = 'r'
            
			sp.label2 = 'Produced'
			sp.data2 = self.s.persistent.getN(self.name + '_blocksChecked', 30)
			sp.data_mod2 = lambda y: y
			sp.color2 = 'b'
            
			sp.share_y = True
			pc.subplots.append(sp)

			sp = SubPlotConf()
			sp.data = self.s.persistent.getN(self.name + '_blocksPercentageProduced', 30)
			sp.label = 'Produced (%)'
			sp.data_mod = lambda y: y
			sp.color = 'b'
			pc.subplots.append(sp)

			pc.fpath = '/tmp/p.png'

			if len(self.s.persistent.getN(self.name + '_sessionBlocksProduced', 30)) >= 2:
				savePlots(pc, 1, 2)
				self.s.notification.sendPhoto('/tmp/p.png')

		session = self.s.chain.getSession()
        
		if self.prev is None:
			self.prev = session

		block = 0
		if self.s.chain.isCollating():
			block = self.s.chain.latestBlockProduced()
			if block == -1:
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
			self.s.persistent.timedAdd(self.name + '_sessionBlocksProduced', self.prev)
			self.s.persistent.timedAdd(self.name + '_blocksChecked', self.totalBlockChecked)
			self.prev = session
			report = f'{self.oc} block produced last session'
			perc = 0
			if self.totalBlockChecked > 0:
				perc = self.oc / self.totalBlockChecked * 100
				report = f'{report} out of {self.totalBlockChecked} ({perc:.2f} %)'
				self.totalBlockChecked = 0
			report = f'{report} {Emoji.BlockProd}'
			self.s.persistent.timedAdd(self.name + '_blocksProduced', self.oc)
			self.s.persistent.timedAdd(self.name + '_blocksPercentageProduced', perc)
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
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskBlockProductionReportParachain]

	def __init__(self, conf):
		super().__init__(conf)

	@staticmethod
	def detect(conf):
		try:
			Amplitude(conf).getVersion()
			return Amplitude(conf).isParachain()
		except:
			return False

	def getSession(self):
		si = self.getSubstrateInterface()
		result = si.query(module='Session', storage_function='CurrentIndex', params=[])
		return result.value

	def isCollating(self):
		collator = self.conf.getOrDefault('chain.validatorAddress')
		if collator:
			si = self.getSubstrateInterface()
			result = si.query(module='ParachainStaking', storage_function='TopCandidates', params=[])
			for c in result.value:
				if c["owner"].lower() == collator.lower():
					return True
		return False
