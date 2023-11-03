# MIT License

# Copyright (c) 2021-2023 Openbitlab Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from srvcheck.tasks.task import minutes

from ..notification import Emoji, NotificationLevel
from ..tasks import Task
from .substrate import (
    Substrate,
    TaskSubstrateBlockProductionReportCharts,
    TaskSubstrateBlockProductionReportParachain,
    TaskSubstrateRelayChainStuck,
)


class TaskAstarBlockProductionCheck(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        super().__init__(
            "TaskAstarBlockProductionCheck", services, checkEvery, notifyEvery
        )
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
                        + f"{self.prev} {Emoji.BlockMiss}",
                        level=NotificationLevel.Error,
                    )
                self.prev = block
        return False


class Astar(Substrate):
    TYPE = "parachain"
    CUSTOM_TASKS = [
        TaskSubstrateRelayChainStuck,
        TaskSubstrateBlockProductionReportParachain,
        TaskSubstrateBlockProductionReportCharts,
        TaskAstarBlockProductionCheck,
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
            result = self.sub_iface.query(
                module="CollatorSelection", storage_function="Candidates", params=[]
            )
            for c in result.value:
                if c["who"].lower() == f"{collator}".lower():
                    return True
            result = self.sub_iface.query(
                module="CollatorSelection", storage_function="Invulnerables", params=[]
            )
            for c in result.value:
                if c.lower() == f"{collator}".lower():
                    return True
        return False

    def latestBlockProduced(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            result = self.sub_iface.query(
                module="CollatorSelection",
                storage_function="LastAuthoredBlock",
                params=[collator],
            )
            return result.value
        return 0

    def getStartingRoundBlock(self):
        return -1
