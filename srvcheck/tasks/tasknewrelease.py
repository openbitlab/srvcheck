from ..notification import Emoji
from . import Task, minutes, hours

class TaskNewReleaseAlert(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskNewReleaseAlert', conf, notification, system, chain, minutes(15), hours(2))

	def isPluggable(conf):
		return True

	def run(self):
		current = self.chain.getVersion()
		latest = self.chain.getLatestVersion()
		
		if current != latest:
			return self.notify('has new release: %s %s' % (latest, Emoji.Rel))

		return False