from . import Task 

class TaskSystemUsageAlert(Task):
	def __init__(self, notification, system, chain):
		super().__init__('TaskSystemUsage', notification, system, chain, 15, 120)

	def run(self):
		usage = self.system.getUsage()

		if usage.cpu > 90:
			self.notify('CPU usage is above %d%%' % usage['cpu'])

		if usage.diskPercentageUsed > 90:
			self.notify('Disk usage is above %d%%' % usage['diskPercentageUsed'])
			
		self.markChecked()