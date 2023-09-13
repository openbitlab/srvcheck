from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes, seconds
from ..utils import Bash
from .chain import Chain


class TaskNearBlockMissed(Task):
    def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(6)):
        super().__init__("TaskNearBlockMissed", services, checkEvery, notifyEvery)
        self.THRESHOLD_RATIO = self.s.chain.getKickOutThresholds()[0]

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        try:
            r = self.s.chain.getProductionReport()
            expected = int(r["num_expected_blocks"])
            produced = int(r["num_produced_blocks"])
            if produced / expected < self.THRESHOLD_RATIO:
                return self.notify(
                    f"produced only {produced} / {expected} blocks {Emoji.BlockMiss}",
                    level=NotificationLevel.Warning,
                )
        except:
            return False
        return False


class TaskNearChunksMissed(Task):
    def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(6)):
        super().__init__("TaskNearChunksMissed", services, checkEvery, notifyEvery)

        self.THRESHOLD_RATIO = self.s.chain.getKickOutThresholds()[1]

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        try:
            r = self.s.chain.getProductionReport()
            expected = int(r["num_expected_chunks"])
            produced = int(r["num_produced_chunks"])
            if produced / expected < self.THRESHOLD_RATIO:
                return self.notify(
                    f"produced only {produced} / {expected} chunks {Emoji.BlockMiss}",
                    level=NotificationLevel.Warning,
                )
        except:
            return False
        return False


class TaskNearCheckProposal(Task):
    def __init__(self, services):
        super().__init__(
            "TaskNearCheckProposal",
            services,
            checkEvery=seconds(services.chain.EPOCHTIME),
            notifyEvery=seconds(services.chain.EPOCHTIME / 2),
        )
        self.prev_epoch = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        if self.prev_epoch is None:
            self.prev_epoch = self.s.chain.getEpoch()
        elif self.prev_epoch != self.s.chain.getEpoch():
            self.prev_epoch = self.s.chain.getEpoch()
            p = self.s.chain.getProposal()
            if len(p) == 0:
                return self.notify(
                    f"failed to send proposal {Emoji.Health}",
                    level=NotificationLevel.Warning,
                )
            elif "Declined" in p:
                return self.notify(
                    f"proposal has been rejected {Emoji.LowBal}",
                    level=NotificationLevel.Warning,
                )
        return False


class TaskNearCheckKicked(Task):
    def __init__(self, services, checkEvery=minutes(1)):
        super().__init__(
            "TaskNearCheckKicked",
            services,
            checkEvery=checkEvery,
            notifyEvery=seconds(services.chain.EPOCHTIME / 3),
        )
        self.prev_epoch = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):  # noqa: C901
        kicked_set = self.s.chain.getKickedout()
        pool_id = self.s.chain.getPoolId()
        if self.prev_epoch is None:
            self.prev_epoch = self.s.chain.getEpoch()
        elif self.prev_epoch != self.s.chain.getEpoch():
            self.prev_epoch = self.s.chain.getEpoch()
            for v in kicked_set:
                if v["account_id"] == pool_id:
                    reason = v["reason"]
                    if "NotEnoughChunks" in reason:
                        produced = reason["NotEnoughChunks"]["produced"]
                        expected = reason["NotEnoughChunks"]["expected"]
                        return self.notify(
                            "kicked out for not producing enough chunks, produced only "
                            + f"{produced} / {expected} chunks {Emoji.BlockMiss}",
                            level=NotificationLevel.Error,
                        )
                    elif "NotEnoughBlocks" in reason:
                        produced = reason["NotEnoughBlocks"]["produced"]
                        expected = reason["NotEnoughBlocks"]["expected"]
                        return self.notify(
                            "kicked out for not producing enough blocks, produced only "
                            + f"{produced} / {expected} blocks {Emoji.BlockMiss}",
                            level=NotificationLevel.Error,
                        )
                    elif "NotEnoughStake" in reason:
                        stake = int(reason["NotEnoughStake"]["stake_u128"][:-24])
                        threshold = int(
                            reason["NotEnoughStake"]["threshold_u128"][:-24]
                        )
                        missing = threshold - stake
                        return self.notify(
                            f"kicked out, missing {missing} Near to stake threshold {Emoji.LowBal}",
                            level=NotificationLevel.Error,
                        )
                    elif "Slashed" in reason:
                        return self.notify(
                            f"kicked out: slashed  {Emoji.Health}",
                            level=NotificationLevel.Error,
                        )
                    elif "Unstaked" in reason:
                        return self.notify(
                            f"kicked out: unstaked {Emoji.ActStake}",
                            level=NotificationLevel.Error,
                        )
                    elif "DidNotGetASeat" in reason:
                        return self.notify(
                            f"kicked out: sufficient stake but failed to get a seat {Emoji.Health}",
                            level=NotificationLevel.Error,
                        )
        return False


class Near(Chain):
    TYPE = "near"
    NAME = ""
    BLOCKTIME = 1.5
    EP = "http://localhost:3030/"
    EPOCHTIME = ""
    CUSTOM_TASKS = [
        TaskNearBlockMissed,
        TaskNearChunksMissed,
        TaskNearCheckProposal,
        TaskNearCheckKicked,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        self.EPOCHTIME = (
            int(
                super().rpcCall("EXPERIMENTAL_protocol_config", {"finality": "final"})[
                    "epoch_length"
                ]
            )
            * self.BLOCKTIME
        )

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
        return int(self.rpcCall("status")["sync_info"]["latest_block_height"])

    def isSynching(self):
        return self.rpcCall("status")["sync_info"]["syncing"]

    def getVersion(self):
        return self.rpcCall("status")["version"]["build"]

    def getPoolId(self):
        return self.rpcCall("status")["validator_account_id"]

    def getProductionReport(self):
        validators = self.rpcCall("validators", [None])["current_validators"]
        for v in validators:
            if v["account_id"] == self.getPoolId():
                return v
        raise Exception("Node is not in the current validators!")

    def getEpoch(self):
        return self.rpcCall("block", {"finality": "final"})["header"]["epoch_id"]

    def getProposal(self):
        return Bash(f"near proposals | grep {self.getPoolId()}").value()

    def getKickedout(self):
        return self.rpcCall("validators", [None])["prev_epoch_kickout"]

    def getKickOutThresholds(self):
        block = (
            int(
                self.rpcCall("EXPERIMENTAL_protocol_config", {"finality": "final"})[
                    "block_producer_kickout_threshold"
                ]
            )
            / 100
        )
        chunk = (
            int(
                self.rpcCall("EXPERIMENTAL_protocol_config", {"finality": "final"})[
                    "chunk_producer_kickout_threshold"
                ]
            )
            / 100
        )
        return block, chunk
