from .substrate import (
    Substrate,
    TaskSubstrateBlockProductionReportCharts,
    TaskSubstrateBlockProductionReportParachain,
    TaskSubstrateRelayChainStuck,
)


class Mangata(Substrate):
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
            Mangata(conf).getVersion()
            return (
                Mangata(conf).isParachain()
                and Mangata(conf).getNodeName() == "Mangata Parachain Collator"
            )
        except:
            return False

    def getSession(self):
        si = self.getSubstrateInterface()
        result = si.query(
            module="ParachainStaking", storage_function="Round", params=[]
        )
        return result.value

    def isCollating(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            si = self.getSubstrateInterface()
            result = si.query(
                module="ParachainStaking",
                storage_function="SelectedCandidates",
                params=[],
            )
            for c in result.value:
                if c.lower() == collator.lower():
                    return True
        return False

    def getSessionWrapped(self):
        return self.getSession()["current"]

    def getStartingRoundBlock(self):
        return self.getSession()["first"]
