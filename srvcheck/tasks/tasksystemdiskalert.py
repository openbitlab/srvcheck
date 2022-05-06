from ..utils import toGB, Bash
from . import Task, minutes, hours

LOG_SIZE_THRESHOLD = 4 #GB

class TaskSystemDiskAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemDiskAlert', conf, notification, system, chain, minutes(15), hours(2))

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if usage.diskPercentageUsed > 90:
			return self.notify('Disk usage is above %d%% (/var/log: %.1fG)' % (usage.diskPercentageUsed, toGB(usage.diskUsedByLog)))
			
		return False

	def canRecover(self):
		return toGB(self.system.getUsage().diskUsedByLog) > LOG_SIZE_THRESHOLD

	def recover(self):
		Bash('truncate -s 0 /var/log/syslog')
		Bash('rm /var/log/syslog.*')
		Bash('rm -r /var/log/journal/*')
