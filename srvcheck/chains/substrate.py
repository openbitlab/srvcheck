from .chain import Chain, rpcCall

class Substrate (Chain):
    TYPE = "substrate"
    NAME = ""
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
        return self.rpcCall('system_version')

    def getHeight(self):
        raise Exception('Abstract getHeight()')

    def getBlockHash(self):
        return self.rpcCall('chain_getBlockHash')

    def getPeerCount(self):
        return self.rpcCall('system_health')['peers']

    def getNetwork(self):
        raise Exception('Abstract getNetwork()')

    def isStaking(self):
        raise Exception('Abstract isStaking()')