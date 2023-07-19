from srvcheck.tasks.task import minutes

from ..notification import Emoji
from ..tasks import Task
from .substrate import (
    Substrate,
    TaskSubstrateBlockProductionReportCharts,
    TaskSubstrateBlockProductionReportParachain,
    TaskSubstrateRelayChainStuck,
)


class TaskBridgeHubPolkaBlockProductionCheck(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        super().__init__("TaskBridgeHubPolkaBlockProductionCheck", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return services.chain.isParachain()

    def run(self):
        if self.s.chain.isCollating():
            block = self.s.chain.latestBlockProduced()
            if block > 0:
                if self.prev is None:
                    self.prev = block
                elif self.prev == block:
                    return self.notify(
                        "no block produced in the latest 30 minutes! Last block produced was "
                        + f"{self.prev} {Emoji.BlockMiss}"
                    )
                self.prev = block
        return False


class BridgeHubPolka(Substrate):
    TYPE = "parachain"
    CUSTOM_TASKS = [
        TaskSubstrateRelayChainStuck,
        TaskSubstrateBlockProductionReportParachain,
        TaskSubstrateBlockProductionReportCharts,
        TaskBridgeHubPolkaBlockProductionCheck,
    ]

    def __init__(self, conf):
        super().__init__(conf)

    @staticmethod
    def detect(conf):
        try:
            BridgeHubPolka(conf).getVersion()
            return (
                BridgeHubPolka(conf).isParachain()
                and BridgeHubPolka(conf).getNodeName() == "Polkadot parachain"
            )
        except:
            return False

    def isCollating(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            si = self.sub_iface
            result = si.query(
                module="CollatorSelection", storage_function="Candidates", params=[]
            )
            for c in result.value:
                if c["who"].lower() == f"{collator}".lower():
                    return True
            result = si.query(
                module="CollatorSelection", storage_function="Invulnerables", params=[]
            )
            for c in result.value:
                if c.lower() == f"{collator}".lower():
                    return True
        return False

    def latestBlockProduced(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            si = self.sub_iface
            result = si.query(
                module="CollatorSelection",
                storage_function="LastAuthoredBlock",
                params=[collator],
            )
            return result.value
        return 0

    def getStartingRoundBlock(self):
        return -1
