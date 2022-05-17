from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours
from ..utils import Bash
import requests

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
		if balance < 1:
			return self.notify('validator balance is too low,  %s SOL left %s' % (balance, Emoji.LowBal))
		else:
			return False

class Solana (Chain):
	TYPE = "solana"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:8899/"
	CUSTOM_TASKS = [ TaskSolanaHealthError, TaskSolanaDelinquentCheck ]
	
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

	def getLatestVersion(self):
		c = requests.get(f"https://api.github.com/repos/{self.conf['chain']['ghRepository']}/releases/latest").json()
		return c['tag_name']

	def getVersion(self):
		return self.rpcCall('getVersion')["solana-core"]

	def getHeight(self):
		return self.rpcCall('getBlockHeight')

	def getBlockHash(self):
		return self.rpcCall('getLatestBlockhash')['value']['blockhash']

	def getPeerCount(self):
		raise Exception('Abstract getPeerCount()')

	def getNetwork(self):
		raise Exception('Abstract getNetwork()')

	def isStaking(self):
		raise Exception('Abstract isStaking()')

	def isSynching(self):
		raise Exception('Abstract isSynching()')

	def getIdentityAddress(self):
		return Bash(f"solana address --url {self.EP}")

	def getValidators(self):
		return Bash(f"solana validators --url {self.EP} --output json-compact")["validators"]

	def isDelinquent(self):
		validators = self.getValidators()
		val_info = [i for i in validators if i['identityPubkey'] == self.getIdentityAddress()]
		if len(val_info) > 0:
			return val_info[0]["delinquent"]
		raise Exception('Identity not found in the validators list')

	def getValidatorBalance(self):
		return int(Bash(f"solana balance {self.getIdentityAddress()} --url {self.EP} | grep -o '[0-9.]*'"))