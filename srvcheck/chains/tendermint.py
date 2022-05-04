from .chain import Chain, rpcCall
from ..tasks import Task
import requests

THRESHOLD_NOTSIGNED = 5 

class TendermintBlockMissedTask(Task):
	def __init__(self, notification, chain, checkEvery = 60, notifyEvery = 60*10):
		super().__init__('TendermintBlockMissed', notification, chain, checkEvery, notifyEvery)
		self.prev = None 

	def run(self):
		nblockh = self.getHeight()

		if not self.prev:
			self.prev = nblockh
			self.markChecked()

		# TODO: checks 
		
		self.markChecked()


class TendermintPositionChangedTask(Task):
	def __init__(self, notification, chain, checkEvery = 60, notifyEvery = 60*10):
		super().__init__('TendermintPositionChanged', notification, chain, checkEvery, notifyEvery)
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


class Tendermint (Chain):
	NAME = "tendermint"
	BLOCKTIME = 60 

	def __init__(self, conf):
		super().__init__(conf)
		self.TASKS += TendermintBlockMissedTask 
		self.TASKS += TendermintPositionChangedTask 

	def detect(conf):
		try:
			Tendermint(conf).getVersion()
			return True
		except:
			return False

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
