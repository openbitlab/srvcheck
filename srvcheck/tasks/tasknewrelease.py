import re
from packaging import version
from srvcheck.main import main
from ..notification import Emoji
from . import Task, minutes, hours
from ..utils import Bash


def versionCompare(current, latest, prerelease=False):
	c_ver = version.parse(current.split('-')[0])
	if prerelease:
		l_ver = version.parse(latest.split('-')[0])
	else: # ignore prerelease
		l_ver = version.parse(latest)

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
		self.config_file = "/etc/srvcheck.conf"

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

		if self.conf.getOrDefault('chain.localVersion') is None:
			return Bash(f'sed -i -e "s/^localVersion =.*/localVersion = {current}/" {self.config_file}').value()

		if versionCompare(self.conf.getOrDefault('chain.localVersion'), current) < 0:
			Bash(f'sed -i -e "s/^localVersion =.*/localVersion = {current}/" {self.config_file}').value()
			return self.notify(f'is now running latest version: {current}')
		
		return False