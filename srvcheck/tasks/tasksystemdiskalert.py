from ..notification import Emoji
from ..utils import toGB, Bash, ConfItem, ConfSet
from . import Task, minutes, hours

ConfSet.addItem(ConfItem('system.log_size_threshold', 4, int, 'threshold for log size in GB'))
ConfSet.addItem(ConfItem('system.disk_limit', 90, int, 'threshold for disk usage in %'))

class TaskSystemDiskAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemDiskAlert', conf, notification, system, chain, minutes(15), hours(2))
		self.prevDiskSize = None

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if self.prevDiskSize is None:
			self.prevDiskSize = usage.diskSize

		dl = self.conf.getOrDefault('system.disk_limit')
		if usage.diskPercentageUsed > dl:
			return self.notify('disk usage is above %d%% (%d%%) (/var/log: %.1fG, /: %.1fG) %s' % 
				(dl, usage.diskPercentageUsed, toGB(usage.diskUsedByLog), toGB(usage.diskUsed), Emoji.Disk))

		if usage.diskSize > self.prevDiskSize:
			c = self.notify('disk size increased (%.1fG -> %.1fG) %s' % 
				(toGB(self.prevDiskSize), toGB(usage.diskSize), Emoji.Disk), True)
			self.prevDiskSize = usage.diskSize
			return c

		return False

	def canRecover(self):
		return toGB(self.system.getUsage().diskUsedByLog) > self.conf.getOrDefault('system.log_size_threshold')

	def recover(self):
		Bash('truncate -s 0 /var/log/syslog')
		Bash('rm /var/log/syslog.*')
		Bash('rm -r /var/log/journal/*')
