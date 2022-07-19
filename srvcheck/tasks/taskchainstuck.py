import time
from ..notification import Emoji
from . import Task, minutes

def elapsedToString(since):
	elapsed = (time.time() - since)
	if (elapsed / 60) > 60:
		elapsed = str(int(elapsed / 60 / 60)) + ' hours and ' + str(int(elapsed / 60 % 60)) + ' minutes'
	elif (elapsed / 60) >= 1:
		elapsed = str(int(elapsed / 60)) + ' minutes'
	else:
		elapsed = str(int(elapsed)) + ' seconds'
	return elapsed

class TaskChainStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainStuck', conf, notification, system, chain, chain.BLOCKTIME * 2, chain.BLOCKTIME * 2)
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
			elapsed = elapsedToString(self.since)
			return self.notify(f'chain is stuck at block {bh} since {elapsed} ({self.oc}) {Emoji.Stuck}')

		if self.oc > 0:
			elapsed = elapsedToString(self.since)
			prevOc = self.oc
			self.oc = 0
			self.prev = bh
			return self.notify(f'chain come back in sync after {elapsed} ({prevOc}) {Emoji.SyncOk}')

		self.prev = bh
		self.since = time.time()
		self.oc = 0
		return False