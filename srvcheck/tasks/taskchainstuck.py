import time
from ..notification import Emoji
from . import Task, minutes

class TaskChainStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainStuck', conf, notification, system, chain, chain.BLOCKTIME * 2, minutes(5))
		self.prev = None
		self.since = None
		self.oc = 0

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
			self.since = time.time()
			return False

		if bh == self.prev:
			self.oc += 1
			elapsed = (time.time() - self.since)
			if (elapsed / 60) >= 1:
				elapsed = str(int(elapsed / 60)) + ' minutes'
			else:
				elapsed = str(int(elapsed)) + ' seconds'
			return self.notify(f'chain is stuck at block {bh} since {elapsed} ({self.oc}) {Emoji.Stuck}')

		self.prev = bh
		self.since = time.time()
		self.oc = 0
		return False
