from ..notification import Emoji
from . import Task, minutes

class TaskChainSynching(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainSynching', conf, notification, system, chain, minutes(1), minutes(30))
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		if self.chain.isSynching():
			return self.notify(f'chain is synching {Emoji.Slow}')

		return False
