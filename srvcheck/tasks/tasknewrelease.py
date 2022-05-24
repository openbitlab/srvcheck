from ..notification import Emoji
from . import Task, minutes, hours
import re

class TaskNewRelease(Task):
	def __init__(self, confSet, notification, system, chain):
		super().__init__('TaskNewRelease', confSet, notification, system, chain, minutes(15), hours(2))

	def isPluggable(confSet):
		return True

	def run(self):
		current = self.chain.getLocalVersion()
		latest = self.chain.getLatestVersion()
		c_ver = re.findall(r'(\d+[.]\d+[.]\d+)', current)[0]
		l_ver = re.findall(r'(\d+[.]\d+[.]\d+)', latest)[0]

		if c_ver != l_ver:
			return self.notify('has new release: %s %s' % (latest, Emoji.Rel))

		return False