from ..notification import Emoji
from . import Task, hours


class TaskAPT(Task):
	def __init__(self, services):
		super().__init__('TaskAPT', services, hours(12), hours(24))

	@staticmethod
	def isPluggable(services):
        # Check if it is a debian based distro
		return True

	def run(self):
        # Apt update

        # Check for security updates

        # Check for other updates

        # Notify / update security

		return False
