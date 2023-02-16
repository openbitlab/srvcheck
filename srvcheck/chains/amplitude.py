from .substrate import Substrate
from .substrate import TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts

class Amplitude(Substrate):
	TYPE = "parachain"
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts]

	def __init__(self, conf):
		super().__init__(conf)

	@staticmethod
	def detect(conf):
		try:
			Amplitude(conf).getVersion()
			return Amplitude(conf).isParachain() and Amplitude(conf).getNodeName() == "Pendulum Collator"
		except:
			return False

	def getRoundInfo(self):
		si = self.getSubstrateInterface()
		result = si.query(module='ParachainStaking', storage_function='Round', params=[])
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

	def getStartingRoundBlock(self):
		return self.getRoundInfo()['first']
