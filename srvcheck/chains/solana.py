from statistics import median
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
			return self.notify('health error! %s' % Emoji.Health)

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
			median = self.chain.getMedianLastVote()
			return self.notify('last vote stuck at height: %d, median is: %d %s' % (lastVote, median, Emoji.Slow))
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
			return self.notify('active stake for epoch %s: %d SOL %s' % (ep, act_stake, Emoji.ActStake))
		return False

class TaskSolanaLeaderSchedule(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(24)):
		super().__init__('TaskSolanaLeaderSchedule', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	def isPluggable(conf):
		return True

	def run(self):
		ep = self.chain.getEpoch()

		if self.prev == None:
			self.prev = ep

		try:
			if self.prev != ep:
				self.chain.getLeaderSchedule()
				self.prev = ep
			return False
		except Exception:
			return self.notify('no leader slot assigned for the epoch %s %s' % (ep, Emoji.NoLeader))

class TaskSolanaSkippedSlots(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(24), notifyEvery=hours(24)):
		super().__init__('TaskSolanaSkippedSlots', conf, notification, system, chain, checkEvery, notifyEvery)

	def isPluggable(conf):
		return True

	def run(self):
		bp_info = self.chain.getBlockProduction()
		skipped_perc = bp_info[1] / bp_info[0]
		if skipped_perc > self.THRESHOLD_SKIPPED_SLOT:
			return self.notify('skipped %d%% of assigned slots (%d/%d) %s' % (int(skipped_perc), bp_info[1], bp_info[0], Emoji.BlockMiss))
		return False

class Solana (Chain):
	TYPE = "solana"
	NAME = ""
	BLOCKTIME = 60
	THRESHOLD_SKIPPED_SLOT = 0.25 # 25 % 
	EP = "http://localhost:8899/"
	CUSTOM_TASKS = [ TaskSolanaHealthError, TaskSolanaDelinquentCheck, TaskSolanaBalanceCheck, TaskSolanaLastVoteCheck, TaskSolanaEpochActiveStake, TaskSolanaLeaderSchedule, TaskSolanaSkippedSlots ]
	
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

	def getLeaderSchedule(self):
		identityAddr = self.getIdentityAddress()
		schedule = self.rpcCall('getLeaderSchedule', [ None, { "identity": identityAddr } ])
		if len(schedule) == 1:
			return schedule[identityAddr]
		raise Exception('No leader slot assigned to your Identity for the current epoch')

	def getBlockProduction(self):
		identityAddr = self.getIdentityAddress()
		b_prod_info = self.rpcCall('getBlockProduction', [ { "identity": identityAddr } ])['value']['byIdentity']
		if len(b_prod_info) == 1:
			return b_prod_info[identityAddr]
		raise Exception('No blocks produced in the current epoch')

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
	
	def getMedianLastVote(self):
		validators = self.getValidators()
		votes = []
		for v in validators:
			votes.append(v["lastVote"])
		return median(votes)
