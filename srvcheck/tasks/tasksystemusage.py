from . import Task, hours
from ..utils import savePlots, PlotsConf, SubPlotConf, toGB, toPrettySize

class TaskSystemUsage(Task):
	def __init__(self, services):
		super().__init__('TaskSystemUsage', services, hours(24), hours(24))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		usage = self.s.system.getUsage()

		# Burnrate estimation 
		rate = self.s.persistent.getAveragedDiff('TaskSystemUsage_diskUsed', 7)
		if rate:
			days = (usage.diskSize - usage.diskUsed) / rate
			sv = '\n\tDisk burnrate: %.1f days left (%s/day rate)' % (days, toPrettySize(rate))
			out = str(usage) + sv
		else:
			out = str(usage)

		serviceUptime = self.s.system.getServiceUptime()
		self.notify(out + '\n\tService uptime: ' + str(serviceUptime))

		# Saving historical data
		if self.s.persistent.hasPassedNHoursSinceLast(self.name + '_ramSize', 23):
			self.s.persistent.timedAdd(self.name + '_diskUsed', usage.diskUsed)
			self.s.persistent.timedAdd(self.name + '_diskPercentageUsed', usage.diskPercentageUsed)
			self.s.persistent.timedAdd(self.name + '_diskUsedByLog', usage.diskUsedByLog)
			self.s.persistent.timedAdd(self.name + '_ramUsed', usage.ramUsed)
			self.s.persistent.timedAdd(self.name + '_ramSize', usage.ramSize)

		# Sending a chart
		pc = PlotsConf()
		pc.title = self.s.conf.getOrDefault('chain.name') + " - System usage"

		sp = SubPlotConf()
		# sp.name = self.s.conf.getOrDefault('chain.name') + " - Disk"
		sp.data = self.s.persistent.getN(self.name + '_diskUsed', 30)
		sp.label = 'Used (GB)'
		sp.data_mod = lambda y: toGB(y)
		sp.color = 'b'

		# sp.data2 = data['TaskSystemUsage_diskPercentageUsed'][-14::]
		# sp.label2 = 'Used (%)'
		# sp.data_mod2 = lambda y: y
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.getN(self.name + '_diskPercentageUsed', 30)
		sp.label = 'Used (%)'
		sp.data_mod = lambda y: y
		sp.color = 'r'
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.getN(self.name + '_diskUsedByLog', 30)
		sp.label = 'Used by log (GB)'
		sp.data_mod = lambda y: toGB(y)
		sp.color = 'g'
		pc.subplots.append(sp)

		sp = SubPlotConf()
		sp.data = self.s.persistent.getN(self.name + '_ramUsed', 30)
		sp.label = 'Ram used (GB)'
		sp.data_mod = lambda y: toGB(y)
		sp.color = 'y'

		sp.label2 = 'Ram size (GB)'
		sp.data2 = self.s.persistent.getN(self.name + '_ramSize', 30)
		sp.data_mod2 = lambda y: toGB(y)
		sp.color2 = 'r'

		sp.share_y = True

		pc.subplots.append(sp)

		pc.fpath = '/tmp/t.png'

		if len(self.s.persistent.getN(self.name + '_diskPercentageUsed', 30)) >= 2:
			savePlots(pc, 2, 2)
			self.s.notification.sendPhoto('/tmp/t.png')

		return False
