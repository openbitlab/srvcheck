import requests
import srvcheck
from time import sleep
from . import Task, minutes, hours
from ..utils import Bash

class TaskAutoUpdater(Task):
	def __init__(self, conf, notification, system, chain):
		super().__init__('TaskAutoUpdater', conf, notification, system, chain, minutes(1), minutes(2))

	@staticmethod
	def isPluggable(conf):
		return True

	def run(self):
		nTag = requests.get('https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags').json()[-1]['ref'].split('/')[-1].split('v')[1]

		if srvcheck.__version__ != nTag:
			Bash(f'pip install --force-reinstall git+https://github.com/openbitlab/srvcheck@v{nTag}')
			Bash('systemctl restart node-monitor.service')
