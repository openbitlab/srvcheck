from .substrate import Substrate
from .substrate import TaskRelayChainStuck, TaskBlockProductionReportParachain, TaskBlockProductionReportCharts

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

	def getSessionWrapped(self):
		return self.getSession()['current']

	def getStartingRoundBlock(self):
		return self.getSession()['first']
		