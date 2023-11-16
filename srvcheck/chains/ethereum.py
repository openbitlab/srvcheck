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

import json
import requests

from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours
from ..utils import ConfItem, ConfSet
from .chain import Chain

ConfSet.addItem(ConfItem("chain.validatorAddress", description="Validators indexes"))
ConfSet.addItem(ConfItem("chain.beaconEndpoint", description="Consensus client endpoint"))


class TaskEthereumHealthError(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskEthereumHealthError", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        try:
            self.s.chain.getHealth()
            return False
        except Exception:
            return self.notify(f"beacon node health error! {Emoji.Health}", NotificationLevel.Error)


class TaskEthereumLowPeerError(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskEthereumLowPeerError", services, checkEvery, notifyEvery)
        self.minPeers = 3

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        p = self.s.chain.getBeaconNodePeerCount()

        if p == 0:
            return self.notify(
                f"beacon node has 0 peers {Emoji.Peers}",
                level=NotificationLevel.Error,
            )
        elif p < self.minPeers:
            return self.notify(
                f"beacon node has only {p} peers {Emoji.Peers}",
                level=NotificationLevel.Warning,
            )

        return False


class TaskEthereumAttestationsCheck(Task):
    pass


class TaskEthereumBlockProductionCheck(Task):
    pass


class TaskValidatorBalanceCheck(Task):
    def __init__(self, services, checkEvery=hours(24), notifyEvery=hours(24)):
        super().__init__("TaskValidatorBalanceCheck", services, checkEvery, notifyEvery)
        self.prev = {}

    @staticmethod
    def isPluggable(services):
        validatorsActive = [s for s in services.chain.isStaking() if s == "yes"]
        return services.conf.exists("chain.validatorAddress") and validatorsActive > 0

    def run(self):
        validatorIndexes = self.conf.getOrDefault("chain.validatorAddress")
        for i, index in enumerate(validatorIndexes.split(", ")):
            prevBalance = self.prev[str(index)]
            self.prev[str(index)] = self.s.chain.getValidatorRewards()

            out = f"validator index {index}:\n"
            out += f"balance: {self.prev[str(index)]} ETH\n"
            out += f"rewards in the latest 24hr: {self.prev[str(index)] - prevBalance} ETH "
            out += f"{Emoji.ActStake}"
            if len(validatorIndexes) - 1 > i:
                out += "\n\n"

        return self.notify(
            out,
            level=NotificationLevel.Info,
        )

class TaskValidatorBalanceChart(Task):
    pass


class Ethereum(Chain):
    TYPE = "ethereum"
    NAME = "ethereum"
    BLOCKTIME = 15
    EP = "http://localhost:8545/"         # execution client
    CC = "http://localhost:5052/eth/v1/"  # consensus client
    CUSTOM_TASKS = [
        TaskEthereumHealthError,
        TaskEthereumLowPeerError,
        TaskEthereumAttestationsCheck,
        TaskEthereumBlockProductionCheck,
        TaskValidatorBalanceCheck,
        TaskValidatorBalanceChart,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        if conf.exists("chain.beaconEndpoint"):
            self.CC = f"{conf.getOrDefault('chain.beaconEndpoint')}/eth/v1/"

    @staticmethod
    def detect(conf):
        try:
            return Ethereum(conf).getHeight() and Ethereum(conf).getSlot()
        except:
            return False

    def getLatestVersion(self):
        raise Exception("Abstract getLatestVersion()")

    def getVersion(self):
        out = requests.get(f"{self.CC}/node/version")
        return json.loads(out.text)["data"]["version"]

    def getHealth(self):
        status = requests.get(f"{self.CC}/node/health").status_code
        return status != 503 and status != 400

    def getHeight(self):
        return self.rpcCall("eth_blockNumber")

    def getSlot(self):
        out = requests.get(f"{self.CC}/beacon/headers")
        return json.loads(out.text)["data"][0]["header"]["message"]["slot"]

    def getEpoch(self):
        out = requests.get(f"{self.CC}/beacon/states/finalized/finality_checkpoints")
        return json.loads(out.text)["data"]["current_justified"]["epoch"]

    def getBlockHash(self):
        return self.rpcCall("eth_getBlockByNumber", ["latest", False])["hash"]

    def getNetwork(self):
        return self.rpcCall("net_version")

    def getPeerCount(self):
        return int(self.rpcCall("net_peerCount"), 16)

    def getBeaconNodePeerCount(self):
        out = requests.get(f"{self.CC}/node/peer_count")
        return int(json.loads(out.text)["data"]["connected"])
    
    def isStaking(self):
        validatorStatus = self.isValidator()
        return ["yes" if s == "active_ongoing" else "no" for s in validatorStatus]

    def isValidator(self):
        validatorIndexes = self.conf.getOrDefault("chain.validatorAddress")
        try:
            if validatorIndexes:
                s = []
                for index in validatorIndexes.split(", "):
                    out = requests.get(f"{self.CC}/beacon/states/head/validators/{index}")
                    s.append(json.loads(out.text)["data"]["status"])
                return s 
            else:
                return False
        except:
            return False

    def isSynching(self):
        out = requests.get(f"{self.CC}/node/syncing")
        return json.loads(out.text)["data"]["is_syncing"]
    
    def getWithdrawalCredentials(self, validatorIndex):
        out = requests.get(f"{self.CC}/beacon/states/head/validators/{validatorIndex}")
        return json.loads(out.text)["data"]["validator"]["withdrawal_credentials"]
    
    def getAddressBalance(self, address):
        balance = self.rpcCall("eth_getBalance", [address, "latest"])
        return int(balance) * 10 ** -18
    
    def getValidatorBalance(self, validatorIndex):
        out = requests.get(f"{self.CC}/beacon/states/head/validators/{validatorIndex}")
        return int(json.loads(out.text)["data"]["balance"]) * 10 ** -9

    def getValidatorRewards(self, validatorIndex):
        withdrawalCredentials = self.getWithdrawalCredentials(self, validatorIndex)
        if withdrawalCredentials[:4] == "0x01":
            withdrawalAddress = withdrawalCredentials[:2] + withdrawalCredentials[26:]
            return self.getAddressBalance(withdrawalAddress)
        return self.getValidatorBalance(validatorIndex)