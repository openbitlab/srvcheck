from ..notification import Emoji
from . import Task, minutes, hours

RAM_LIMIT = 85

class TaskSystemRamAlert(Task):
	def __init__(self, services):
		super().__init__('TaskSystemRamAlert', services, minutes(15), hours(2))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		usage = self.s.system.getUsage()
		ramUsed = round(usage.ramUsed/usage.ramSize*100, 1)
		if ramUsed > RAM_LIMIT:
			return self.notify('Ram usage is above %d%% (%d%%) %s' % (RAM_LIMIT, ramUsed, Emoji.Ram))

		return False
