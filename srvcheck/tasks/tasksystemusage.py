from . import Task, hours

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

		for x in ['diskUsed', 'diskPercentageUsed', 'diskUsedByLog', 'ramUsed']:
			if self.s.persistent.hasPassedNHoursSinceLast(self.name + '_' + x, 23):
				self.s.persistent.timedAdd(self.name + '_' + x, usage[x])

		return False
