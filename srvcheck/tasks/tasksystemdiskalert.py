from . import Task 

class TaskSystemDiskAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemDiskAlert', conf, notification, system, chain, 15, 120)

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if usage.diskPercentageUsed > 90:
			self.notify('Disk usage is above %d%%' % usage['diskPercentageUsed'])
			
		self.markChecked()