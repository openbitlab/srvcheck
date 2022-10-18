from . import Task, hours
from ..utils import savePlot, PlotConf

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

		if self.s.persistent.hasPassedNHoursSinceLast(self.name + '_diskUsed', 2):
			self.s.persistent.timedAdd(self.name + '_diskUsed', usage.diskUsed)
			self.s.persistent.timedAdd(self.name + '_diskPercentageUsed', usage.diskPercentageUsed)
			self.s.persistent.timedAdd(self.name + '_diskUsedByLog', usage.diskUsedByLog)
			self.s.persistent.timedAdd(self.name + '_ramUsed', usage.ramUsed)


		# savePlot("Disk Percentage Used", self.s.persistent.get(self.name + '_' + 'diskPercentageUsed'), '%% used', '/tmp/t.png')
		# self.s.notification.sendPhoto('/tmp/t.png')

		pc = PlotConf ()
		pc.name = self.s.conf.getOrDefault('chain.name') + " - Disk"
		pc.data = self.s.persistent.get(self.name + '_diskUsed')
		pc.label = 'Used (GB)'
		pc.data_mod = lambda y: y/1024/1024


		pc.data2 = self.s.persistent.get(self.name + '_diskPercentageUsed')
		pc.label2 = 'Used (%)'
		pc.data_mod2 = lambda y: y

		pc.fpath = '/tmp/t.png'

		savePlot(pc)
		self.s.notification.sendPhoto('/tmp/t.png')

		return False
