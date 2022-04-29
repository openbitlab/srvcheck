from . import Task 

class TaskSystemUsage(Task):
	def __init__(self, notification, system, chain):
		super().__init__('TaskSystemUsage', notification, system, chain, 60*24, 60*24)

	def run(self):
		usage = self.system.getUsage()
		self.notify(usage)
		self.markChecked()