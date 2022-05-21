from ..notification import Emoji
from ..utils import toGB, Bash
from . import Task, minutes, hours

LOG_SIZE_THRESHOLD = 4 #GB
DISK_LIMIT = 90

class TaskSystemDiskAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemDiskAlert', conf, notification, system, chain, minutes(15), hours(2))
		self.prevDiskSize = None

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if self.prevDiskSize is None:
			self.prevDiskSize = usage.diskSize

		if usage.diskPercentageUsed > DISK_LIMIT:
			return self.notify('Disk usage is above %d%% (%d%%) (/var/log: %.1fG) %s' % (DISK_LIMIT, usage.diskPercentageUsed, toGB(usage.diskUsedByLog), Emoji.Disk))

		if usage.diskSize > self.prevDiskSize:
			c = self.notify('Disk size increased (%.1fG -> %.1fG) %s' % (toGB(self.prevDiskSize), toGB(usage.diskSize), Emoji.Disk), True)
			self.prevDiskSize = usage.diskSize
			return c
			
		return False

	def canRecover(self):
		return toGB(self.system.getUsage().diskUsedByLog) > LOG_SIZE_THRESHOLD

	def recover(self):
		Bash('truncate -s 0 /var/log/syslog')
		Bash('rm /var/log/syslog.*')
		Bash('rm -r /var/log/journal/*')
