from . import Task, hours

class TaskSystemUsage(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemUsage', conf, notification, system, chain, hours(24), hours(24))

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()
		self.notify(str(usage))
		return False