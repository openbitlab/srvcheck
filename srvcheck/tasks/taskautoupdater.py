import requests
import srvcheck
from . import Task, minutes, hours
from ..utils import Bash

def versionCompare(v1, v2):
	v1 = v1.split('.')
	v2 = v2.split('.')
	for i in range(min(len(v1), len(v2))):
		if int(v1[i]) > int(v2[i]):
			return 1
		elif int(v1[i]) < int(v2[i]):
			return -1
	return 0

class TaskAutoUpdater(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAutoUpdater', conf, notification, system, chain, minutes(60), hours(2))

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		nTag = requests.get('https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags').json()[-1]['ref'].split('/')[-1].split('v')[1]

		if versionCompare(srvcheck.__version__, nTag) > 0:
			self.notify(f'New monitor version detected: {nTag}')
			self.notification.flush()
			Bash(f'pip install --force-reinstall git+https://github.com/openbitlab/srvcheck@{nTag}')
			Bash('systemctl restart node-monitor.service')
