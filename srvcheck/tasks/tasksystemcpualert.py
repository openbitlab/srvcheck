from ..notification import Emoji
from . import Task, minutes, hours

CPU_LIMIT = 90

class TaskSystemCpuAlert(Task):
	def __init__(self, services):
		super().__init__('TaskSystemCpuAlert', services, minutes(15), hours(2))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		usage = self.s.system.getUsage()

		if usage.cpuUsage > CPU_LIMIT:
			return self.notify('CPU usage is above %d%% (%d%%) %s' % (CPU_LIMIT, usage.cpuUsage, Emoji.Cpu))

		return False
