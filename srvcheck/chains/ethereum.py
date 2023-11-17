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
import struct

from binascii import unhexlify
from time import sleep
from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes
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
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=hours(1)):
        super().__init__("TaskEthereumAttestationsCheck", services, checkEvery, notifyEvery)
        self.prev = {}
        self.prevEpoch = None

    @staticmethod
    def isPluggable(services):
        c = services.chain.getValidatorActiveCount()
        return services.conf.exists("chain.validatorAddress") and c > 0
    
    def getAggregationBits(self, slot, committeeIndex):
        while True:
            attestations = self.s.chain.getSlotAttestations(slot)
            if attestations == "Not ready yet":
                sleep(60)
            else:
                break
        bitsArr = []
        for att in attestations:
            if att["data"]["index"] == committeeIndex:
                aggregationBitsHex = att["aggregation_bits"]
                binRes = struct.unpack('<32B', unhexlify(aggregationBitsHex[2:]))
                binStr = ""
                for b in binRes:
                    if len(str(bin(b))) != 10:
                        binS = str(bin(b))[2:]
                        binPadded = "".join(["0" for i in range(len(binS), 8)]) + binS
                    else:
                        binPadded = str(bin(b))[2:]
                    binStr += str(binPadded[::-1])
                bitsArr.append(binStr[:-4])
        return bitsArr

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        print("Epoch: ", ep)
        print("Prev epoch: ", self.prevEpoch)
        if self.prevEpoch != ep:
            validatorActiveIndexes = self.s.chain.isStaking()
            for i, index in enumerate(validatorActiveIndexes):
                prevPerformance = 100
                if str(index) not in self.prev:
                    self.prev[str(index)] = {}
                    self.prev[str(index)]["miss"] = 0
                    self.prev[str(index)]["count"] = 0
                validator = self.s.chain.getValidatorCommitteeIndexInEpoch(index, ep)
                if validator:
                    bits = self.getAggregationBits(validator["slot"], validator["indexCommittee"])
                    missed = True
                    for bit in bits:
                        if bit[validator["indexInCommittee"]] != "0":
                            missed = False
                    if missed:
                        self.prev[str(index)]["miss"] += 1
                    self.prev[str(index)]["count"] += 1
                    print("Validator: ", validator)
                    out = ""
                    if self.prev[str(index)]["count"] > 0 and self.prev[str(index)]["count"] % 12 == 0:
                        diffMiss = self.prev[str(index)]["miss_last_12_slots"] - self.prev[str(index)]["miss"]
                        diffCount = self.prev[str(index)]["count_last_12_slots"] - self.prev[str(index)]["count"]
                        performance = diffMiss / diffCount * 100
                        if performance < 90:
                            if prevPerformance != 100:
                                out += "\n\n"
                            out += f"validator {index} performance: {performance:.2f} % "
                            out += f"({diffMiss} missed out the {diffCount} slots) {Emoji.BlockMiss}"
                            prevPerformance = performance
                        self.prev[str(index)]["miss_last_12_slots"] = self.prev[str(index)]["miss"]
                        self.prev[str(index)]["count_last_12_slots"] = self.prev[str(index)]["count"]
            print("Prev: ", self.prev)
            self.prevEpoch = ep
            if out != "":
                return self.notify(
                    out,
                    level=NotificationLevel.Info,
                )
        return False


class TaskEthereumBlockProductionCheck(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(1)):
        super().__init__("TaskEthereumBlockProductionCheck", services, checkEvery, notifyEvery)
        self.prev = {}

    @staticmethod
    def isPluggable(services):
        c = services.chain.getValidatorActiveCount()
        return services.conf.exists("chain.validatorAddress") and c > 0

    def run(self):
        validatorActiveIndexes = self.s.chain.isStaking()
        for i, index in enumerate(validatorActiveIndexes):
            pass
        return False


class TaskValidatorBalanceCheck(Task):
    def __init__(self, services, checkEvery=hours(24), notifyEvery=hours(24)):
        super().__init__("TaskValidatorBalanceCheck", services, checkEvery, notifyEvery)
        self.prev = {}

    @staticmethod
    def isPluggable(services):
        c = services.chain.getValidatorActiveCount()
        return services.conf.exists("chain.validatorAddress") and c > 0

    def run(self):
        validatorActiveIndexes = self.s.chain.isStaking()
        for i, index in enumerate(validatorActiveIndexes):
            if str(index) in self.prev:
                prevBalance = self.prev[str(index)]
                newBalance = True
            else:
                newBalance = False
            self.prev[str(index)] = self.s.chain.getValidatorRewards(index)

            out = f"\nvalidator index {index}:\n"
            out += f"balance: {self.prev[str(index)]} ETH"
            if newBalance:
                out += f"\nrewards in the latest 24hr: {self.prev[str(index)] - prevBalance} ETH "
            out += f"{Emoji.ActStake}"
            if len(validatorActiveIndexes) - 1 > i:
                out += "\n"

        return self.notify(
            out,
            level=NotificationLevel.Info,
        )
    

class Ethereum(Chain):
    TYPE = "ethereum"
    NAME = "ethereum"
    BLOCKTIME = 15
    EP = "http://localhost:8545/" # execution client
    CC = "http://localhost:5052/" # consensus client
    CUSTOM_TASKS = [
        TaskEthereumHealthError,
        TaskEthereumLowPeerError,
        TaskEthereumAttestationsCheck,
        TaskEthereumBlockProductionCheck,
        TaskValidatorBalanceCheck,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        if conf.exists("chain.beaconEndpoint"):
            self.CC = f"{conf.getOrDefault('chain.beaconEndpoint')}"

    @staticmethod
    def detect(conf):
        try:
            return Ethereum(conf).getHeight() and Ethereum(conf).getSlot()
        except:
            return False

    def getLatestVersion(self):
        raise Exception("Abstract getLatestVersion()")

    def getVersion(self):
        out = requests.get(f"{self.CC}/eth/v1/node/version")
        return json.loads(out.text)["data"]["version"]

    def getHealth(self):
        status = requests.get(f"{self.CC}/eth/v1/node/health").status_code
        return status != 503 and status != 400

    def getHeight(self):
        return self.rpcCall("eth_blockNumber")

    def getSlot(self):
        out = requests.get(f"{self.CC}/eth/v1/beacon/headers")
        return json.loads(out.text)["data"][0]["header"]["message"]["slot"]

    def getEpoch(self):
        out = requests.get(f"{self.CC}/eth/v1/beacon/states/finalized/finality_checkpoints")
        return json.loads(out.text)["data"]["current_justified"]["epoch"]

    def getBlockHash(self):
        return self.rpcCall("eth_getBlockByNumber", ["latest", False])["hash"]

    def getNetwork(self):
        return self.rpcCall("net_version")

    def getPeerCount(self):
        return int(self.rpcCall("net_peerCount"), 16)

    def getBeaconNodePeerCount(self):
        out = requests.get(f"{self.CC}/eth/v1/node/peer_count")
        return int(json.loads(out.text)["data"]["connected"])
    
    def isStaking(self):
        validatorStatus = self.isValidator()
        return [k for k, v in validatorStatus.items() if "active" in v]

    def isValidator(self):
        validatorIndexes = self.conf.getOrDefault("chain.validatorAddress")
        try:
            if validatorIndexes:
                validators = {}
                for index in validatorIndexes.split(", "):
                    out = requests.get(f"{self.CC}/eth/v1/beacon/states/head/validators/{index}")
                    validators[str(index)] = json.loads(out.text)["data"]["status"]
                return validators
            else:
                return False
        except:
            return False

    def isSynching(self):
        out = requests.get(f"{self.CC}/eth/v1/node/syncing")
        return json.loads(out.text)["data"]["is_syncing"]
    
    def getValidatorActiveCount(self):
        return len([s for s in self.isStaking()])
    
    def getWithdrawalCredentials(self, validatorIndex):
        out = requests.get(f"{self.CC}/eth/v1/beacon/states/head/validators/{validatorIndex}")
        return json.loads(out.text)["data"]["validator"]["withdrawal_credentials"]
    
    def getAddressBalance(self, address):
        balance = self.rpcCall("eth_getBalance", [address, "latest"])
        return int(balance, 16) * 10 ** -18
    
    def getValidatorBalance(self, validatorIndex):
        out = requests.get(f"{self.CC}/eth/v1/beacon/states/head/validators/{validatorIndex}")
        return int(json.loads(out.text)["data"]["balance"]) * 10 ** -9

    def getValidatorRewards(self, validatorIndex):
        withdrawalCredentials = self.getWithdrawalCredentials(validatorIndex)
        if withdrawalCredentials[:4] == "0x01":
            withdrawalAddress = withdrawalCredentials[:2] + withdrawalCredentials[26:]
            return self.getAddressBalance(withdrawalAddress) + self.getValidatorBalance(validatorIndex)
        return self.getValidatorBalance(validatorIndex)

    def getValidatorCommitteeIndexInEpoch(self, validatorIndex, epoch):
        out = requests.get(f"{self.CC}/eth/v1/beacon/states/head/committees?epoch={epoch}")
        committeeEpochData = json.loads(out.text)["data"]
        val = {}
        for committee in committeeEpochData:
            try:
                index = committee["validators"].index(validatorIndex)
                val["indexCommittee"] = committee["index"]
                val["indexInCommittee"] = index
                val["slot"] = committee["slot"]
                break
            except:
                pass
        return val

    def getSlotAttestations(self, slot):
        out = requests.get(f"{self.CC}/eth/v2/beacon/blocks/{slot}")
        print("Status code attestations request: ", out.status_code)
        if out.status_code == 404:
            return "Not ready yet"
        return json.loads(out.text)["data"]["message"]["body"]["attestations"]
