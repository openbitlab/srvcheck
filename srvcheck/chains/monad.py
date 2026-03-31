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

import json
import subprocess
import time as _time

from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes
from ..utils import ConfItem, ConfSet
from .chain import Chain

ConfSet.addItem(
    ConfItem(
        "monad.ledgerTailService",
        "monad-ledger-tail",
        str,
        "systemd service name for monad-ledger-tail",
    )
)
ConfSet.addItem(
    ConfItem(
        "monad.timeoutThreshold",
        5,
        int,
        "number of consecutive timeouts before alerting",
    )
)
ConfSet.addItem(
    ConfItem(
        "monad.finalizationLagThreshold",
        5000,
        int,
        "finalization lag threshold in milliseconds before alerting",
    )
)


def readLedgerTailLogs(service, since="5m ago"):
    try:
        result = subprocess.run(
            ["journalctl", "-u", service, "--no-pager", "-o", "json", "--since", since],
            capture_output=True,
            text=True,
            timeout=30,
        )
        lines = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    lines.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return lines
    except Exception:
        return []


def parseLedgerTailLogs(logs):
    events = []
    for entry in logs:
        msg = entry.get("MESSAGE", "")
        try:
            data = json.loads(msg)
        except (json.JSONDecodeError, TypeError):
            continue
        fields = data.get("fields", {})
        event_type = fields.get("message", "")
        if event_type in ("timeout", "finalized_block", "proposed_block"):
            events.append(fields)
    return events


class TaskMonadTimeoutDetection(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(1)):
        super().__init__(
            "TaskMonadTimeoutDetection", services, checkEvery, notifyEvery
        )
        self.timeoutCount = 0
        self.lastTimeoutRound = None
        self.seenEvents = {}

    @staticmethod
    def isPluggable(services):
        return services.conf.getOrDefault("chain.validatorAddress") is not None

    def _dedupe(self, event_type, round_num):
        """Returns True if event should be processed, False if already seen."""
        key = f"{event_type}:{round_num}"
        now = _time.time()
        if key in self.seenEvents and self.seenEvents[key] > now:
            return False
        self.seenEvents[key] = now + 120
        # Cleanup expired entries
        if len(self.seenEvents) > 4000:
            self.seenEvents = {
                k: v for k, v in self.seenEvents.items() if v > now
            }
        return True

    def run(self):
        service = self.s.conf.getOrDefault("monad.ledgerTailService")
        events = parseLedgerTailLogs(readLedgerTailLogs(service))
        if not events:
            return False

        validator_addr = self.s.conf.getOrDefault("chain.validatorAddress")
        if not validator_addr:
            return False
        validator_norm = validator_addr.lower().removeprefix("0x")
        threshold = self.s.conf.getOrDefault("monad.timeoutThreshold")

        for fields in events:
            event_type = fields.get("message", "")
            author = fields.get("author", fields.get("validator", ""))
            round_num = fields.get("round", fields.get("height",
                                   fields.get("round_number")))

            if not self._dedupe(event_type, round_num):
                continue

            author_norm = author.lower().removeprefix("0x") if author else ""

            if event_type == "timeout":
                if round_num == self.lastTimeoutRound:
                    continue
                self.lastTimeoutRound = round_num

                if author_norm == validator_norm:
                    self.timeoutCount += 1
                    level = NotificationLevel.Warning \
                        if self.timeoutCount >= threshold \
                        else NotificationLevel.Info
                    self.notify(
                        f"timeout detected (#{self.timeoutCount}/{threshold}) "
                        f"round {round_num} {Emoji.BlockMiss}",
                        noCheck=True,
                        level=level,
                    )

            elif event_type == "finalized_block":
                if author_norm == validator_norm and self.timeoutCount > 0:
                    self.notify(
                        f"recovered on round {round_num}, "
                        f"previous timeout streak: "
                        f"{self.timeoutCount} {Emoji.SyncOk}",
                        noCheck=True,
                        level=NotificationLevel.Info,
                    )
                    self.timeoutCount = 0

        return False


class TaskMonadBlockProductionReport(Task):
    def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(1)):
        super().__init__(
            "TaskMonadBlockProductionReport", services, checkEvery, notifyEvery
        )
        self.currentEpoch = None
        self.reportedEpoch = None
        self.lastRound = None
        self.produced = 0
        self.totalBlocks = 0
        self.authors = set()

    @staticmethod
    def isPluggable(services):
        return services.conf.getOrDefault("chain.validatorAddress") is not None

    def _report(self, name):
        num_validators = len(self.authors) if self.authors else 1
        expected = self.totalBlocks / num_validators
        missed = max(0, round(expected) - self.produced)

        self.s.persistent.timedAdd(
            f"{name}_blocksProduced", self.produced)
        self.s.persistent.timedAdd(
            f"{name}_blocksExpected", round(expected))
        self.s.persistent.timedAdd(
            f"{name}_blocksMissed", missed)

        self.notify(
            f"epoch {self.currentEpoch} ended: "
            f"produced {self.produced}, "
            f"expected {round(expected)}, "
            f"missed {missed} {Emoji.BlockProd}",
            noCheck=True,
            level=NotificationLevel.Info,
        )

        self.reportedEpoch = self.currentEpoch

    def run(self):
        service = self.s.conf.getOrDefault("monad.ledgerTailService")
        events = parseLedgerTailLogs(readLedgerTailLogs(service, since="15m ago"))
        if not events:
            return False

        validator_addr = self.s.conf.getOrDefault("chain.validatorAddress")
        name = self.s.conf.getOrDefault("chain.name")

        for fields in events:
            event_type = fields.get("message", "")
            epoch = fields.get("epoch")
            round_num = fields.get("round")

            # Skip already processed events
            if self.lastRound is not None and round_num is not None \
                    and int(round_num) <= self.lastRound:
                continue

            if self.currentEpoch is None:
                self.currentEpoch = epoch

            if epoch != self.currentEpoch:
                if self.currentEpoch != self.reportedEpoch:
                    self._report(name)

                self.produced = 0
                self.totalBlocks = 0
                self.authors = set()
                self.currentEpoch = epoch

            if event_type == "proposed_block":
                author = fields.get("author", "")
                self.totalBlocks += 1
                if author:
                    self.authors.add(author.lower())
                if (
                    author
                    and validator_addr
                    and author.lower() == validator_addr.lower()
                ):
                    self.produced += 1

            if round_num is not None:
                self.lastRound = int(round_num)

        return False


class TaskMonadFinalizationLag(Task):
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(10)):
        super().__init__("TaskMonadFinalizationLag", services, checkEvery, notifyEvery)
        self.wasLagging = False

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        service = self.s.conf.getOrDefault("monad.ledgerTailService")
        events = parseLedgerTailLogs(readLedgerTailLogs(service))
        if not events:
            return False

        threshold = self.s.conf.getOrDefault("monad.finalizationLagThreshold")
        max_lag = 0

        for fields in events:
            if fields.get("message") != "finalized_block":
                continue
            try:
                block_ts = int(fields["block_ts_ms"])
                now_ts = int(fields["now_ts_ms"])
                lag = now_ts - block_ts
                if lag > max_lag:
                    max_lag = lag
            except (KeyError, ValueError, TypeError):
                continue

        if max_lag >= threshold:
            self.wasLagging = True
            return self.notify(
                f"finalization lag is high: {max_lag}ms {Emoji.Slow}",
                level=NotificationLevel.Warning,
            )

        if self.wasLagging:
            self.wasLagging = False
            return self.notify(
                f"finalization lag recovered: {max_lag}ms {Emoji.SyncOk}",
                level=NotificationLevel.Info,
            )

        return False


class Monad(Chain):
    TYPE = "monad"
    NAME = "monad"
    BLOCKTIME = 1
    EP = "http://localhost:8080/"
    CUSTOM_TASKS = [
        TaskMonadTimeoutDetection,
        TaskMonadBlockProductionReport,
        TaskMonadFinalizationLag,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        disabled = conf.getOrDefault("tasks.disabled") or ""
        if "TaskChainLowPeer" not in disabled:
            extra = "TaskChainLowPeer" if not disabled else ",TaskChainLowPeer"
            ConfSet.setDefaultValue("tasks.disabled", disabled + extra)

    @staticmethod
    def detect(conf):
        try:
            version = Monad(conf).getVersion()
            return "monad" in version.lower()
        except Exception:
            return False

    def getVersion(self):
        return self.rpcCall("web3_clientVersion")

    def getHeight(self):
        return int(self.rpcCall("eth_blockNumber"), 16)

    def getBlockHash(self):
        block = self.rpcCall("eth_getBlockByNumber", ["latest", False])
        return block["hash"]

    def getPeerCount(self):
        raise Exception("net_peerCount not supported by Monad RPC")

    def getNetwork(self):
        chain_id = self.rpcCall("eth_chainId")
        return f"monad-{int(chain_id, 16)}"

    def isStaking(self):
        addr = self.conf.getOrDefault("chain.validatorAddress")
        if addr is None:
            return False
        return True

    def isSynching(self):
        result = self.rpcCall("eth_syncing")
        return result is not False and result is not None
