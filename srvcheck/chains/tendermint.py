from fileinput import isstdin
from .chain import Chain, rpcCall
from ..tasks import Task
import requests

class TendermintBlockMissedTask(Task):
    def __init__(self, notification, chain, checkEvery = 15, notifyEvery = 15):
        super().__init__('TendermintBlockMissed', notification, chain, checkEvery, notifyEvery)

    def run(self):
        pass 

class TendermintPositionChange(Task):
    def __init__(self, notification, chain, checkEvery = 15, notifyEvery = 15):
        super().__init__('TendermintPositionChange', notification, chain, checkEvery, notifyEvery)

    def run(self):
        pass 

class Tendermint (Chain):
    NAME = "Tendermint"
    BLOCKTIME = 15
    EP = 'http://localhost:26657/'

    def __init__(self, conf):
        super().__init__(conf)
        self.TASKS += TendermintBlockMissedTask
        if self.isStaking():
            self.TASKS += TendermintPositionChange

    def detect():
        try:
            Tendermint().getVersion()
            return True
        except:
            return False

    def getLatestVersion(self):
        raise Exception('Abstract getLatestVersion()')

    def getVersion(self):
        return rpcCall(self.EP, 'abci_info')

    def getHeight(self):
        return rpcCall(self.EP, 'abci_info')['response']['last_block_height']

    def getBlockHash(self):
        return rpcCall(self.EP, 'status')['sync_info']['latest_block_hash']

    def getPeerNumber(self):
        return rpcCall(self.EP, 'net_info')['n_peers']

    def getNetwork(self):
        raise Exception('Abstract getNetwork()')

    def isStaking(self):
        return True if int(rpcCall(self.EP, 'status')['validator_info']['voting_power']) > 0 else False