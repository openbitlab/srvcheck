import re
from ..notification import Emoji
from . import Task, minutes, hours

def versionCompare(current, latest):
	c_ver = "".join(re.findall(r'(\d+[.]\d+[.]\d+)', current)[0].split('.'))
	l_ver = "".join(re.findall(r'(\d+[.]\d+[.]\d+)', latest)[0].split('.'))

	if len(c_ver) < len(l_ver):
		c_ver = int(c_ver.ljust(len(l_ver), "0"))
		l_ver = int(l_ver)
	elif len(l_ver) < len(c_ver):
		l_ver = int(l_ver.ljust(len(l_ver), "0"))
		c_ver = int(c_ver)
	else:
		c_ver = int(c_ver)
		l_ver = int(l_ver)

	if c_ver < l_ver:
		return -1
	elif c_ver > l_ver:
		return 1
	else:
		return 0

class TaskNewRelease(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskNewRelease', conf, notification, system, chain, minutes(15), hours(2))
		self.conf = conf

	@staticmethod
	def isPluggable(conf, chain):
		return True if conf.getOrDefault('chain.ghRepository') else False

	def run(self):
		current = self.chain.getLocalVersion()
		latest = self.chain.getLatestVersion()

		if versionCompare(current, latest) < 0:
			output = f"has new release: {latest} {Emoji.Rel}"
			if self.chain.TYPE == "solana":
				d_stake = self.chain.getDelinquentStakePerc()
				output += f"\n\tDelinquent Stake: {d_stake}%"
				output += "\n\tIt's recommended to upgrade when there's less than 5% delinquent stake"
			return self.notify(output)

		return False
