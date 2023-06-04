from srvcheck.tasks.task import minutes

from ..notification import Emoji
from ..tasks import Task
from .substrate import (
    Substrate,
    TaskBlockProductionReportCharts,
    TaskBlockProductionReportParachain,
    TaskRelayChainStuck,
)


class TaskBlockProductionCheck(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        super().__init__("TaskBlockProductionCheck", services, checkEvery, notifyEvery)
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


class Astar(Substrate):
    TYPE = "parachain"
    CUSTOM_TASKS = [
        TaskRelayChainStuck,
        TaskBlockProductionReportParachain,
        TaskBlockProductionReportCharts,
        TaskBlockProductionCheck,
    ]

    def __init__(self, conf):
        super().__init__(conf)

    @staticmethod
    def detect(conf):
        try:
            Astar(conf).getVersion()
            return (
                Astar(conf).isParachain()
                and Astar(conf).getNodeName() == "Astar Collator"
            )
        except:
            return False

    def isCollating(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            si = self.getSubstrateInterface()
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
            si = self.getSubstrateInterface()
            result = si.query(
                module="CollatorSelection",
                storage_function="LastAuthoredBlock",
                params=[collator],
            )
            return result.value
        return 0

    def getStartingRoundBlock(self):
        return -1
