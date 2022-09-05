import json
import re
import requests
from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours, minutes
from ..utils import ConfItem, ConfSet

ConfSet.addItem(ConfItem('chain.validatorAddress', description='Validator address'))

class TaskAptosHealthError(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskAptosHealthError', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		try:
			self.chain.getHealth()
			return False
		except Exception:
			return self.notify(f'health error! {Emoji.Health}')

class TaskAptosValidatorProposalCheck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAptosValidatorProposalCheck', conf, notification, system, chain, checkEvery = minutes(30), notifyEvery = hours(1))
		self.prevEpCount = None
		self.prevEp = None

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isValidator()

	def run(self):
		p_count = self.chain.getProposalsCount()
		ep = self.chain.getEpoch()

		if self.prevEpCount is None:
			self.prevEpCount = p_count
		if self.prevEp is None:
			self.prevEp = ep

		print(f'#Debug TaskAptosValidatorProposalCheck: {ep}, {p_count}, {self.prevEpCount}')
		if self.prevEp != ep:
			self.prevEp = ep
			if p_count == self.prevEpCount:
				return self.notify(f'is not proposing new consensus {Emoji.BlockMiss}')
			else:
				prevC = self.prevEpCount
				self.prevEpCount = p_count
				return self.notify(f'proposed {p_count - prevC} new consensus {Emoji.BlockProd}')
		return False
	
class TaskAptosCurrentConsensusStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAptosCurrentConsensusStuck', conf, notification, system, chain, checkEvery = minutes(5), notifyEvery=hours(1))
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isValidator()

	def run(self):
		cur_round = self.chain.getCurrentConsensus()

		print(f'#Debug TaskAptosCurrentConsensusStuck: {self.prev}, {cur_round}')
		if self.prev is None:
			self.prev = cur_round
			return False 
		if cur_round == self.prev:
			return self.notify(f'consensus round stuck {Emoji.BlockMiss}')
		
		self.prev = cur_round
		return False

class TaskAptosConnectedToFullNodeCheck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAptosConnectedToFullNodeCheck', conf, notification, system, chain, checkEvery = minutes(5), notifyEvery=hours(1))

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isValidator()

	def run(self):
		conn = self.chain.getConnections()

		print(f'#Debug TaskAptosConnectedToFullNodeCheck: {conn}')
		if len(conn) > 0:
			vfn_in = conn[1].split(" ")[-1]
			if vfn_in == "0":
				return self.notify(f'not connected to full node {Emoji.NoLeader}')

		return False

class TaskAptosConnectedToAptosNodeCheck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAptosConnectedToAptosNodeCheck', conf, notification, system, chain, checkEvery = minutes(5), notifyEvery=hours(1))

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isValidator()

	def run(self):
		aptosPeerId = 'f326fd30'

		print(f'#Debug TaskAptosConnectedToAptosNodeCheck: {self.chain.isConnectedToPeer(aptosPeerId)}')
		if self.chain.isConnectedToPeer(aptosPeerId) is False:
			return self.notify(f'not connected to Aptos node {Emoji.Peers}')

		return False

class TaskAptosStateSyncCheck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAptosStateSyncCheck', conf, notification, system, chain, checkEvery = minutes(5), notifyEvery=hours(1))
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		sync = int(self.chain.getAptosStateSyncVersion()[0].split(" ")[-1])

		print(f'#Debug TaskAptosStateSyncCheck: {sync}, {self.prev}')
		if self.prev is None:
			self.prev = sync
		elif sync == self.prev:
			return self.notify(f'is not state synching {Emoji.Stuck}')
		
		self.prev = sync
		return False

class TaskStakePoolRewardsCheck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskStakePoolRewardsCheck', conf, notification, system, chain, checkEvery = minutes(30), notifyEvery=hours(1))
		self.prev = None
		self.prevEp = None
		self.validatorAddress = conf.getOrDefault('chain.validatorAddress')

	@staticmethod
	def isPluggable(conf, chain):
		return chain.isValidator()

	def run(self):
		ep = self.chain.getEpoch()

		explorerAit3 = f"https://ait3.aptosdev.com/v1/accounts/{self.validatorAddress}/resources"
		res = requests.get(explorerAit3)
		stakedValue = int(json.loads(res.text)[1]['data']['active']['value'])

		if self.prev is None:
			self.prev = stakedValue
		if self.prevEp is None:
			self.prevEp = ep

		print(f'#Debug TaskStakePoolRewardsCheck: {ep}, {self.prev}, {stakedValue}')
		if self.prevEp != ep:
			self.prevEp = ep
			if self.prev == stakedValue:
				return self.notify(f'is not making staking rewards {Emoji.LowBal}')
			else:
				diff = stakedValue - self.prev
				self.prev = stakedValue
				return self.notify(f'made {diff} staking rewards, new active stake {stakedValue} {Emoji.ActStake}')
		return False

class Aptos (Chain):
	TYPE = "aptos"
	NAME = "aptos"
	BLOCKTIME = 15
	EP = 'http://localhost:8080/v1'
	EP_METRICS = 'http://localhost:9101/metrics'
	CUSTOM_TASKS = [TaskAptosHealthError, TaskAptosStateSyncCheck, TaskAptosValidatorProposalCheck, TaskAptosCurrentConsensusStuck, TaskAptosConnectedToFullNodeCheck, TaskAptosConnectedToAptosNodeCheck, TaskStakePoolRewardsCheck]

	@staticmethod
	def detect(conf):
		try:
			return Aptos(conf).getHealth()
		except:
			return False

	def getLatestVersion(self):
		raise Exception('Abstract getLatestVersion()')

	def getVersion(self):
		raise Exception('Abstract getVersion()')

	def getHealth(self):
		out = requests.get(f"{self.EP}/-/healthy")
		health = json.loads(out.text)['message']
		return True if health == 'aptos-node:ok' else False

	def getHeight(self):
		out = requests.get(self.EP)
		return json.loads(out.text)['block_height']

	def getEpoch(self):
		out = requests.get(self.EP)
		return json.loads(out.text)['epoch']

	def getBlockHash(self):
		raise Exception('Abstract getBlockHash()')

	def getPeerCount(self):
		conn = self.getConnections()
		if self.isValidator():
			if len(conn) > 1:
				in_peer = int(conn[0].split(" ")[-1])
				out_peer = int(conn[2].split(" ")[-1])
				return in_peer + out_peer
			return 0
		raise Exception('Abstract getPeerCount()')

	def getAptosStateSyncVersion(self):
		out = requests.get(self.EP_METRICS).text.split("\n")
		state_sync = [s for s in out if 'aptos_state_sync_version' in s and 'synced' in s]
		return state_sync

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def getRole(self):
		out = requests.get(self.EP)
		return json.loads(out.text)['node_role']

	def getConnections(self):
		out = requests.get(self.EP_METRICS).text.split("\n")
		connections = [s for s in out if 'aptos_connections' in s and '#' not in s]
		return connections

	def isConnectedToPeer(self, peerId):
		out = requests.get(self.EP_METRICS).text.split("\n")		
		conn = [s for s in out if 'aptos_network_peer_connected' in s and peerId in s]
		if len(conn) > 0:
			return True
		return False

	def isStaking(self):
		raise Exception('Abstract isStaking()')

	def isValidator(self):
		role = self.getRole()
		return True if role == "validator" else False

	def isSynching(self):
		out = requests.get(self.EP_METRICS).text.split("\n")
		sync_status = [s for s in out if 'aptos_state_sync_version{type="synced"}' in s]
		return True if len(sync_status) == 0 else False 

	def getProposalsCount(self):
		out_val = requests.get(self.EP_METRICS).text.split("\n")
		proposals_count = [s for s in out_val if 'aptos_consensus_proposals_count' in s and "#" not in s]
		if len(proposals_count) == 1:
			return int(proposals_count[0].split(" ")[-1])
		return -1

	def getCurrentConsensus(self):
		out = requests.get(self.EP_METRICS)
		cur_round = re.findall('aptos_consensus_current_round [0-9]+',out.text)[0].split(" ")[1].replace('"', '')
		return cur_round