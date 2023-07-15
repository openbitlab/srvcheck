import configparser
import json
import re

from dateutil import parser

from ..notification import Emoji
from ..tasks import Task, hours, minutes, seconds
from ..utils import Bash, ConfItem, ConfSet
from .chain import Chain

ConfSet.addItem(ConfItem("chain.activeSet", description="active set of validators"))
ConfSet.addItem(ConfItem("chain.blockWindow", 100, int))
ConfSet.addItem(ConfItem("chain.thresholdNotsigned", 5, int))


class TaskTendermintBlockMissed(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(5)):
        self.BLOCK_WINDOW = services.conf.getOrDefault("chain.blockWindow")
        average_block_time = services.chain.getAverageBlockTime()

        super().__init__(
            "TaskTendermintBlockMissed",
            services,
            checkEvery=seconds(average_block_time * self.BLOCK_WINDOW),
            notifyEvery=notifyEvery,
        )

        self.THRESHOLD_NOTSIGNED = self.s.conf.getOrDefault("chain.thresholdNotsigned")
        self.prev = None
        self.prevMissed = None

    @staticmethod
    def isPluggable(services):
        return services.chain.isStaking()

    def run(self):
        nblockh = self.s.chain.getHeight()

        if self.prev is None:
            self.prev = nblockh - self.BLOCK_WINDOW

        validatorAddress = self.s.chain.getValidatorAddress()
        missed = 0
        start = self.prev
        while start < nblockh:
            if not next(
                (
                    x
                    for x in self.s.chain.getSignatures(start)
                    if x["validator_address"] == validatorAddress
                ),
                None,
            ):
                lastMissed = start
                missed += 1

            start += 1

        if missed >= self.THRESHOLD_NOTSIGNED and (
            self.prevMissed is None or self.prevMissed != lastMissed
        ):
            self.prevMissed = lastMissed
            self.prev = nblockh
            return self.notify(
                f"{missed} not signed blocks in the latest {self.BLOCK_WINDOW} {Emoji.BlockMiss}"
            )

        return False


class TaskTendermintNewProposal(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=hours(1)):
        super().__init__("TaskTendermintNewProposal", services, checkEvery, notifyEvery)
        self.prev = None
        self.admin_gov = self.s.conf.getOrDefault("tasks.govAdmin")

    @staticmethod
    def isPluggable(services):
        return True

    def getProposalTitle(self, proposal):
        if "id" in proposal:
            return proposal["messages"][0]["content"]["title"]
        elif "proposal_id" in proposal:
            return proposal["content"]["title"]

    def notifyAboutLatestProposals(self, proposals, key):
        nProposalUnread = [
            prop for prop in proposals if int(self.prev[0][key]) < int(prop[key])
        ]
        c = len(nProposalUnread)
        if c > 0:
            out = f"got {c} new proposal: "
            for i, p in enumerate(nProposalUnread):
                if i > 0 and i < len(nProposalUnread):
                    out += "\n"
                out += f"{self.getProposalTitle(p)}"
                out += (
                    f'{" " + Emoji.Proposal if i == len(nProposalUnread) - 1 else ""}'
                )
            self.prev = proposals
            if self.admin_gov:
                out += f" {self.admin_gov}"
            return self.notify(out)

    def run(self):
        nProposal = self.s.chain.getLatestProposals()
        if not self.prev:
            self.prev = nProposal
            if len(self.prev) > 0:
                return self.notify(
                    f"got latest proposal: {self.getProposalTitle(nProposal[0])} {Emoji.Proposal}"
                )
        elif "id" in self.prev[0]:
            self.notifyAboutLatestProposals(nProposal, "id")
        elif "proposal_id" in self.prev[0] and int(self.prev[0]["proposal_id"]) < int(
            nProposal[0]["proposal_id"]
        ):
            self.notifyAboutLatestProposals(nProposal, "proposal_id")
        return False


class TaskTendermintPositionChanged(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__(
            "TaskTendermintPositionChanged", services, checkEvery, notifyEvery
        )
        self.ACTIVE_SET = self.s.conf.getOrDefault("chain.activeSet")
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        npos = self.getValidatorPosition()

        if not self.prev:
            self.prev = npos

        if not self.s.chain.isStaking():
            return self.notify(f"out from the active set {Emoji.NoLeader}")

        if npos != self.prev:
            prev = self.prev
            self.prev = npos

            if npos > prev:
                return self.notify(
                    f"position decreased from {prev} to {npos} {Emoji.PosDown}"
                )
            else:
                return self.notify(
                    f"position increased from {prev} to {npos} {Emoji.PosUp}"
                )

        return False

    def getValidatorPosition(self):
        bh = str(self.s.chain.getHeight())
        active_vals = []
        if self.ACTIVE_SET is None:
            active_s = int(self.s.chain.rpcCall("validators", [bh, "1", "1"])["total"])
        else:
            active_s = int(self.ACTIVE_SET)
        if active_s > 100:
            it = active_s // 100
            diff = active_s
            for i in range(it):
                active_vals += self.s.chain.rpcCall(
                    "validators", [bh, str(i + 1), "100"]
                )["validators"]
                diff -= 100
            if diff > 0:
                active_vals += self.s.chain.rpcCall(
                    "validators", [bh, str(i + 2), "100"]
                )["validators"]
        else:
            active_vals += self.s.chain.rpcCall("validators", [bh, "1", str(active_s)])[
                "validators"
            ]
        p = [
            i
            for i, j in enumerate(active_vals)
            if j["address"] == self.s.chain.getValidatorAddress()
        ]
        return p[0] + 1 if len(p) > 0 else -1


class TaskTendermintHealthError(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskTendermintHealthError", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        try:
            self.s.chain.getHealth()
            return False
        except:
            return self.notify(f"health error! {Emoji.Health}")


class Tendermint(Chain):
    TYPE = "tendermint"
    NAME = ""
    BLOCKTIME = 60
    EP = "http://localhost:26657/"
    CUSTOM_TASKS = [
        TaskTendermintBlockMissed,
        TaskTendermintPositionChanged,
        TaskTendermintHealthError,
        TaskTendermintNewProposal,
    ]

    @staticmethod
    def detect(conf):
        try:
            Tendermint(conf).getVersion()
            return True
        except:
            return False

    def getHealth(self):
        return self.rpcCall("health")

    def getVersion(self):
        return self.rpcCall("abci_info")

    def getLocalVersion(self):
        try:
            return self.getVersion()["response"]["version"]
        except Exception as e:
            ver = self.conf.getOrDefault("chain.localVersion")
            if ver is None:
                raise Exception("No local version of the software specified!") from e
            return ver

    def getHeight(self):
        return int(self.rpcCall("abci_info")["response"]["last_block_height"])

    def getBlockHash(self):
        return self.rpcCall("status")["sync_info"]["latest_block_hash"]

    def getAverageBlockTime(self):
        span = 1000
        current_height = self.getHeight()
        current_block_time = parser.parse(
            self.rpcCall("block", [str(current_height)])["block"]["header"]["time"]
        )
        past_block_time = parser.parse(
            self.rpcCall("block", [str(current_height - span)])["block"]["header"][
                "time"
            ]
        )
        time_diff = (current_block_time - past_block_time).total_seconds()
        average_block_time = int(time_diff / span)
        return average_block_time if average_block_time > 0 else 1

    def getPeerCount(self):
        return int(self.rpcCall("net_info")["n_peers"])

    def getNetwork(self):
        raise Exception("Abstract getNetwork()")

    def isStaking(self):
        return (
            True
            if int(self.rpcCall("status")["validator_info"]["voting_power"]) > 0
            else False
        )

    def getValidatorAddress(self):
        return self.rpcCall("status")["validator_info"]["address"]

    def getSignatures(self, height):
        return self.rpcCall("block", [str(height)])["block"]["last_commit"][
            "signatures"
        ]

    def isSynching(self):
        return self.rpcCall("status")["sync_info"]["catching_up"]

    def getLatestProposals(self):
        serv = self.conf.getOrDefault("chain.service")
        if serv:
            c = configparser.ConfigParser()
            c.read(f"/etc/systemd/system/{serv}")
            cmd = re.split(" ", c["Service"]["ExecStart"])[0]
            proposals = json.loads(
                Bash(cmd + " q gov proposals --reverse --output json").value()
            )["proposals"]
            return [
                p for p in proposals if p["status"] == "PROPOSAL_STATUS_VOTING_PERIOD"
            ]
        raise Exception("No service file name specified!")
