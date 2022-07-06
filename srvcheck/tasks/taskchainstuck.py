from ..notification import Emoji
from . import Task, minutes

class TaskChainStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainStuck', conf, notification, system, chain, chain.BLOCKTIME * 2, minutes(5))
		self.prev = None

		try:
			self.chain.getBlockHash()
			self.method = self.chain.getBlockHash
		except:
			self.method = self.chain.getHeight

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		bh = self.method()

		if self.prev is None:
			self.prev = bh
			return False

		if bh == self.prev:
			return self.notify(f'chain is stuck at block {bh} {Emoji.Stuck}')

		self.prev = bh
		return False
