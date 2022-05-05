from .chain import Chain, rpcCall
from ..tasks import Task

class TaskTendermintBlockMissed(Task):
	def __init__(self, notification, system, chain, checkEvery=60, notifyEvery=60*10):
		self.BLOCK_WINDOW = chain.conf["blockWindow"]
		self.THRESHOLD_NOTSIGNED = chain.conf["thresholdNotsigned"]

		super().__init__('TaskTendermintBlockMissed',
		      notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	def run(self):
		nblockh = self.getHeight()

		if not self.prev:
			self.prev = nblockh
			self.markChecked()
		elif nblockh - self.prev >= self.BLOCK_WINDOW:
			block = self.prev
			missed=0
			while block < self.prev+self.BLOCK_WINDOW:
				if self.getValidatorAddress() not in self.getSignatures(block): missed += 1
				block += 1
			if missed >= self.THRESHOLD_NOTSIGNED:
				self.notify('%d not signed blocks in the latest %d' % (missed, self.BLOCK_WINDOW))

		self.markChecked()


class TaskTendermintPositionChanged(Task):
	def __init__(self, notification, system, chain, checkEvery=60, notifyEvery=60*10):
		super().__init__('TaskTendermintPositionChanged',
		      notification, system, chain, checkEvery, notifyEvery)
		self.active_set = self.chain.conf["activeSet"]
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
			active_s = int(self.chain.rpcCall('validators', [bh, "1", "1"])['total'])
		else:
			active_s = int(self.active_set)
		if (active_s > 100):
			it = active_s // 100
			diff = 0
			for i in range(it):
				active_vals += self.chain.rpcCall('validators', [bh, str(i + 1), "100"])['validators']
				diff = active_s - 100
			if (diff > 0):
				active_vals += self.chain.rpcCall('validators', [bh, str(i + 2), "100"])['validators']
		else:
			active_vals += self.chain.rpcCall('validators', [bh, "1", str(active_s)])['validators']
		p = [i for i, j in enumerate(active_vals) if j['address'] == self.chain.getValidatorAddress()]
		return p[0] + 1 if len(p) > 0 else -1 

class TaskTendermintHealthError(Task):
	def __init__(self, notification, system, chain, checkEvery = 60, notifyEvery = 60*10):
		super().__init__('TaskTendermintHealthError', notification, system, chain, checkEvery, notifyEvery)
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
		self.TASKS += TaskTendermintHealthError
		if self.isStaking():
			self.TASKS += TaskTendermintPositionChanged
			self.TASKS += TaskTendermintBlockMissed 

	def detect(conf):
		try:
			Tendermint(conf).getVersion()
			return True
		except:
			return False

	def getHealth(self):
		return self.rpcCall('health')

	def getLatestVersion(self):
		raise Exception('Abstract getLatestVersion()')

	def getVersion(self):
		return self.rpcCall('abci_info')

	def getHeight(self):
		return self.rpcCall('abci_info')['response']['last_block_height']

	def getBlockHash(self):
		return self.rpcCall('status')['sync_info']['latest_block_hash']

	def getPeerNumber(self):
		return self.rpcCall('net_info')['n_peers']

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		return True if int(self.rpcCall('status')['validator_info']['voting_power']) > 0 else False

	def getValidatorAddress(self):
		return self.rpcCall('status')['validator_info']['address']

	def getSignatures(self, height):
		return self.rpcCall('block')['height']['block']['last_commit']['signatures']
