from . import Task, minutes, hours

class TaskChainUnreachable(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskChainUnreachable', conf, notification, system, chain, minutes(15), hours(1))

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		try:
			self.chain.getHeight()
		except Exception:
			self.notify('chain is not reachable')
