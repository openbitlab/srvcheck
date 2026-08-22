# MIT License

# Copyright (c) 2021-2026 Openbitlab Team

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

import requests

from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes
from ..utils import ConfItem, ConfSet
from .chain import Chain, rpcCall

ConfSet.addItem(ConfItem("chain.validatorAddress", description="Validator address"))
ConfSet.addItem(
    ConfItem(
        "octra.minConsensusPeers",
        4,
        int,
        "minimum number of consensus peers before alerting",
    )
)
ConfSet.addItem(
    ConfItem(
        "octra.votingDisabledChecks",
        2,
        int,
        "consecutive checks with voting disabled before alerting",
    )
)

OCTRA_DEFAULT_REPO = "octra-labs/lite_node"
OCTRA_DECIMALS = 6
SYNC_LAG_THRESHOLD = 10


def shortCommit(commit):
    return commit[:8] if isinstance(commit, str) else str(commit)


class TaskOctraVotingStatus(Task):
    """Alerts when the validator stops voting (stat.sh `voting = disabled`).

    A short `voting = disabled` window right after a rejoin/update is normal, so
    the alert fires only after `octra.votingDisabledChecks` consecutive checks.
    """

    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(30)):
        super().__init__("TaskOctraVotingStatus", services, checkEvery, notifyEvery)
        self.disabledCount = 0
        self.alerted = False

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        voting, reason = self.s.chain.getVotingStatus()
        threshold = self.s.conf.getOrDefault("octra.votingDisabledChecks")

        if voting:
            if self.alerted:
                self.alerted = False
                self.disabledCount = 0
                return self.notify(
                    f"voting enabled again {Emoji.SyncOk}",
                    noCheck=True,
                    level=NotificationLevel.Info,
                )
            self.disabledCount = 0
            return False

        self.disabledCount += 1
        if self.disabledCount >= threshold:
            self.alerted = True
            reasonStr = f" (reason: {reason})" if reason else ""
            return self.notify(
                f"voting is disabled{reasonStr} since {self.disabledCount} checks {Emoji.NoLeader}",
                level=NotificationLevel.Error,
            )
        return False


class TaskOctraValidatorActive(Task):
    """Alerts when the validator is not in the active validator set."""

    def __init__(self, services, checkEvery=minutes(5), notifyEvery=hours(1)):
        super().__init__("TaskOctraValidatorActive", services, checkEvery, notifyEvery)
        self.wasInactive = False

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        membership = self.s.chain.getValidatorMembership()

        if membership["active"]:
            if self.wasInactive:
                self.wasInactive = False
                return self.notify(
                    f"validator is back in the active set {Emoji.SyncOk}",
                    noCheck=True,
                    level=NotificationLevel.Info,
                )
            return False

        self.wasInactive = True
        if membership["scheduled"]:
            return self.notify(
                "validator is not active yet, scheduled for activation at epoch "
                f"{membership['activateEpoch']} {Emoji.Slow}",
                level=NotificationLevel.Warning,
            )
        return self.notify(
            f"validator is not in the active set ({membership['setSize']} validators) "
            f"{Emoji.Delinq}",
            level=NotificationLevel.Error,
        )


class TaskOctraConsensusPeers(Task):
    """Alerts when the number of consensus peers is too low."""

    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(30)):
        super().__init__("TaskOctraConsensusPeers", services, checkEvery, notifyEvery)

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        peers = self.s.chain.getConsensusPeerCount()
        minPeers = self.s.conf.getOrDefault("octra.minConsensusPeers")

        if peers == 0:
            return self.notify(
                f"node has 0 consensus peers {Emoji.Peers}",
                level=NotificationLevel.Error,
            )
        if peers < minPeers:
            return self.notify(
                f"node has only {peers} consensus peers {Emoji.Peers}",
                level=NotificationLevel.Warning,
            )
        return False


class TaskOctraNewRelease(Task):
    """Compares the running `source_commit` with the upstream SOURCE_COMMIT file."""

    def __init__(self, services, checkEvery=minutes(30), notifyEvery=hours(6)):
        super().__init__("TaskOctraNewRelease", services, checkEvery, notifyEvery)

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        current = self.s.chain.getVersion()
        latest = self.s.chain.getLatestVersion()

        if current and latest and current != latest:
            return self.notify(
                f"has new release: {shortCommit(latest)} "
                f"(running {shortCommit(current)}) {Emoji.Rel}",
                level=NotificationLevel.Info,
            )
        return False


class TaskOctraBalanceReport(Task):
    """Daily report of validator balance (rewards accrue here) and consensus weight."""

    def __init__(self, services, checkEvery=hours(24), notifyEvery=hours(24)):
        super().__init__("TaskOctraBalanceReport", services, checkEvery, notifyEvery)
        self.prevBalance = None

    @staticmethod
    def isPluggable(services):
        return services.chain.isValidator()

    def run(self):
        balance = self.s.chain.getValidatorBalance()
        weight = self.s.chain.getValidatorWeight()

        out = f"balance: {balance:.6f} OCT"
        if self.prevBalance is not None:
            delta = balance - self.prevBalance
            sign = "+" if delta >= 0 else ""
            out += f" ({sign}{delta:.6f} since last report)"
        self.prevBalance = balance

        if weight is not None:
            out += f", weight: {weight:.6f}"

        return self.notify(f"{out} {Emoji.ActStake}", level=NotificationLevel.Info)


class Octra(Chain):
    TYPE = "octra"
    NAME = "octra"
    BLOCKTIME = 10
    EP = "http://127.0.0.1:8080"
    CUSTOM_TASKS = [
        TaskOctraVotingStatus,
        TaskOctraValidatorActive,
        TaskOctraConsensusPeers,
        TaskOctraNewRelease,
        TaskOctraBalanceReport,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        self.baseUrl = Octra.baseUrlFromConf(conf)
        self.EP = self.baseUrl + "/rpc"

        # The generic release check compares version strings, which is meaningless
        # for commit hashes: Octra has its own TaskOctraNewRelease.
        disabled = conf.getOrDefault("tasks.disabled") or ""
        if "tasks.disabled" in ConfSet.items and "TaskNewRelease" not in disabled:
            extra = "TaskNewRelease" if not disabled else ",TaskNewRelease"
            ConfSet.setDefaultValue("tasks.disabled", disabled + extra)

    @staticmethod
    def baseUrlFromConf(conf):
        base = (conf.getOrDefault("chain.endpoint") or Octra.EP).rstrip("/")
        if base.endswith("/rpc"):
            base = base[: -len("/rpc")]
        return base

    @staticmethod
    def detect(conf):
        try:
            url = Octra.baseUrlFromConf(conf) + "/rpc"
            return rpcCall(url, "octra_runtimeVersion").get("node") == "octra"
        except Exception:
            return False

    # Raw endpoints

    def getRuntimeVersion(self):
        return self.rpcCall("octra_runtimeVersion")

    def getStatus(self):
        return requests.get(
            self.baseUrl + "/status", headers={"Accept": "application/json"}, timeout=10
        ).json()

    def getConsensusPeerStates(self):
        return self.rpcCall("octra_consensusPeerStates")

    def getValidatorSetProof(self):
        return self.rpcCall("octra_validatorSetProof")

    def getAccount(self, address):
        return self.rpcCall("octra_account", [address, 1])

    # Chain interface

    def getVersion(self):
        return self.getRuntimeVersion()["source_commit"]

    def getLatestVersion(self):
        repo = self.conf.getOrDefault("chain.ghRepository") or OCTRA_DEFAULT_REPO
        r = requests.get(f"https://raw.githubusercontent.com/{repo}/main/SOURCE_COMMIT", timeout=30)
        r.raise_for_status()
        return r.text.strip()

    def getHeight(self):
        return int(self.getStatus()["head_epoch"])

    def getBlockHash(self):
        return self.getStatus()["state_root"]

    def getPeerCount(self):
        d = self.getConsensusPeerStates().get("p2p_diagnostics") or {}
        return int(d.get("connected", 0))

    def getNetwork(self):
        return self.getRuntimeVersion()["chain_id"]

    def isStaking(self):
        return self.getValidatorMembership()["active"]

    def isSynching(self):
        peers = self.getConsensusPeerStates()
        records = peers.get("peers") or []
        if not records:
            return False
        local = self.getHeight()
        network = max(int(p.get("head_epoch", 0)) for p in records)
        return (network - local) > SYNC_LAG_THRESHOLD

    # Octra specific

    def getValidatorAddress(self):
        addr = self.conf.getOrDefault("chain.validatorAddress")
        if addr:
            return addr
        try:
            return self.getRuntimeVersion().get("validator")
        except Exception:
            return None

    def isValidator(self):
        return self.getValidatorAddress() is not None

    def getVotingStatus(self):
        """Returns (voting: bool, reason: str | None)"""
        peers = self.getConsensusPeerStates()
        voting = peers.get("voting")
        return (bool(voting), peers.get("voting_reason"))

    def getConsensusPeerCount(self):
        return len(self.getConsensusPeerStates().get("peers") or [])

    def getValidatorMembership(self):
        proof = self.getValidatorSetProof()
        addr = self.getValidatorAddress()
        validators = proof.get("validators") or []
        active = any(v.get("address") == addr for v in validators)

        scheduled = False
        activateEpoch = None
        sched = proof.get("scheduled")
        if isinstance(sched, dict):
            scheduled = any(v.get("address") == addr for v in (sched.get("validators") or []))
            activateEpoch = sched.get("activate_epoch")

        return {
            "active": active,
            "scheduled": scheduled,
            "activateEpoch": activateEpoch,
            "setSize": len(validators),
        }

    def getValidatorWeight(self):
        """Consensus weight in OCT units (None if not in the active set)"""
        addr = self.getValidatorAddress()
        for v in self.getValidatorSetProof().get("validators") or []:
            if v.get("address") == addr:
                return int(v["weight"]) / 10**OCTRA_DECIMALS
        return None

    def getValidatorBalance(self):
        """Account balance in OCT"""
        acc = self.getAccount(self.getValidatorAddress())
        if "balance_raw" in acc:
            return int(acc["balance_raw"]) / 10**OCTRA_DECIMALS
        return float(acc["balance"])
