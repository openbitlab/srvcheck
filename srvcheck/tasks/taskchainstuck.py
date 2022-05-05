from . import Task 

class TaskChainStuck(Task):
	def __init__(self, notification, system, chain):
		super().__init__('TaskChainStuck', notification, system, chain, chain.BLOCKTIME * 2, 5)
		self.prev = None

	def run(self):
		bh = self.chain.getBlockHash()

		if self.prev == None:
			self.prev = bh
			self.markChecked()
			return 

		if bh == self.prev:
			self.notify('Chain is stuck at block %s' % bh)
		
		self.markChecked()