from ..notification import Emoji
from . import Task, minutes, hours

CPU_LIMIT = 90

class TaskSystemCpuAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemCpuAlert', conf, notification, system, chain, minutes(15), hours(2))

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if usage.cpuUsage > CPU_LIMIT:
			return self.notify('CPU usage is above %d%% (%d%%) %s' % (CPU_LIMIT, usage.cpuUsage, Emoji.Cpu))

		return False
