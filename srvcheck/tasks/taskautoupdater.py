import requests
import srvcheck
from packaging import version
from . import Task, minutes, hours
from ..utils import Bash

def versionCompare(v1, v2):
	v1 = version.parse(current)
	v2 = version.parse(latest)

	if v1 < v2:
		return -1
	elif v1 > v2:
		return 1
	else:
		return 0

class TaskAutoUpdater(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAutoUpdater', conf, notification, system, chain, minutes(60), hours(2))

	@staticmethod
	def isPluggable(conf, chain):
		return True

	def run(self):
		nTag = requests.get('https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags').json()[-1]['ref'].split('/')[-1].split('v')[1]

		if versionCompare(nTag, srvcheck.__version__) > 0:
			self.notify(f'New monitor version detected: v{nTag}')
			self.notification.flush()
			Bash(f'pip install --force-reinstall git+https://github.com/openbitlab/srvcheck@v{nTag}')
			Bash('systemctl restart node-monitor.service')
