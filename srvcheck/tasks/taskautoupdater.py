from . import Task, minutes, hours
import requests
import subprocess
import sys

class TaskAutoUpdater(Task):
    def __init__(self, conf, notification, system, chain):
        super().__init__('TaskAutoUpdater', conf, notification, system, chain, minutes(60), hours(2))
    
    def run(self):
        nTag = requests.get('https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags').json()[-1]['ref'].split('/')[-1]
        if self.conf["version"]["tagVersion"] != nTag:
            self.notify('Installing new monitor version: %s' % (nTag))
            subprocess.check_call([sys.executable, "pip", "install", "git+https://github.com/openbitlab/srvcheck"]) 
            subprocess.check_call([sys.executable, "systemctl", "restart", "node-monitor.service"])

      



