from .chain import Chain, rpcCall
from ..tasks import Task

THRESHOLD_NOTSIGNED = 5 

class TaskTendermintBlockMissed(Task):
	def __init__(self, notification, chain, checkEvery = 60, notifyEvery = 60*10):
		super().__init__('TaskTendermintBlockMissed', notification, chain, checkEvery, notifyEvery)
		self.prev = None 

	def run(self):
		nblockh = self.getHeight()

		if not self.prev:
			self.prev = nblockh
			self.markChecked()

		# TODO: checks 
		
		self.markChecked()

class TaskTendermintPositionChanged(Task):
	def __init__(self, notification, chain, checkEvery = 60, notifyEvery = 60*10):
		super().__init__('TaskTendermintPositionChanged', notification, chain, checkEvery, notifyEvery)
		self.prev = None 

	def run(self):
		npos = self.getValidatorPosition()

		if not self.prev:
			self.prev = npos
			self.markChecked()

		if npos != self.prev:
			if npos > self.prev:
				self.notify('Position increased from %d to %d' % (self.prev, npos))
			else:
				self.notify('Position decreased from %d to %d' % (self.prev, npos))
		
		self.markChecked()

class TaskTendermintHealthError(Task):
	def __init__(self, notification, chain, checkEvery = 60, notifyEvery = 60*10):
		super().__init__('TaskTendermintHealthError', notification, chain, checkEvery, notifyEvery)
		self.prev = None 

	def run(self):
		errors = self.chain.getHealth()['errors']

		if errors != None:
			self.notify('Health error: %s' % str(errors))
		
		self.markChecked()


class Tendermint (Chain):
	NAME = "tendermint"
	BLOCKTIME = 60 

	def __init__(self, conf):
		super().__init__(conf)
		self.TASKS += TaskTendermintBlockMissed 
		self.TASKS += TaskTendermintHealthError 
		self.TASKS += TaskTendermintPositionChanged 

	def detect(conf):
		try:
			Tendermint(conf).getVersion()
			return True
		except:
			return False

	def getHealth(self):
		return rpcCall(self.EP, 'health')

	def getLatestVersion(self):
		raise Exception('Abstract getLatestVersion()')

	def getVersion(self):
		raise Exception('Abstract getVersion()')

	def getHeight(self):
		return rpcCall(self.EP, 'status')['sync_info']['latest_block_height']
		
	def getBlockHash(self):
		raise Exception('Abstract getHeight()')

	def getPeerNumber(self):
		return rpcCall(self.EP, 'status')['net_info']['n_peers']

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		raise Exception('Abstract isStaking()')
