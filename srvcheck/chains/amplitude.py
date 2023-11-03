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

from .substrate import (
    Substrate,
    TaskSubstrateBlockProductionReportCharts,
    TaskSubstrateBlockProductionReportParachain,
    TaskSubstrateRelayChainStuck,
)


class Amplitude(Substrate):
    TYPE = "parachain"
    CUSTOM_TASKS = [
        TaskSubstrateRelayChainStuck,
        TaskSubstrateBlockProductionReportParachain,
        TaskSubstrateBlockProductionReportCharts,
    ]

    def __init__(self, conf):
        super().__init__(conf)

    @staticmethod
    def detect(conf):
        try:
            Amplitude(conf).getVersion()
            return (
                Amplitude(conf).isParachain()
                and Amplitude(conf).getNodeName() == "Pendulum Collator"
            )
        except:
            return False

    def getRoundInfo(self):
        result = self.sub_iface.query(
            module="ParachainStaking", storage_function="Round", params=[]
        )
        return result.value

    def isCollating(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            result = self.sub_iface.query(
                module="ParachainStaking", storage_function="TopCandidates", params=[]
            )
            for c in result.value:
                if c["owner"].lower() == collator.lower():
                    return True
        return False

    def getStartingRoundBlock(self):
        return self.getRoundInfo()["first"]
