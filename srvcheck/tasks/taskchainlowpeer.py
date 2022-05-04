from . import Task 

MIN_PEERS = 2

class TaskChainLowPeer(Task):
	def __init__(self, notification, system, chain):
		super().__init__('TaskChainLowPeer', notification, system, chain, self.chain.BLOCK_TIME * 2, 5)

	def run(self):
		p = self.chain.getPeerNumber()

		if p < MIN_PEERS:
			self.notify('Chain has only %d peers' % p)
		
		self.markChecked()