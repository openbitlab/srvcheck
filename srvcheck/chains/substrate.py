from .chain import Chain, rpcCall
import requests

class Substrate (Chain):
    NAME = "substrate"
    BLOCKTIME = 15 
    EP = 'http://localhost:9933/'

    def __init__(self, conf):
        super().__init__(conf)
        self.TASKS = []

    def detect(conf):
        try:
            Substrate(conf).getVersion()
            return True
        except:
            return False

    def getLatestVersion(self):
        raise Exception('Abstract getLatestVersion()')

    def getVersion(self):
        return rpcCall(self.EP, 'system_version')

    def getHeight(self):
        raise Exception('Abstract getHeight()')

    def getBlockHash(self):
        return rpcCall(self.EP, 'chain_getBlockHash')

    def getPeerCount(self):
        return rpcCall(self.EP, 'system_health')['peers']

    def getNetwork(self):
        raise Exception('Abstract getNetwork()')

    def isStaking(self):
        raise Exception('Abstract isStaking()')