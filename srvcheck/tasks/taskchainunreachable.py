from ..notification import Emoji
from . import Task, minutes, hours

class TaskChainUnreachable(Task):
	def __init__(self, services):
		super().__init__('TaskChainUnreachable', services, minutes(15), hours(1))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		try:
			self.s.chain.getHeight()
		except Exception:
			self.notify(f'chain is not reachable {Emoji.Unreachable}')
