from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours
import requests
from ..utils import Bash
import json
import configparser
import re

class TaskTendermintBlockMissed(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=hours(10)):
		self.BLOCK_WINDOW = int(conf["chain"]["blockWindow"])
		self.THRESHOLD_NOTSIGNED = int(conf["chain"]["thresholdNotsigned"])

		super().__init__('TaskTendermintBlockMissed',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		nblockh = self.chain.getHeight()

		if not self.prev:
			self.prev = nblockh
		elif nblockh - self.prev >= self.BLOCK_WINDOW:
			block = int(self.prev)
			missed = 0
			while block < self.prev + self.BLOCK_WINDOW:
				if self.getValidatorAddress() not in self.getSignatures(block): missed += 1
				block += 1
			if missed >= self.THRESHOLD_NOTSIGNED:
				return self.notify('%d not signed blocks in the latest %d %s' % (missed, self.BLOCK_WINDOW, Emoji.BlockMiss))

		return False

class TaskTendermintNewProposal(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(2), notifyEvery=hours(10)):
		super().__init__('TaskTendermintNewProposal',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev=None

	def isPluggable(conf):
		return True
	
	def run(self):
		nProposal=self.chain.getLatestProposal()
		if not self.prev:
			self.prev = self.chain.getLatestProposal()
		elif self.prev["proposal_id"] != nProposal["proposal_id"]:
			self.prev = nProposal
			return self.notify(' got new proposal: %s %s' % (nProposal["content"]["title"], Emoji.Proposal))

		return False


class TaskTendermintPositionChanged(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=hours(10)):
		super().__init__('TaskTendermintPositionChanged',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.ACTIVE_SET = conf["chain"]["activeSet"]
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		npos = self.getValidatorPosition()

		if not self.prev:
			self.prev = npos

		if npos != self.prev:
			prev = self.prev
			self.prev = npos
			if npos > prev:
				return self.notify('position decreased from %d to %d %s' % (self.prev, npos, Emoji.PosUp))
			else:
				return self.notify('position increased from %d to %d %s' % (self.prev, npos, Emoji.PosDown))
				
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
			diff = active_s
			for i in range(it):
				active_vals += self.chain.rpcCall('validators', [bh, str(i + 1), "100"])['validators']
				diff -= 100
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
			return self.notify('Health error! %s' % Emoji.Health)

class Tendermint (Chain):
	TYPE = "tendermint"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:26657/"
	CUSTOM_TASKS = [TaskTendermintBlockMissed, TaskTendermintPositionChanged, TaskTendermintHealthError]
	
	def __init__(self, conf):
		super().__init__(conf)

	def detect(conf):
		try:
			Tendermint(conf).getVersion()
			return True
		except:
			return False

	def getHealth(self):
		return self.rpcCall('health')

	def getLatestVersion(self):
		c = requests.get('https://api.github.com/repos/' + self.conf['chain']['ghRepository']+ '/releases/latest').json()
		return c['tag_name']

	def getVersion(self):
		try:
			return self.rpcCall('abci_info')["response"]["version"]
		except:
			return self.conf['chain']['localVersion']

	def getHeight(self):
		return int(self.rpcCall('abci_info')['response']['last_block_height'])

	def getBlockHash(self):
		return self.rpcCall('status')['sync_info']['latest_block_hash']

	def getPeerCount(self):
		return int(self.rpcCall('net_info')['n_peers'])

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		return True if int(self.rpcCall('status')['validator_info']['voting_power']) > 0 else False

	def getValidatorAddress(self):
		return self.rpcCall('status')['validator_info']['address']

	def getSignatures(self, height):
		return self.rpcCall('block', [str(height)])['block']['last_commit']['signatures']

	def isSynching(self):
		raise Exception('Abstract isSynching()')
	
	def getLatestProposal(self):
		cmd = configparser.ConfigParser().read('/etc/systemd/system/'+self.chain.conf["chain"]["service"])
		cmd = re.split(' ', cmd["Service"]["ExecStart"])[0]
		return json.loads(Bash(cmd+" q gov proposal --reverse --limit 1 --output json").stdout)["proposals"][0]
