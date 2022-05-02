from .chain import Chain
from ..tasks import Task
import requests

class TendermintBlockMissedTask(Task):
    def __init__(self, notification, chain, checkEvery = 15, notifyEvery = 15):
        super().__init__('TendermintBlockMissed', notification, chain, checkEvery, notifyEvery)

    def run(self):
        pass 

class Tendermint (Chain):
    NAME = "Tendermint"
    BLOCKTIME = 15 

    def __init__(self, conf):
        super().__init__(conf)
        self.TASKS += TendermintBlockMissedTask 

    def detect():
        try:
            Tendermint().getVersion()
            return True
        except:
            return False

    def getLatestVersion(self):
        raise Exception('Abstract getLatestVersion()')

    def getVersion(self):
        raise Exception('Abstract getVersion()')

    def getHeight(self):
        raise Exception('Abstract getHeight()')

    def getBlockHash(self):
        raise Exception('Abstract getHeight()')

    def getPeerNumber(self):
        raise Exception('Abstract getPeerNumber()')

    def getNetwork(self):
        raise Exception('Abstract getNetwork()')

    def isStaking(self):
        raise Exception('Abstract isStaking()')