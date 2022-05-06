from . import Task 

class TaskChainStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainStuck', conf, notification, system, chain, chain.BLOCKTIME * 2, 5)
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		bh = self.chain.getBlockHash()

		if self.prev == None:
			self.prev = bh
			self.markChecked()
			return 

		if bh == self.prev:
			self.notify('Chain is stuck at block %s' % bh)
		
		self.markChecked()