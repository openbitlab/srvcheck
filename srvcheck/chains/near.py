import json
from ..notification import Emoji
from .chain import Chain
from ..tasks import Task, seconds, hours, minutes

class TaskNearBlockMissed (Task):
    def __init__(self, conf, notification, system, chain, checkEvery=minutes(2), notifyEvery=minutes(5)):
        super().__init__("TaskNearBlockMissed", conf, notification, system, chain, checkEvery, notifyEvery)

        self.THRESHOLD_RATIO = 0.5
    
    @staticmethod
    def isPluggable(conf, chain):
        return True

    def run(self):
        try:
            r = self.chain.getProductionReport()
            expected = int(r['num_expected_blocks'])
            produced = int(r['num_produced_blocks'])
            if produced/expected < self.THRESHOLD_RATIO:
                return self.notify(f'produced only {produced} / {expected} blocks {Emoji.BlockMiss}')
        except:
            return False
        return False

class TaskNearChunksMissed (Task):
    def __init__(self, conf, notification, system, chain, checkEvery=minutes(1), notifyEvery=minutes(3)):
        super().__init__("TaskNearChunksMissed", conf, notification, system, chain, checkEvery, notifyEvery)

        self.THRESHOLD_RATIO = 0.6
    
    @staticmethod
    def isPluggable(conf, chain):
        return True

    def run(self):
        try:
            r = self.chain.getProductionReport()
            expected = int(r['num_expected_chunks'])
            produced = int(r['num_produced_chunks'])
            if produced/expected < self.THRESHOLD_RATIO:
                return self.notify(f'produced only {produced} / {expected} chunks {Emoji.BlockMiss}')
        except:
            return False
        return False

    

class Near (Chain):
    TYPE = "near"
    NAME = ""
    BLOCKTIME = 60
    EP = "http://localhost:3030/"
    CUSTOM_TASKS = [ TaskNearBlockMissed, TaskNearChunksMissed]

    @staticmethod
    def detect(conf):
        try:
            Near(conf).getVersion()
            return True
        except:
            return False

    def getPeerCount(self):
        return int(self.rpcCall("network_info")["num_active_peers"])

    def getHeight(self):
        return int(self.rpcCall("block", [{ "finality": "final" }])['header']['height'])

    def isSynching(self):
        return self.rpcCall('status')['sync_info']['syncing']

    def getVersion(self):
        return self.rpcCall('status')['version']['build']

    def getPoolId(self):
        return self.rpcCall('status')['validator_account_id']

    def getProductionReport(self):
        validators = self.rpcCall('validators')['current_validators']
        for v in validators:
            if v['account_id'] == self.getPoolId():
                return v
        raise Exception('Node is not in the current validators!')

    

