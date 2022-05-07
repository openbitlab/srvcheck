from .chain import Chain
from ..tasks import Task,  hours

class TaskTendermintBlockMissed(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=hours(10)):
		self.BLOCK_WINDOW = conf["blockWindow"]
		self.THRESHOLD_NOTSIGNED = conf["thresholdNotsigned"]

		super().__init__('TaskTendermintBlockMissed',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		nblockh = self.getHeight()

		if not self.prev:
			self.prev = nblockh
		elif nblockh - self.prev >= self.BLOCK_WINDOW:
			block = self.prev
			missed = 0
			while block < self.prev+self.BLOCK_WINDOW:
				if self.getValidatorAddress() not in self.getSignatures(block): missed += 1
				block += 1
			if missed >= self.THRESHOLD_NOTSIGNED:
				return self.notify('%d not signed blocks in the latest %d %s' % (missed, self.BLOCK_WINDOW, self.notification.BLOCK_MISS_EMOJI))

		return False

class TaskTendermintPositionChanged(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=hours(10)):
		super().__init__('TaskTendermintPositionChanged',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.ACTIVE_SET = conf["activeSet"]
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		npos = self.getValidatorPosition()

		if not self.prev:
			self.prev = npos

		if npos != self.prev:
			if npos > self.prev:
				return self.notify('Position increased from %d to %d %s' % (self.prev, npos, self.notification.POS_UP_EMOJI))
			else:
				return self.notify('Position decreased from %d to %d %s' % (self.prev, npos, self.notification.POS_DOWN_EMOJI))
				
		return False


	def getValidatorPosition(self):
		bh = self.chain.getHeight()
		active_vals = []
		if (self.ACTIVE_SET == ''):
			active_s = int(self.chain.rpcCall('validators', [bh, "1", "1"])['total'])
		else:
			active_s = int(self.ACTIVE_SET)
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
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskTendermintHealthError', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	def isPluggable(conf):
		return True

	def run(self):
		try:
			self.chain.getHealth()
			return False
		except Exception as e:
			return self.notify('Health error! %s' % self.notification.HEALTH_EMOJI)
		

class Tendermint (Chain):
	TYPE = "tendermint"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:26657/"
	TASKS = []
	
	def __init__(self, conf):
		super().__init__(conf)
		self.TASKS.append(TaskTendermintHealthError)
		if self.isStaking():
			self.TASKS.append(TaskTendermintPositionChanged)
			self.TASKS.append(TaskTendermintBlockMissed)

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
		return self.rpcCall('block', [str(height)])['block']['last_commit']['signatures']
