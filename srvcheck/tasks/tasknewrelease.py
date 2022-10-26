import configparser
from packaging import version
from ..notification import Emoji
from . import Task, minutes, hours
from ..utils import Bash, ConfSet

def versionCompare(current, latest):
	c_ver = version.parse(current.split('-')[0]) if isinstance(version.parse(current), version.LegacyVersion) is True else version.parse(current)
	l_ver = version.parse(latest.split('-')[0]) if isinstance(version.parse(latest), version.LegacyVersion) is True else version.parse(latest)

	if c_ver < l_ver:
		return -1
	elif c_ver > l_ver:
		return 1
	else:
		return 0

class TaskNewRelease(Task):
	def __init__(self, services):
		super().__init__('TaskNewRelease', services, minutes(15), hours(2))
		self.cf = self.s.conf.getOrDefault('configFile')

	@staticmethod
	def isPluggable(services):
		return True if services.conf.getOrDefault('chain.ghRepository') else False

	def run(self):
		confRaw = configparser.ConfigParser()
		confRaw.optionxform=str
		confRaw.read(self.cf)
		self.conf = ConfSet(confRaw)

		current = self.s.chain.getLocalVersion()
		latest = self.s.chain.getLatestVersion()

		if self.conf.getOrDefault('chain.localVersion') is None:
			Bash(f'sed -i -e "s/^localVersion =.*/localVersion = {current}/" {self.cf}')
			return False
		
		if versionCompare(current, latest) < 0:
			output = f"has new release: {latest} {Emoji.Rel}"
			if self.s.chain.TYPE == "solana":
				d_stake = self.s.chain.getDelinquentStakePerc()
				output += f"\n\tDelinquent Stake: {d_stake}%"
				output += "\n\tIt's recommended to upgrade when there's less than 5% delinquent stake"
			return self.notify(output)

		if versionCompare(current, self.conf.getOrDefault('chain.localVersion')) > 0:
			Bash(f'sed -i -e "s/^localVersion =.*/localVersion = {current}/" {self.cf}')
			self.notify(f'is now running latest version: {current.split("-")[0]} {Emoji.Updated}')
			self.s.notification.flush()
		
		return False
