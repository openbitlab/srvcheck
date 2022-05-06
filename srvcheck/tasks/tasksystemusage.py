from . import Task 

class TaskSystemUsage(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemUsage', conf, notification, system, chain, 60*24, 60*24)

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()
		self.notify(usage)
		return False