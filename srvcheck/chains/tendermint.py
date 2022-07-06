import json
import configparser
import re
from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours, minutes
from ..utils import Bash
from ..utils import ConfItem, ConfSet

ConfSet.addItem(ConfItem('chain.activeSet', description='active set of validators'))
ConfSet.addItem(ConfItem('chain.blockWindow', 100, int))
ConfSet.addItem(ConfItem('chain.thresholdNotsigned', 5, int))

class TaskTendermintBlockMissed(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(1), notifyEvery=minutes(5)):
		super().__init__('TaskTendermintBlockMissed',
		      conf, notification, system, chain, checkEvery, notifyEvery)

		self.BLOCK_WINDOW = self.conf.getOrDefault('chain.blockWindow')
		self.THRESHOLD_NOTSIGNED = self.conf.getOrDefault('chain.thresholdNotsigned')
		self.prev = None
		self.prevMissed = None

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		nblockh = self.chain.getHeight()

		if self.prev is None:
			self.prev = nblockh
		missed = 0
		start = nblockh - self.BLOCK_WINDOW
		while start < nblockh:
			if not next((x for x in self.chain.getSignatures(start) if x['validator_address'] == self.chain.getValidatorAddress()), None):
				lastMissed = start 
				missed += 1

			start += 1

		if missed >= self.THRESHOLD_NOTSIGNED and (self.prevMissed is None or self.prevMissed != lastMissed):
			self.prevMissed = lastMissed
			self.prev = nblockh
			return self.notify(f'{missed} not signed blocks in the latest {self.BLOCK_WINDOW} {Emoji.BlockMiss}')

		return False

class TaskTendermintNewProposal(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=minutes(1), notifyEvery=hours(1)):
		super().__init__('TaskTendermintNewProposal',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev=None

	@staticmethod
	def isPluggable(conf):
		return True

	def getProposalTitle(self, proposal):
		if "id" in proposal:
			return proposal["messages"][0]["content"]["title"]
		elif "proposal_id" in proposal:
			return proposal["content"]["title"]

	def run(self):
		nProposal = self.chain.getLatestProposal()
		if not self.prev:
			self.prev = nProposal
			if nProposal.status == "PROPOSAL_STATUS_VOTING_PERIOD":
				return self.notify(f'got latest proposal: {self.getProposalTitle(nProposal)} {Emoji.Proposal}')
		elif "id" in self.prev and self.prev["id"] != nProposal["id"]:
			self.prev = nProposal
			return self.notify(f'got new proposal: {self.getProposalTitle(nProposal)} {Emoji.Proposal}')
		elif "proposal_id" in self.prev and self.prev["proposal_id"] != nProposal["proposal_id"]:
			self.prev = nProposal
			return self.notify(f'got new proposal: {self.getProposalTitle(nProposal)} {Emoji.Proposal}')
		return False

class TaskTendermintPositionChanged(Task):
	def __init__(self, conf, notification, system, chain, checkEvery=hours(1), notifyEvery=hours(10)):
		super().__init__('TaskTendermintPositionChanged',
		      conf, notification, system, chain, checkEvery, notifyEvery)
		self.ACTIVE_SET = self.conf.getOrDefault('chain.activeSet')
		self.prev = None

	@staticmethod
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
				return self.notify(f'position decreased from {prev} to {npos} {Emoji.PosDown}')
			else:
				return self.notify(f'position increased from {prev} to {npos} {Emoji.PosUp}')

		return False

	def getValidatorPosition(self):
		bh = str(self.chain.getHeight())
		active_vals = []
		if self.ACTIVE_SET is None:
			active_s = int(self.chain.rpcCall('validators', [bh, "1", "1"])['total'])
		else:
			active_s = int(self.ACTIVE_SET)
		if active_s > 100:
			it = active_s // 100
			diff = active_s
			for i in range(it):
				active_vals += self.chain.rpcCall('validators', [bh, str(i + 1), "100"])['validators']
				diff -= 100
			if diff > 0:
				active_vals += self.chain.rpcCall('validators', [bh, str(i + 2), "100"])['validators']
		else:
			active_vals += self.chain.rpcCall('validators', [bh, "1", str(active_s)])['validators']
		p = [i for i, j in enumerate(active_vals) if j['address'] == self.chain.getValidatorAddress()]
		return p[0] + 1 if len(p) > 0 else -1 

class TaskTendermintHealthError(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskTendermintHealthError', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		try:
			self.chain.getHealth()
			return False
		except Exception as _:
			return self.notify(f'health error! {Emoji.Health}')

class Tendermint (Chain):
	TYPE = "tendermint"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:26657/"
	CUSTOM_TASKS = [TaskTendermintBlockMissed, TaskTendermintPositionChanged, TaskTendermintHealthError, TaskTendermintNewProposal]

	@staticmethod
	def detect(conf):
		try:
			Tendermint(conf).getVersion()
			return True
		except:
			return False

	def getHealth(self):
		return self.rpcCall('health')

	def getVersion(self):
		return self.rpcCall('abci_info')

	def getLocalVersion(self):
		try:
			return self.getVersion()["response"]["version"]
		except Exception as e:
			ver = self.conf.getOrDefault('chain.localVersion')
			if ver is None:
				raise Exception('No local version of the software specified!') from e
			return ver

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
		return self.rpcCall('status')['sync_info']['catching_up']

	def getLatestProposal(self):
		serv = self.conf.getOrDefault('chain.service')
		if serv:
			c = configparser.ConfigParser()
			c.read(f"/etc/systemd/system/{serv}")
			cmd = re.split(' ', c["Service"]["ExecStart"])[0]
			return json.loads(Bash(cmd + " q gov proposals --reverse --limit 1 --output json").value())["proposals"][0]
		raise Exception('No service file name specified!')
