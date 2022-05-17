from .chain import Chain
from ..utils import Bash 
import json

class Tezos (Chain):
    NAME = "tezos"
    BLOCKTIME = 60
    EP = 'http://127.0.0.1:8732/'
    CUSTOM_TASKS = []

    def __init__(self, conf):
        super().__init__(conf)

    def detect(conf):
        try:
            Tezos(conf).getVersion()
            return True
        except:
            return False

    def getLatestVersion(self):
        raise Exception('Abstract getLatestVersion()')

    def getVersion(self):
        return self._nodeInfo()['version']

    def getHeight(self):
        return self.getCall('chains/main/blocks/head/helpers/current_level')['level']

    def getBlockHash(self):
        return self._nodeInfo()['lastBlockID']

    def getPeerCount(self):
        return len(self._nodeInfo()['network']['seedPeers'])

    def getNetwork(self):
        return self._nodeInfo()['genesisConfig']['communityIdentifier']

    def isStaking(self):
        return len(self._forgingStatus()) > 0

    def isSynching(self):
        return self._nodeInfo()['syncing']