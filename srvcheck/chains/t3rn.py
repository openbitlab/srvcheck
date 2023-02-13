from .substrate import Substrate
from .substrate import TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts

class T3rn(Substrate):
	TYPE = "parachain"
	CUSTOM_TASKS = [TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts]

	def __init__(self, conf):
		super().__init__(conf)

	@staticmethod
	def detect(conf):
		try:
			T3rn(conf).getVersion()
			return T3rn(conf).isParachain() and T3rn(conf).getNodeName() == "Circuit Collator"
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

	def getStartingRoundBlock(self):
		return -1
