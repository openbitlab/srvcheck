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

from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes
from ..utils import ConfItem, ConfSet
from .chain import Chain

ConfSet.addItem(
    ConfItem("monad.ledgerTailService", "monad-ledger-tail", str,
             "systemd service name for monad-ledger-tail")
)
ConfSet.addItem(
    ConfItem("monad.timeoutThreshold", 5, int,
             "number of consecutive timeouts before alerting")
)


class TaskMonadValidatorBalance(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(1)):
        super().__init__(
            "TaskMonadValidatorBalance", services, checkEvery, notifyEvery
        )
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return services.conf.getOrDefault("chain.validatorAddress") is not None

    def run(self):
        try:
            addr = self.s.conf.getOrDefault("chain.validatorAddress")
            balance = self.s.chain.getValidatorBalance(addr)
            if self.prev is not None and balance < self.prev:
                return self.notify(
                    f"validator balance decreased: {balance:.4f} MON {Emoji.LowBal}",
                    level=NotificationLevel.Warning,
                )
            self.prev = balance
        except Exception:
            pass
        return False


class TaskMonadBlockSigning(Task):
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(10)):
        super().__init__(
            "TaskMonadBlockSigning", services, checkEvery, notifyEvery
        )
        self.consecutiveTimeouts = 0
        self.lastRound = None

    @staticmethod
    def isPluggable(services):
        return services.conf.getOrDefault("chain.validatorAddress") is not None

    def _readLedgerTailLogs(self, since="5m ago"):
        service = self.s.conf.getOrDefault("monad.ledgerTailService")
        try:
            result = subprocess.run(
                ["journalctl", "-u", service, "--no-pager", "-o", "json",
                 "--since", since],
                capture_output=True, text=True, timeout=30,
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

    def run(self):
        logs = self._readLedgerTailLogs()
        if not logs:
            return False

        validator_addr = self.s.conf.getOrDefault("chain.validatorAddress")
        threshold = self.s.conf.getOrDefault("monad.timeoutThreshold")
        timeouts = 0
        recovered = False

        for entry in logs:
            msg = entry.get("MESSAGE", "")
            try:
                data = json.loads(msg)
            except (json.JSONDecodeError, TypeError):
                continue

            event_type = data.get("message", "")
            author = data.get("author_address", data.get("author", ""))

            if event_type == "timeout":
                round_num = data.get("round", data.get("round_number"))
                if round_num != self.lastRound:
                    timeouts += 1
                    self.lastRound = round_num

            elif event_type in ("finalized_block", "proposed_block"):
                if author and validator_addr and \
                        author.lower() == validator_addr.lower():
                    if self.consecutiveTimeouts > 0:
                        recovered = True
                    timeouts = 0

        self.consecutiveTimeouts += timeouts

        if recovered:
            self.consecutiveTimeouts = 0
            return self.notify(
                f"validator recovered after timeouts {Emoji.SyncOk}",
                level=NotificationLevel.Info,
            )

        if self.consecutiveTimeouts >= threshold:
            count = self.consecutiveTimeouts
            return self.notify(
                f"validator missed {count} rounds (timeout) {Emoji.BlockMiss}",
                level=NotificationLevel.Warning,
            )

        return False


class Monad(Chain):
    TYPE = "monad"
    NAME = "monad"
    BLOCKTIME = 1
    EP = "http://localhost:4317/"
    CUSTOM_TASKS = [
        TaskMonadValidatorBalance,
        TaskMonadBlockSigning,
    ]

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
        return int(self.rpcCall("net_peerCount"), 16)

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

    def getValidatorBalance(self, address):
        result = self.rpcCall("eth_getBalance", [address, "latest"])
        return int(result, 16) / 1e18
