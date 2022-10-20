from . import Task, hours
from ..utils import savePlot, savePlots, PlotConf, PlotsConf, SubPlotConf, toGB

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

		if self.s.persistent.hasPassedNHoursSinceLast(self.name + '_ramSize', 23):
			self.s.persistent.timedAdd(self.name + '_diskUsed', usage.diskUsed)
			self.s.persistent.timedAdd(self.name + '_diskPercentageUsed', usage.diskPercentageUsed)
			self.s.persistent.timedAdd(self.name + '_diskUsedByLog', usage.diskUsedByLog)
			self.s.persistent.timedAdd(self.name + '_ramUsed', usage.ramUsed)
			self.s.persistent.timedAdd(self.name + '_ramSize', usage.ramSize)


		# savePlot("Disk Percentage Used", self.s.persistent.get(self.name + '_' + 'diskPercentageUsed'), '%% used', '/tmp/t.png')
		# self.s.notification.sendPhoto('/tmp/t.png')

		# pc = PlotConf ()
		# pc.name = self.s.conf.getOrDefault('chain.name') + " - Disk"
		# pc.data = self.s.persistent.get(self.name + '_diskUsed')
		# pc.label = 'Used (GB)'
		# pc.data_mod = lambda y: y/1024/1024


		# pc.data2 = self.s.persistent.get(self.name + '_diskPercentageUsed')
		# pc.label2 = 'Used (%)'
		# pc.data_mod2 = lambda y: y

		# pc.fpath = '/tmp/t.png'

		# savePlot(pc)
		# self.s.notification.sendPhoto('/tmp/t.png')


		pc = PlotsConf ()
		pc.title = self.s.conf.getOrDefault('chain.name') + " - System usage"

		sp = SubPlotConf()
		# sp.name = self.s.conf.getOrDefault('chain.name') + " - Disk"
		sp.data = self.s.persistent.get(self.name + '_diskUsed')
		sp.label = 'Used (GB)'
		sp.data_mod = lambda y: toGB(y)
		sp.color = 'b'

		# sp.data2 = data['TaskSystemUsage_diskPercentageUsed'][-14::]
		# sp.label2 = 'Used (%)'
		# sp.data_mod2 = lambda y: y
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.get(self.name + '_diskPercentageUsed')
		sp.label = 'Used (%)'
		sp.data_mod = lambda y: y
		sp.color = 'r'
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.get(self.name + '_diskUsedByLog')
		sp.label = 'Used by log (GB)'
		sp.data_mod = lambda y: toGB(y)
		sp.color = 'g'
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.get(self.name + '_ramUsed')
		sp.label = 'Ram used (GB)'
		sp.data_mod = lambda y: toGB(y)
		sp.color = 'y'

		sp.label2 = 'Ram size (GB)'
		sp.data2 = self.s.persistent.get(self.name + '_ramSize')
		sp.data_mod2 = lambda y: toGB(y)
		sp.color2 = 'r'

		sp.share_y = True 
		
		pc.subplots.append(sp)

		pc.fpath = '/tmp/t.png'

		if len(self.s.persistent.get(self.name + '_diskPercentageUsed')) >= 2:
			savePlots(pc, 2, 2)
			self.s.notification.sendPhoto('/tmp/t.png')

		return False
