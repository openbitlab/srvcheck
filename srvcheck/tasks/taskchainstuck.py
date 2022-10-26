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
	def __init__(self, services):
		super().__init__('TaskChainStuck', services, minutes(5), minutes(5))
		self.prev = None
		self.since = None
		self.oc = 0

		try:
			self.s.chain.getBlockHash()
			self.method = self.s.chain.getBlockHash
		except:
			self.method = self.s.chain.getHeight

	@staticmethod
	def isPluggable(services):
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


		if self.oc > 1:
			elapsed = elapsedToString(self.since)
			self.notify (f'chain come back in sync after {elapsed} ({self.oc}) {Emoji.SyncOk}')

		self.prev = bh
		self.since = time.time()
		self.oc = 0
		return False