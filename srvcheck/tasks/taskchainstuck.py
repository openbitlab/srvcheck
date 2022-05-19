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


	def isPluggable(conf):
		return True

	def run(self):
		bh = self.method()

		if self.prev == None:
			self.prev = bh
			return False 

		if bh == self.prev or self.chain.isSynching():
			return self.notify('Chain is stuck at block %s %s' % (str(bh), Emoji.Stuck))
		
		self.prev = bh
		return False