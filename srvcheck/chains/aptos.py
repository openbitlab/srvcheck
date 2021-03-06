from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours, minutes
from ..utils import Bash
import requests
import re
import json

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
		super().__init__('TaskAptosValidatorProposalCheck', conf, notification, system, chain, checkEvery = hours(1), notifyEvery = hours(1))
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		p_count = self.chain.getProposalsCount()

		if self.prev is None:
			self.prev = p_count
			return False 
		if p_count == self.prev or p_count == -1:
			return self.notify(f'is not proposing new consensus {Emoji.BlockMiss}')
		
		self.prev = p_count
		return False
	
class TaskAptosCurrentConsensusStuck(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAptosCurrentConsensusStuck', conf, notification, system, chain, checkEvery = minutes(5), notifyEvery=hours(1))
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		cur_round = self.chain.getCurrentConsensus()

		if self.prev is None:
			self.prev = cur_round
			return False 
		if cur_round == self.prev:
			return self.notify(f'consensus round stuck {Emoji.BlockMiss}')
		
		self.prev = cur_round
		return False

class Aptos (Chain):
	TYPE = "aptos"
	NAME = "aptos"
	BLOCKTIME = 15 
	EP = ''
	EP_VAL = 'http://localhost:8080/'
	EP_FULL = 'http://localhost:8081/'
	EP_METRICS_VAL = 'http://localhost:9101/metrics'
	EP_METRICS_FULL = 'http://localhost:9104/metrics'
	CUSTOM_TASKS = [TaskAptosHealthError, TaskAptosValidatorProposalCheck, TaskAptosCurrentConsensusStuck]

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
		out_val = requests.get(f"{self.EP_VAL}-/healthy")
		out_full = requests.get(f"{self.EP_FULL}-/healthy")
		return True if out_val.text == 'aptos-node:ok' and out_full.text == 'aptos-node:ok' else False
        
	def getHeight(self):
		out = requests.get(self.EP_FULL)
		return json.loads(out.text)['ledger_version']

	def getBlockHash(self):
		raise Exception('Abstract getBlockHash()')

	def getPeerCount(self):
		# aptos_connections
		raise Exception('Abstract getPeerCount()')

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		raise Exception('Abstract isStaking()')

	def isSynching(self):
		out_full = requests.get(self.EP_METRICS_FULL).text.split("\n")
		sync_status_full = [s for s in out_full if 'aptos_state_sync_version{type="synced"}' in s]
		out_val = requests.get(self.EP_METRICS_VAL).text.split("\n")
		sync_status_val = [s for s in out_val if 'aptos_state_sync_version{type="synced"}' in s]
		return True if len(sync_status_full) == 0 or len(sync_status_val) == 0 else False 

	def getProposalsCount(self):
		out_val = requests.get(self.EP_METRICS_VAL).text.split("\n")
		proposals_count = [s for s in out_val if 'aptos_consensus_proposals_count' in s and "#" not in s]
		if len(proposals_count) == 1:
			return int(proposals_count[0].split(" ")[-1])
		return -1

	def getCurrentConsensus(self):
		out = requests.get(self.EP_METRICS_VAL)
		cur_round = re.findall('aptos_consensus_current_round [0-9]+',out.text)[0].split(" ")[1].replace('"', '')
		return cur_round