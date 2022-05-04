from .chain import Chain, rpcCall
from ..tasks import Task

THRESHOLD_NOTSIGNED = 5

class TaskTendermintBlockMissed(Task):
	def __init__(self, notification, chain, checkEvery=60, notifyEvery=60*10):
		super().__init__('TaskTendermintBlockMissed',
		      notification, chain, checkEvery, notifyEvery)
		self.prev = None

	def run(self):
		nblockh = self.getHeight()

		if not self.prev:
			self.prev = nblockh
			self.markChecked()

		# TODO: checks

		self.markChecked()


class TaskTendermintPositionChanged(Task):
	def __init__(self, notification, chain, checkEvery=60, notifyEvery=60*10):
		super().__init__('TaskTendermintPositionChanged',
		      notification, chain, checkEvery, notifyEvery)
		self.active_set = self.chain.conf.active_set
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

	def getValidatorPosition(self):
		bh = self.chain.getHeight()
		active_vals = []
		if (self.active_set == ''):
			active_s = int(rpcCall(self.chain.EP, 'validators', [bh, "1", "1"])['total'])
		else:
			active_s = int(self.active_set)
		if (active_s > 100):
			it = active_s // 100
			diff = 0
			for i in range(it):
				active_vals += rpcCall(self.chain.EP, 'validators', [bh, str(i + 1), "100"])['validators']
				diff = active_s - 100
			if (diff > 0):
				active_vals += rpcCall(self.chain.EP, 'validators', [bh, str(i + 2), "100"])['validators']
		else:
			active_vals += rpcCall(self.chain.EP, 'validators', [bh, "1", str(active_s)])['validators']
		p = [i for i, j in enumerate(active_vals) if j['address'] == self.chain.conf.val_address]
		return p[0] + 1 if len(p) > 0 else -1 

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
	EP = "http://localhost:26657/"
	
	def __init__(self, conf):
		super().__init__(conf)
		self.TASKS += TaskTendermintBlockMissed 
		self.TASKS += TaskTendermintHealthError
		if self.isStaking() and self.conf.val_address != '':
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
		return rpcCall(self.EP, 'abci_info')

	def getHeight(self):
		return rpcCall(self.EP, 'abci_info')['response']['last_block_height']

	def getBlockHash(self):
		return rpcCall(self.EP, 'status')['sync_info']['latest_block_hash']

	def getPeerNumber(self):
		return rpcCall(self.EP, 'net_info')['n_peers']

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		return True if int(rpcCall(self.EP, 'status')['validator_info']['voting_power']) > 0 else False

	def getValidatorAddress(self):
		return rpcCall(self.EP, 'status')['validator_info']['address']
