from statistics import median
import json
from ..notification import Emoji
from .chain import Chain
from ..tasks import Task, seconds, hours, minutes
from ..utils import Bash

class TaskSolanaHealthError(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskSolanaHealthError', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		try:
			self.chain.getHealth()
			return False
		except Exception as _:
			return self.notify(f'health error! {Emoji.Health}')

class TaskSolanaDelinquentCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskSolanaDelinquentCheck', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		if self.chain.isDelinquent():
			return self.notify(f'validator is delinquent {Emoji.Delinq}')
		else:
			return False

class TaskSolanaBalanceCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(10)):
		super().__init__('TaskSolanaBalanceCheck', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		balance = self.chain.getValidatorBalance()
		if balance < 1.0:
			return self.notify(f'validator balance is too low, {balance} SOL left {Emoji.LowBal}')
		else:
			return False

class TaskSolanaLastVoteCheck(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = seconds(30), notifyEvery=minutes(5)):
		super().__init__('TaskSolanaLastVoteCheck', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None 

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		lastVote = self.chain.getLastVote()
		md = self.chain.getMedianLastVote()
		if self.prev is None:
			self.prev = lastVote
		elif self.prev == lastVote and md > lastVote:
			return self.notify(f'last vote stuck at height: {lastVote}, median is: {md} {Emoji.Slow}')
		self.prev = lastVote
		return False

class TaskSolanaEpochActiveStake(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(24)):
		super().__init__('TaskSolanaEpochActiveStake', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None
		self.prevEpoch = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		ep = self.chain.getEpoch()
		act_stake = self.chain.getActiveStake()

		if self.prev is None:
			self.prev = act_stake
		if self.prevEpoch is None:
			self.prevEpoch = ep

		if self.prevEpoch != ep:
			self.prev = act_stake
			self.prevEpoch = ep
			return self.notify(f'active stake for epoch {ep}: {act_stake} SOL {Emoji.ActStake}')
		return False

class TaskSolanaLeaderSchedule(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(1), notifyEvery=hours(24)):
		super().__init__('TaskSolanaLeaderSchedule', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		ep = self.chain.getEpoch()

		if self.prev is None:
			self.prev = ep

		try:
			if self.prev != ep:
				schedule = self.chain.getLeaderSchedule()
				self.prev = ep
				return self.notify(f'{len(schedule)} leader slot assigned for the epoch {ep} {Emoji.Leader}')
			return False
		except Exception:
			return self.notify(f'no leader slot assigned for the epoch {ep} {Emoji.NoLeader}')

class TaskSolanaSkippedSlots(Task):
	def __init__(self, conf, notification, system, chain, checkEvery = hours(6), notifyEvery=hours(6)):
		super().__init__('TaskSolanaSkippedSlots', conf, notification, system, chain, checkEvery, notifyEvery)
		self.prev = None
		self.prevBP = 0
		self.prevM = 0
		self.THRESHOLD_SKIPPED_SLOT = 0.25 # 25 %

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		ep = self.chain.getEpoch()

		if self.prev is None:
			self.prev = ep

		bp_info = self.chain.getBlockProduction()
		if bp_info[0] != 0:
			skipped_perc = (bp_info[0] - bp_info[1]) / bp_info[0]
			if self.prev == ep:
				self.prevBP = bp_info[0]
				self.prevM = bp_info[1]
			if skipped_perc >= self.THRESHOLD_SKIPPED_SLOT:
				skip_p = f"{skipped_perc * 100:.2f}"
				return self.notify('skipped %s%% of assigned slots (%d/%d) %s' % (skip_p, bp_info[1], bp_info[0], Emoji.BlockMiss))
		if self.prev != ep:
			e = self.prev
			self.prev = ep
			if self.prevBP != 0:
				skip_p = f"{(self.prevBP - self.prevM) / self.prevBP * 100:.2f}"
				return self.notify('skipped %s%% of assigned slots (%d/%d) in the epoch %s %s' % (skip_p, self.prevM, self.prevBP, e, Emoji.BlockProd))
		return False

class Solana (Chain):
	TYPE = "solana"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:8899/"
	CUSTOM_TASKS = [ TaskSolanaHealthError, TaskSolanaDelinquentCheck, TaskSolanaBalanceCheck,
		TaskSolanaLastVoteCheck, TaskSolanaEpochActiveStake, TaskSolanaLeaderSchedule, TaskSolanaSkippedSlots ]

	@staticmethod
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

	def getGeneralValidatorsInfo(self):
		return json.loads(Bash(f"solana validators --url {self.EP} --output json-compact").value())

	def getValidators(self):
		return self.getGeneralValidatorsInfo()["validators"]

	def isDelinquent(self):
		return self.getValidatorInfo()["delinquent"]

	def getValidatorBalance(self):
		return float(Bash(f"solana balance {self.getIdentityAddress()} --url {self.EP} | grep -o '[0-9.]*'").value())

	def getLastVote(self):
		return self.getValidatorInfo()["lastVote"]

	def getActiveStake(self):
		return int(self.getValidatorInfo()["activatedStake"]) / (10**9)

	def getDelinquentStakePerc(self):
		val_info = self.getGeneralValidatorsInfo()
		act_stake = val_info["totalActiveStake"]
		del_stake = val_info["totalDelinquentStake"]
		return f"{del_stake / act_stake * 100:.2f}"

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
