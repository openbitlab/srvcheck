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
        self.active_set = self.chain.conf.active_set
        self.prev = self.getValidatorPosition()

    def run(self):
        pos = self.getValidatorPosition()
        if pos != self.prev:
            self.notify('$chain_name position changed to %s $up/down_emoji' % pos)
        self.markChecked() 

    def getValidatorPosition(self):
        bh = self.chain.getHeight()
        active_vals = []
        if (self.active_set == ''):
            active_s = int(rpcCall(self.chain.EP, 'validators', [bh, "1", "1"])['total'])
        else:
            active_s = int(self.active_set)
        if (active_s > 100):
            it = active_s // 100
            diff = 0
            for i in range(it):
                active_vals += rpcCall(self.chain.EP, 'validators', [bh, str(i + 1), "100"])['validators']
                diff = active_s - 100
            if (diff > 0):
                active_vals += rpcCall(self.chain.EP, 'validators', [bh, str(i + 2), "100"])['validators']
        else:
            active_vals += rpcCall(self.chain.EP, 'validators', [bh, "1", str(active_s)])['validators']
        p = [i for i, j in enumerate(active_vals) if j['address'] == self.chain.conf.val_address]
        return p[0] + 1 if len(p) > 0 else -1 

class Tendermint (Chain):
    NAME = "Tendermint"
    BLOCKTIME = 15
    EP = 'http://localhost:26657/'

    def __init__(self, conf):
        super().__init__(conf)
        self.TASKS += TendermintBlockMissedTask
        if self.isStaking() and conf.val_address != '':
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