from distutils.core import setup
from . import Task, minutes, hours
from ..utils import Bash
import requests
import srvcheck

class TaskAutoUpdater(Task):
    def __init__(self, confSet, notification, system, chain):
        super().__init__('TaskAutoUpdater', confSet, notification, system, chain, minutes(60), hours(2))

    def isPluggable(confSet):
        return True
    
    def run(self):
        nTag = requests.get('https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags').json()[-1]['ref'].split('/')[-1].split('v')[1]

        if srvcheck.__version__ != nTag:
            self.notify('installing new monitor version: %s' % (nTag))
            Bash('pip install --upgrade git+https://github.com/openbitlab/srvcheck@'+nTag)
            Bash('systemctl restart node-monitor.service')



