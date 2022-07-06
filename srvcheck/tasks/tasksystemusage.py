from . import Task, hours

class TaskSystemUsage(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemUsage', conf, notification, system, chain, hours(24), hours(24))

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		usage = self.system.getUsage()
		serviceUptime = self.system.getServiceUptime()
		self.notify(str(usage) + '\n\tService uptime: ' + str(serviceUptime))
		return False
