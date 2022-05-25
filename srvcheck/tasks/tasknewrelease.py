from ..notification import Emoji
from . import Task, minutes, hours
import re

class TaskNewRelease(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskNewRelease', conf, notification, system, chain, minutes(15), hours(2))

	def isPluggable(conf):
		return True

	def run(self):
		current = self.chain.getLocalVersion()
		latest = self.chain.getLatestVersion()
		c_ver = re.findall(r'(\d+[.]\d+[.]\d+)', current)[0]
		l_ver = re.findall(r'(\d+[.]\d+[.]\d+)', latest)[0]

		if c_ver != l_ver:
			output = f"has new release: {latest} {Emoji.Rel}"
			if self.chain.TYPE == "solana":
				d_stake = self.chain.getDelinquentStakePerc()
				output += f"\n\tDelinquent Stake: {d_stake}%"
				output += f"\n\tIt's recommended to upgrade when there's less than 5% delinquent stake"
			return self.notify(output)

		return False