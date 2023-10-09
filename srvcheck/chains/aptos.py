import json
import re

import requests

from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes
from ..utils import Bash, ConfItem, ConfSet
from .chain import Chain

ConfSet.addItem(ConfItem("chain.validatorAddress", description="Validator address"))


class TaskAptosHealthError(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskAptosHealthError", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        try:
            self.s.chain.getHealth()
            return False
        except Exception:
            return self.notify(f"health error! {Emoji.Health}", NotificationLevel.Error)


class TaskAptosValidatorPerformanceCheck(Task):
    def __init__(self, services):
        super().__init__(
            "TaskAptosValidatorPerformanceCheck",
            services,
            checkEvery=minutes(30),
            notifyEvery=hours(1),
        )
        self.prevEp = None

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prevEp is None:
            self.prevEp = ep

        if self.prevEp != ep:
            self.prevEp = ep
            performance = self.s.chain.getValidatorPerformance()
            thisEpoch = list(
                filter(lambda item: item, performance[1].replace("|", "").split(" "))
            )
            lastEpoch = list(
                filter(lambda item: item, performance[0].replace("|", "").split(" "))
            )
            activeStakeOut = (
                "active stake increased"
                if int(thisEpoch[7]) > int(lastEpoch[7])
                else "active stake remained the same"
            )
            stakeEmoji = (
                Emoji.ActStake
                if int(thisEpoch[7]) > int(lastEpoch[7])
                else Emoji.LowBal
            )
            activeStakeOut += f", {thisEpoch[7]} active stake {stakeEmoji}"
            print(
                f"#Debug TaskAptosValidatorPerformanceCheck: {ep}, {lastEpoch[0]} new "
                + f"proposals {lastEpoch[3]} out of {lastEpoch[0]}, {thisEpoch[7]}"
            )
            if int(lastEpoch[0]) == 0:
                return self.notify(
                    f"is not proposing new consensus {Emoji.BlockMiss}\n{activeStakeOut}",
                    level=NotificationLevel.Error,
                )
            elif int(lastEpoch[3]) / int(lastEpoch[0]) < 0.25:
                return self.notify(
                    f"{int(lastEpoch[3])/int(lastEpoch[0]) * 100:.2f}% of proposals failed "
                    + f"{Emoji.BlockMiss}\n{activeStakeOut}",
                    level=NotificationLevel.Error,
                )
            else:
                successPercentage = int(lastEpoch[3]) / int(lastEpoch[0]) * 100
                return self.notify(
                    f"proposed {lastEpoch[0]} new consensus, {successPercentage:.2f}% succeed "
                    + f"{Emoji.BlockProd}\n{activeStakeOut}",
                    level=NotificationLevel.Info,
                )
        return False


class TaskAptosCurrentConsensusStuck(Task):
    def __init__(self, services):
        super().__init__(
            "TaskAptosCurrentConsensusStuck",
            services,
            checkEvery=minutes(5),
            notifyEvery=hours(1),
        )
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        cur_round = self.s.chain.getCurrentConsensus()

        print(f"#Debug TaskAptosCurrentConsensusStuck: {self.prev}, {cur_round}")
        if self.prev is None:
            self.prev = cur_round
            return False
        if cur_round == self.prev:
            return self.notify(
                f"consensus round stuck {Emoji.BlockMiss}", NotificationLevel.Error
            )

        self.prev = cur_round
        return False


class TaskAptosConnectedToFullNodeCheck(Task):
    def __init__(self, services):
        super().__init__(
            "TaskAptosConnectedToFullNodeCheck",
            services,
            checkEvery=minutes(5),
            notifyEvery=hours(1),
        )

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        conn = self.s.chain.getConnections()

        print(f"#Debug TaskAptosConnectedToFullNodeCheck: {conn}")
        if len(conn) > 0:
            vfn_in = conn[1].split(" ")[-1]
            if vfn_in == "0":
                return self.notify(
                    f"not connected to full node {Emoji.NoLeader}",
                    NotificationLevel.Error,
                )

        return False


class TaskAptosConnectedToAptosNodeCheck(Task):
    def __init__(self, services):
        super().__init__(
            "TaskAptosConnectedToAptosNodeCheck",
            services,
            checkEvery=minutes(5),
            notifyEvery=hours(1),
        )

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        peerId = "f326fd30"

        print(
            f"#Debug TaskAptosConnectedToAptosNodeCheck: {self.s.chain.isConnectedToPeer(peerId)}"
        )
        if self.s.chain.isConnectedToPeer(peerId) is False:
            return self.notify(
                f"not connected to Aptos node {Emoji.Peers}", NotificationLevel.Error
            )

        return False


class TaskAptosStateSyncCheck(Task):
    def __init__(self, services):
        super().__init__(
            "TaskAptosStateSyncCheck",
            services,
            checkEvery=minutes(5),
            notifyEvery=hours(1),
        )
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        sync = int(self.s.chain.getAptosStateSyncVersion()[0].split(" ")[-1])

        print(f"#Debug TaskAptosStateSyncCheck: {sync}, {self.prev}")
        if self.prev is None:
            self.prev = sync
        elif sync == self.prev:
            return self.notify(
                f"is not state synching {Emoji.Stuck}", NotificationLevel.Error
            )

        self.prev = sync
        return False


class Aptos(Chain):
    TYPE = "aptos"
    NAME = "aptos"
    BLOCKTIME = 15
    EP = "http://localhost:8080/v1"
    EP_METRICS = "http://localhost:9101/metrics"
    CUSTOM_TASKS = [
        TaskAptosHealthError,
        TaskAptosStateSyncCheck,
        TaskAptosValidatorPerformanceCheck,
        TaskAptosCurrentConsensusStuck,
        TaskAptosConnectedToFullNodeCheck,
        TaskAptosConnectedToAptosNodeCheck,
    ]

    @staticmethod
    def detect(conf):
        try:
            return Aptos(conf).getHealth()
        except:
            return False

    def getLatestVersion(self):
        raise Exception("Abstract getLatestVersion()")

    def getVersion(self):
        raise Exception("Abstract getVersion()")

    def getHealth(self):
        out = requests.get(f"{self.EP}/-/healthy")
        health = json.loads(out.text)["message"]
        return True if health == "aptos-node:ok" else False

    def getHeight(self):
        out = requests.get(self.EP)
        return json.loads(out.text)["block_height"]

    def getEpoch(self):
        out = requests.get(self.EP)
        return json.loads(out.text)["epoch"]

    def getBlockHash(self):
        raise Exception("Abstract getBlockHash()")

    def getPeerCount(self):
        conn = self.getConnections()
        if self.isValidator():
            if len(conn) > 1:
                in_peer = int(conn[0].split(" ")[-1])
                out_peer = int(conn[2].split(" ")[-1])
                return in_peer + out_peer
            return 0
        raise Exception("Abstract getPeerCount()")

    def getAptosStateSyncVersion(self):
        out = requests.get(self.EP_METRICS).text.split("\n")
        state_sync = [
            s for s in out if "aptos_state_sync_version" in s and "synced" in s
        ]
        return state_sync

    def getNetwork(self):
        raise Exception("Abstract getNetwork()")

    def getRole(self):
        out = requests.get(self.EP)
        return json.loads(out.text)["node_role"]

    def getConnections(self):
        out = requests.get(self.EP_METRICS).text.split("\n")
        connections = [s for s in out if "aptos_connections" in s and "#" not in s]
        return connections

    def isConnectedToPeer(self, peerId):
        out = requests.get(self.EP_METRICS).text.split("\n")
        conn = [s for s in out if "aptos_network_peer_connected" in s and peerId in s]
        if len(conn) > 0:
            return True
        return False

    def isStaking(self):
        raise Exception("Abstract isStaking()")

    def isValidator(self):
        role = self.getRole()
        return True if role == "validator" else False

    def isSynching(self):
        out = requests.get(self.EP_METRICS).text.split("\n")
        sync_status = [s for s in out if 'aptos_state_sync_version{type="synced"}' in s]
        return True if len(sync_status) == 0 else False

    def getCurrentConsensus(self):
        out = requests.get(self.EP_METRICS)
        cur_round = (
            re.findall("aptos_consensus_current_round [0-9]+", out.text)[0]
            .split(" ")[1]
            .replace('"', "")
        )
        return cur_round

    def getValidatorPerformance(self):
        validatorAddress = self.conf.getOrDefault("chain.validatorAddress")
        if validatorAddress[:2] == "0x":
            validatorAddress = validatorAddress[2:]
        performance = (
            Bash(
                "aptos node analyze-validator-performance --analyze-mode=detailed-epoch-table "
                + f"--url=https://ait3.aptosdev.com/ | grep {validatorAddress}"
            )
            .value()
            .split("\n")
        )
        return performance
