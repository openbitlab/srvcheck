import subprocess
import apt

from ..notification import Emoji
from . import Task, hours



class TaskAPT(Task):
	def __init__(self, services):
		super().__init__('TaskAPT', services, hours(12), hours(24))

	@staticmethod
	def isPluggable(services):
		try:
			subprocess.check_call(['apt', '--version'])
			return True
		except subprocess.CalledProcessError:
			return False

	def run(self):
		cache = apt.Cache()
		cache.update()
		security_updates = []
		updates = []

		for pkg in cache:
			if pkg.is_upgradable and pkg.is_security_upgrade:
				security_updates.append(pkg.name)
			elif pkg.is_upgradable:
				updates.append(pkg.name)

		if security_updates:
			# Notify
			pass

		return False
