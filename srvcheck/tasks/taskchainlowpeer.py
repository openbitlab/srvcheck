from ..notification import Emoji
from . import Task, minutes

MIN_PEERS = 3

class TaskChainLowPeer(Task):
	def __init__(self, services):
		super().__init__('TaskChainLowPeer', services, services.chain.BLOCKTIME * 2, minutes(5))

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		p = self.s.chain.getPeerCount()

		if p < MIN_PEERS:
			return self.notify(f'chain has only {p} peers {Emoji.Peers}')

		return False
