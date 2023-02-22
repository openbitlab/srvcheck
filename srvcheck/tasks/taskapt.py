import subprocess

from ..notification import Emoji
from . import Task, hours

def indexOf(a, v):
	try:
		return a.index(v)
	except ValueError:
		return -1


class TaskAPT(Task):
	def __init__(self, services):
		super().__init__('TaskAPT', services, hours(12), hours(24))

	@staticmethod
	def isPluggable(services):
		try:
			import apt
			subprocess.check_call(['apt', '--version'])
			return True
		except subprocess.CalledProcessError:
			return False

	def run(self):
		import apt 

		cache = apt.Cache()
		cache.update()
		security_updates = []
		updates = []

		for pkg in cache:
			if not pkg.is_installed:
				continue
			if pkg.is_upgradable and indexOf(pkg.candidate.uri, 'security') != -1:
				security_updates.append(pkg.name)
			elif pkg.is_upgradable:
				updates.append(pkg.name)

		if security_updates:
			return self.notify(f'has {len(security_updates)} security updates pending ({len(updates)+len(security_updates)} pending updates total): {", ".join(security_updates)} {Emoji.Floppy}')

		return False
