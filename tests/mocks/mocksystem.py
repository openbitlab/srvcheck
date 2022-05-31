from srvcheck.utils.system import SystemUsage

class MockSystem:
	def __init__(self, conf):
		self.conf = conf
		self.usage = SystemUsage()

	def getServiceUptime(self):
		return 'na'

	def getUsage(self):
		return self.usage
		