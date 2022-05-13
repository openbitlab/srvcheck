from distutils.core import setup
from . import Task, minutes, hours
from ..utils import Bash
import requests
import srvcheck

class TaskAutoUpdater(Task):
    def __init__(self, conf, notification, system, chain):
        super().__init__('TaskAutoUpdater', conf, notification, system, chain, minutes(60), hours(2))

    def isPluggable(conf):
        return True
    
    def run(self):
        nTag = requests.get('https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags').json()
        nTag = nTag[-1]['ref'].split('/')[-1].split('v')[1]

        if srvcheck.__version__ != nTag:
            self.notify('Installing new monitor version: %s' % (nTag))
            Bash('pip install --upgrade git+https://github.com/openbitlab/srvcheck@'+nTag)
            Bash('systemctl restart node-monitor.service')



