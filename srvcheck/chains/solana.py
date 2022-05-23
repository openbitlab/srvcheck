from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours, minutes
from ..utils import Bash
from ..utils import confGetOrDefault
import requests
import json

class TaskSolanaHealthError(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskSolanaHealthError', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	def isPluggable(conf):
		return True

	def run(self):
		try:
			self.chain.getHealth()
			return False
		except Exception as e:
			return self.notify('Health error! %s' % Emoji.Health)

class TaskSolanaDelinquentCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskSolanaDelinquentCheck', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	def isPluggable(conf):
		return True

	def run(self):
		if self.chain.isDelinquent():
			return self.notify('validator is delinquent %s' % Emoji.Delinq)
		else:
			return False

class TaskSolanaBalanceCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskSolanaBalanceCheck', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	def isPluggable(conf):
		return True

	def run(self):
		balance = self.chain.getValidatorBalance()
		if balance < 1.0:
			return self.notify('validator balance is too low, %s SOL left %s' % (balance, Emoji.LowBal))
		else:
			return False

class TaskSolanaLastVoteCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = 30, notifyEvery=minutes(5)):
		super().__init__('TaskSolanaLastVoteCheck', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	def isPluggable(conf):
		return True

	def run(self):
		lastVote = self.chain.getLastVote()
		if self.prev == None:
			self.prev = lastVote
		elif self.prev == lastVote:
			return self.notify(' last vote stuck at height: %d %s' % (lastVote, Emoji.Stuck))
		self.prev = lastVote
		return False

class TaskSolanaEpochActiveStake(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(24)):
		super().__init__('TaskSolanaEpochActiveStake', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None
		self.prevEpoch = None

	def isPluggable(conf):
		return True

	def run(self):
		ep = self.chain.getEpoch()
		act_stake = self.chain.getActiveStake()

		if self.prev == None:
			self.prev = act_stake
		if self.prevEpoch == None:
			self.prevEpoch = ep
		
		if self.prevEpoch != ep:
			self.prev = act_stake
			self.prevEpoch = ep
			return self.notify(' active stake for epoch %s: %d SOL %s' % (ep, act_stake, Emoji.ActStake))
		return False
		
class Solana (Chain):
	TYPE = "solana"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:8899/"
	CUSTOM_TASKS = [ TaskSolanaHealthError, TaskSolanaDelinquentCheck, TaskSolanaBalanceCheck, TaskSolanaEpochActiveStake ]
	
	def __init__(self, conf):
		super().__init__(conf)

	def detect(conf):
		try:
			Solana(conf).getVersion()
			return True
		except:
			return False

	def getHealth(self):
		return self.rpcCall('getHealth')

	def getVersion(self):
		return self.rpcCall('getVersion')["solana-core"]

	def getLocalVersion(self):
		return self.getVersion()

	def getHeight(self):
		return self.rpcCall('getBlockHeight')

	def getBlockHash(self):
		return self.rpcCall('getLatestBlockhash')['value']['blockhash']

	def getEpoch(self):
		return self.rpcCall('getEpochInfo')['epoch']

	def getPeerCount(self):
		raise Exception('Abstract getPeerCount()')

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		raise Exception('Abstract isStaking()')

	def isSynching(self):
		return False

	def getIdentityAddress(self):
		return Bash(f"solana address --url {self.EP}").value()

	def getValidators(self):
		return json.loads(Bash(f"solana validators --url {self.EP} --output json-compact").value())["validators"]

	def isDelinquent(self):
		return self.getValidatorInfo()["delinquent"]

	def getValidatorBalance(self):
		return float(Bash(f"solana balance {self.getIdentityAddress()} --url {self.EP} | grep -o '[0-9.]*'").value())

	def getLastVote(self):
		return self.getValidatorInfo()["lastVote"]

	def getActiveStake(self):
		return int(self.getValidatorInfo()["activatedStake"]) / (10**9)

	def getValidatorInfo(self):
		validators = self.getValidators()
		val_info = next((x for x in validators if x['identityPubkey'] == self.getIdentityAddress()), None)
		if val_info:
			return val_info
		raise Exception('Identity not found in the validators list')
