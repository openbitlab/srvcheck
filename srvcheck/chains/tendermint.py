from .chain import Chain
import requests

class Tendermint (Chain):
    NAME = "Tendermint"
    BLOCKTIME = 15 

    def __init__(self, conf):
        super().__init__(conf)

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