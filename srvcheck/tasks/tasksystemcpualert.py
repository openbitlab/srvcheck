from . import Task, minutes, hours

class TaskSystemCpuAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskSystemCpuAlert', conf, notification, system, chain, minutes(15), hours(2))

	def isPluggable(conf):
		return True

	def run(self):
		usage = self.system.getUsage()

		if usage.cpuUsage > 90:
			return self.notify('CPU usage is above %d%%' % usage.cpu, self.notification.CPU_EMOJI)

		return False