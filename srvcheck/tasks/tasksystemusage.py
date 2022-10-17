from . import Task, hours
from ..utils import savePlot

class TaskSystemUsage(Task):
	def __init__(self, services):
		super().__init__('TaskSystemUsage', services, hours(24), hours(24))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		usage = self.s.system.getUsage()
		serviceUptime = self.s.system.getServiceUptime()
		self.notify(str(usage) + '\n\tService uptime: ' + str(serviceUptime))

		if self.s.persistent.hasPassedNHoursSinceLast(self.name + '_diskUsed', 23):
			self.s.persistent.timedAdd(self.name + '_diskUsed', usage.diskUsed)
			self.s.persistent.timedAdd(self.name + '_diskPercentageUsed', usage.diskPercentageUsed)
			self.s.persistent.timedAdd(self.name + '_diskUsedByLog', usage.diskUsedByLog)
			self.s.persistent.timedAdd(self.name + '_ramUsed', usage.ramUsed)


		# savePlot("Disk Percentage Used", self.s.persistent.get(self.name + '_' + 'diskPercentageUsed'), '%% used', '/tmp/t.png')
		# self.s.notification.sendPhoto('/tmp/t.png')

		savePlot("Disk Used", self.s.persistent.get(self.name + '_diskUsed'), 'used (GB)', '/tmp/t.png')
		self.s.notification.sendPhoto('/tmp/t.png')

		return False
