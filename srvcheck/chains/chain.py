import requests
from ..utils import confGetOrDefault

def rpcCall(url, method, params=[]):
    d = requests.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).json()
    return d['result']


def getCall(url, data):
    return requests.get(url, json=data).json()


class Chain:
    NAME = ""
    BLOCKTIME = 10

    def __init__(self, conf):
        self.conf = conf
        ep = confGetOrDefault(self.conf, 'chain.endpoint', '')
        if ep != '': self.EP = ep       
        b = confGetOrDefault(self.conf, 'chain.blockTime', 10, int)
        if b != '': self.BLOCKTIME = b
        n = confGetOrDefault(self.conf, 'chain.name', '')
        if n != '': self.NAME = n

    def rpcCall(self, method, params=[]):
        """ Calls the RPC method with the given parameters """
        return rpcCall(self.EP, method, params)

    def getCall(self, r, data):
        """ Calls the GET method with the given parameters """
        return getCall(self.EP + r, data)

    ### Abstract methods
    @staticmethod
    def detect(conf):
        """ Checks if the current server is running this chain """
        raise Exception('Abstract detect()')

    def getVersion(self):
        """ Returns software version """
        raise Exception('Abstract getVersion()')

    def getLatestVersion(self):
        """ Returns software local version """
        gh_repo = confGetOrDefault(self.conf, 'chain.ghRepository')
        if gh_repo:
            c = requests.get(f"https://api.github.com/repos/{gh_repo}/releases/latest").json()
            return c['tag_name']
        raise Exception('No github repo specified!')

    def getHeight(self):
        """ Returns the block height """
        raise Exception('Abstract getHeight()')

    def getBlockHash(self):
        """ Returns the block height """
        raise Exception('Abstract getHeight()')

    def getPeerCount(self):
        """ Returns the number of peers """
        raise Exception('Abstract getPeerCount()')

    def getNetwork(self):
        """ Returns network used """
        raise Exception('Abstract getNetwork()')

    def isStaking(self):
        """ Returns true if the node is staking """
        raise Exception('Abstract isStaking()')

    def isSynching(self):
        """ Returns true if the node is synching """
        raise Exception('Abstract isSynching()')
