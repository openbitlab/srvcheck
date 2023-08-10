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
