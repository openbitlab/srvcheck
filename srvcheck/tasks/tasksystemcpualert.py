from . import Task 

class TaskSystemCpuAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemCpuAlert', conf, notification, system, chain, 15, 120)

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if usage.cpu > 90:
			self.notify('CPU usage is above %d%%' % usage['cpu'])

		self.markChecked()