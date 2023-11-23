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
from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes
from ..utils import ConfItem, ConfSet
from .chain import Chain

ConfSet.addItem(ConfItem("chain.validatorAddress", description="Validators indexes"))
ConfSet.addItem(ConfItem("chain.beaconEndpoint", description="Consensus client endpoint"))


def checkMissedBit(validatorIndexInCommittee, binBits=None):
    if binBits:
        missed = True
        for bit in binBits:
            if bit[validatorIndexInCommittee] != "0":
                missed = False
        return missed
    else:
        return None
        
def convertBitsHexBin(hexBits):
    bitsArr = []
    for hexB in hexBits:
        binRes = struct.unpack('<32B', unhexlify(hexB[2:]))
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

def initializeValidatorData(validator, validatorIndex):
    if str(validatorIndex) not in validator:
        validator[str(validatorIndex)] = {}
        validator[str(validatorIndex)]["miss"] = 0
        validator[str(validatorIndex)]["count"] = 0
        validator[str(validatorIndex)]["miss_last_n_slots"] = 0
        validator[str(validatorIndex)]["count_last_n_slots"] = 0
        validator[str(validatorIndex)]["inclusions"] = []
    return validator

def fixUrl(url):
    parts = [p for i, p in enumerate(url.split("/")) if p != "" or i < 2]
    return "/".join(parts)

def getOutput(validator, first, strOut, index):
    out = ""
    mod = 5 if strOut == "syncs" else 12
    if validator["count"] > 0 and validator["count"] % mod == 0:
        diffMiss = validator["miss"] - validator["miss_last_n_slots"]
        diffCount = validator["count"] - validator["count_last_n_slots"]
        performance = diffMiss / diffCount * 100
        if performance < 90:
            if not first:
                out += "\n\n"
            out += f"Validator {index} {strOut} performance: {performance:.2f} % "
            out += f"({diffMiss} missed out the {diffCount} {strOut}) {Emoji.BlockMiss}"
            distances = len([d for d in validator["inclusions"] if d > 1])
            if distances > 0:
                out += f"\n{distances} times with inclusion distance greater than 1 {Emoji.Slow}"
        validator["miss_last_n_slots"] = validator["miss"]
        validator["count_last_n_slots"] = validator["count"]
    if validator["count"] % (mod * 10) == 0:
        validator = initializeValidatorData(validator, index)
    return validator, out


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
        attestations = self.s.chain.getSlotAttestations(slot)
        if attestations == "Not available":
                return None
        bitsArr = []
        for att in attestations:
            if att["data"]["index"] == committeeIndex:
                print("Attestation hex bits: ", att["aggregation_bits"])
                bitsArr.append(att["aggregation_bits"])
        bitsArr = convertBitsHexBin(bitsArr)
        print(f"Attestation Bits for slot {slot}:", bitsArr)
        return bitsArr
    
    def checkAttestationMissed(self, validator, tries):
        bits = self.getAggregationBits(int(validator["slot"]) + tries, validator["indexCommittee"])
        return checkMissedBit(int(validator["indexInCommittee"]), bits)

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        print("Epoch: ", ep)
        print("Prev epoch: ", self.prevEpoch)
        if self.prevEpoch != ep:
            validatorActiveIndexes = self.s.chain.isStaking()
            out = ""
            for index in validatorActiveIndexes:
                first = True
                self.prev = initializeValidatorData(self.prev, index)
                validator = self.s.chain.getValidatorAttestationDuty(index, ep)
                if validator:
                    i = 1
                    while True:
                        miss = self.checkAttestationMissed(validator, i)
                        if not miss or i > 30:
                            break
                        i += 1
                    print(f"Inclusion distance: {i}")
                    if miss is None:
                        continue
                    self.prev[str(index)]["miss"] += 1 if miss else 0
                    self.prev[str(index)]["count"] += 1
                    self.prev[str(index)]["inclusions"].append(i)
                    print("Validator: ", validator)
                    self.prev[str(index)], outStr = getOutput(self.prev[str(index)], first, "attestation", index)
                    out += outStr
                    first = False
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
        self.prevEpoch = None

    @staticmethod
    def isPluggable(services):
        c = services.chain.getValidatorActiveCount()
        return services.conf.exists("chain.validatorAddress") and c > 0

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep
        
        if self.prevEpoch != ep:
            validatorActiveIndexes = self.s.chain.isStaking()
            out = ""
            for index in validatorActiveIndexes:
                first = True
                validatorSlot = self.s.chain.getValidatorProposerDuty(index, ep)
                print("Validator Proposer Duty: ", validatorSlot)
                if validatorSlot != -1:
                    miss = self.s.chain.getSlotProposer(validatorSlot) == index
                    self.prev[str(index)] = True if miss else False
                    if not first:
                        out += "\n\n"
                    out += f"Validator {index} missed block proposal duty! {Emoji.BlockMiss}"
                    first = False
            self.prevEpoch = ep
            if out != "":
                return self.notify(
                    out,
                    level=NotificationLevel.Info,
                )
        return False


class TaskEthereumSyncCommitteeCheck(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(1)):
        super().__init__("TaskEthereumSyncCommitteeCheck", services, checkEvery, notifyEvery)
        self.prev = {}
        self.prevEpoch = None
        self.prevSlot = None

    @staticmethod
    def isPluggable(services):
        c = services.chain.getValidatorActiveCount()
        return services.conf.exists("chain.validatorAddress") and c > 0

    def run(self):
        ep = self.s.chain.getEpoch()
        slot = self.s.chain.getSlot()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        if self.prevSlot is None:
            self.prevSlot = slot

        if self.prevEpoch != ep:
            validatorActiveIndexes = self.s.chain.isStaking()
            out = ""
            for index in validatorActiveIndexes:
                first = True
                self.prev = initializeValidatorData(self.prev, index)
                validatorIndexInCommittee = self.s.chain.getValidatorSyncDuty(index, ep)
                print("Validator sync committee duty: ", validatorIndexInCommittee)
                if validatorIndexInCommittee != -1:
                    slot = self.s.chain.getSlot()
                    for s in range(self.prevSlot, slot):
                        hexBits = self.s.chain.getSyncCommitteeBitsHex(s)
                        print("Sync committee hex bits: ", hexBits)
                        if hexBits == "Not available":
                            continue
                        bitsArr = convertBitsHexBin([hexBits])
                        print("Sync committee bits: ", bitsArr)
                        miss = checkMissedBit(validatorIndexInCommittee, bitsArr)
                        self.prev[str(index)]["miss"] += 1 if miss else 0
                        self.prev[str(index)]["count"] += 1
                    outStr = f"Validator {index} syncs"
                    self.prev[str(index)], outStr = getOutput(self.prev[str(index)], first, outStr)
                    out += outStr
                    first = False
            self.prevEpoch = ep
            if out != "":
                return self.notify(
                    out,
                    level=NotificationLevel.Info,
                )


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

            out = f"\nValidator index {index}:\n"
            out += f"Total balance: {self.prev[str(index)]} ETH"
            if newBalance:
                out += f"\nRewards in the latest 24hr: {self.prev[str(index)] - prevBalance} ETH"
            out += f" {Emoji.ActStake}"
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
        TaskEthereumSyncCommitteeCheck,
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
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/node/version"))
        return json.loads(out.text)["data"]["version"]

    def getHealth(self):
        status = requests.get(fixUrl(f"{self.CC}/eth/v1/node/health")).status_code
        return status != 503 and status != 400

    def getHeight(self):
        return self.rpcCall("eth_blockNumber")

    def getSlot(self):
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/beacon/headers"))
        return json.loads(out.text)["data"][0]["header"]["message"]["slot"]

    def getEpoch(self):
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/beacon/states/head/finality_checkpoints"))
        return int(json.loads(out.text)["data"]["current_justified"]["epoch"])

    def getBlockHash(self):
        return self.rpcCall("eth_getBlockByNumber", ["latest", False])["hash"]

    def getNetwork(self):
        return self.rpcCall("net_version")

    def getPeerCount(self):
        return int(self.rpcCall("net_peerCount"), 16)

    def getBeaconNodePeerCount(self):
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/node/peer_count"))
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
                    out = requests.get(fixUrl(f"{self.CC}/eth/v1/beacon/states/head/validators/{index}"))
                    validators[str(index)] = json.loads(out.text)["data"]["status"]
                return validators
            else:
                return False
        except:
            return False

    def isSynching(self):
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/node/syncing"))
        return json.loads(out.text)["data"]["is_syncing"]
    
    def getValidatorActiveCount(self):
        return len([s for s in self.isStaking()])
    
    def getWithdrawalCredentials(self, validatorIndex):
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/beacon/states/head/validators/{validatorIndex}"))
        return json.loads(out.text)["data"]["validator"]["withdrawal_credentials"]
    
    def getAddressBalance(self, address):
        balance = self.rpcCall("eth_getBalance", [address, "latest"])
        return int(balance, 16) * 10 ** -18
    
    def getValidatorBalance(self, validatorIndex):
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/beacon/states/head/validators/{validatorIndex}"))
        return int(json.loads(out.text)["data"]["balance"]) * 10 ** -9

    def getValidatorRewards(self, validatorIndex):
        withdrawalCredentials = self.getWithdrawalCredentials(validatorIndex)
        if withdrawalCredentials[:4] == "0x01":
            withdrawalAddress = withdrawalCredentials[:2] + withdrawalCredentials[26:]
            return self.getAddressBalance(withdrawalAddress) + self.getValidatorBalance(validatorIndex)
        return self.getValidatorBalance(validatorIndex)

    def getValidatorAttestationDuty(self, validatorIndex, epoch):
        d = [validatorIndex]
        out = requests.post(fixUrl(f"{self.CC}/eth/v1/validator/duties/attester/{epoch}"), json=d)
        committeeEpochData = json.loads(out.text)["data"][0]
        val = {}
        val["indexCommittee"] = committeeEpochData["committee_index"]
        val["indexInCommittee"] = committeeEpochData["validator_committee_index"]
        val["slot"] = committeeEpochData["slot"]
        return val
    
    def getSlotAttestations(self, slot):
        out = requests.get(fixUrl(f"{self.CC}/eth/v2/beacon/blocks/{slot}"))
        print(f"Status code attestations request for slot {slot}: ", out.status_code)
        if out.status_code == 404:
            return "Not available"
        return json.loads(out.text)["data"]["message"]["body"]["attestations"]

    def getValidatorProposerDuty(self, validatorIndex, epoch):
        d = [validatorIndex]
        out = requests.get(fixUrl(f"{self.CC}/eth/v1/validator/duties/proposer/{epoch}"), json=d)
        proposersEpochData = json.loads(out.text)["data"]
        val = list(filter(lambda x: x["validator_index"] == validatorIndex, proposersEpochData))
        if len(val) > 0:
            return val[0]["slot"]
        return -1
    
    def getSlotProposer(self, slot):
        out = requests.get(fixUrl(f"{self.CC}/eth/v2/beacon/blocks/{slot}"))
        print("Status code attestations request: ", out.status_code)
        if out.status_code == 404:
            return "Not available"
        return json.loads(out.text)["data"]["message"]["proposer_index"]

    def getValidatorSyncDuty(self, validatorIndex, epoch):
        d = [validatorIndex]
        out = requests.post(fixUrl(f"{self.CC}/eth/v1/validator/duties/sync/{epoch}"), json=d)
        syncEpochData = json.loads(out.text)["data"]
        if len(syncEpochData) > 0:
            return syncEpochData["validator_sync_committee_indices"]
        return -1

    def getSyncCommitteeBitsHex(self, slot):
        out = requests.get(fixUrl(f"{self.CC}/eth/v2/beacon/blocks/{slot}"))
        print("Status code attestations request: ", out.status_code)
        if out.status_code == 404:
            return "Not available"
        return json.loads(out.text)["data"]["message"]["body"]["sync_aggregate"]["sync_committee_bits"]
