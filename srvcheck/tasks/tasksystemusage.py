from . import Task, hours

class TaskSystemUsage(Task):
	def __init__(self, confSet, notification, system, chain):
		super().__init__('TaskSystemUsage', confSet, notification, system, chain, hours(24), hours(24))

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()
		serviceUptime = self.system.getServiceUptime()
		self.notify(str(usage) + '\n\tService uptime: ' + str(serviceUptime))
		return False