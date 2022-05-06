from . import Task, minutes

class TaskChainStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainStuck', conf, notification, system, chain, chain.BLOCKTIME * 2, minutes(5))
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		bh = self.chain.getBlockHash()

		if self.prev == None:
			self.prev = bh
			return False 

		if bh == self.prev:
			return self.notify('Chain is stuck at block %s' % bh)
		
		return False