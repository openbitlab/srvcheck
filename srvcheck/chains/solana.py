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
from statistics import median

from ..notification import Emoji, NotificationLevel
from ..tasks import Task, hours, minutes, seconds
from ..utils import Bash
from .chain import Chain


class TaskSolanaHealthError(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskSolanaHealthError", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        try:
            self.s.chain.getHealth()
            return False
        except:
            return self.notify(
                f"health error! {Emoji.Health}", level=NotificationLevel.Error
            )


class TaskSolanaDelinquentCheck(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskSolanaDelinquentCheck", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        if self.s.chain.isDelinquent():
            return self.notify(
                f"validator is delinquent {Emoji.Delinq}", level=NotificationLevel.Error
            )
        else:
            return False


class TaskSolanaBalanceCheck(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(10)):
        super().__init__("TaskSolanaBalanceCheck", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        balance = self.s.chain.getValidatorBalance()
        if balance < 1.0:
            return self.notify(
                f"validator balance is too low, {balance} SOL left {Emoji.LowBal}",
                level=NotificationLevel.Error,
            )
        else:
            return False


class TaskSolanaLastVoteCheck(Task):
    def __init__(self, services, checkEvery=seconds(30), notifyEvery=minutes(5)):
        super().__init__("TaskSolanaLastVoteCheck", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        lastVote = self.s.chain.getLastVote()
        md = self.s.chain.getMedianLastVote()
        if self.prev is None:
            self.prev = lastVote
        elif self.prev == lastVote and md > lastVote:
            return self.notify(
                f"last vote stuck at height: {lastVote}, median is: {md} {Emoji.Slow}",
                level=NotificationLevel.Error,
            )
        self.prev = lastVote
        return False


class TaskSolanaEpochActiveStake(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(24)):
        super().__init__(
            "TaskSolanaEpochActiveStake", services, checkEvery, notifyEvery
        )
        self.prev = None
        self.prevEpoch = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        ep = self.s.chain.getEpoch()
        act_stake = self.s.chain.getActiveStake()

        if self.prev is None:
            self.prev = act_stake
        if self.prevEpoch is None:
            self.prevEpoch = ep

        if self.prevEpoch != ep:
            self.prev = act_stake
            self.prevEpoch = ep
            return self.notify(
                f"active stake for epoch {ep}: {act_stake} SOL {Emoji.ActStake}",
                level=NotificationLevel.Info,
            )
        return False


class TaskSolanaLeaderSchedule(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=hours(24)):
        super().__init__("TaskSolanaLeaderSchedule", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prev is None:
            self.prev = ep

        try:
            if self.prev != ep:
                schedule = self.s.chain.getLeaderSchedule()
                self.prev = ep
                return self.notify(
                    f"{len(schedule)} leader slot assigned for the epoch {ep} {Emoji.Leader}",
                    level=NotificationLevel.Info,
                )
            return False
        except Exception:
            return self.notify(
                f"no leader slot assigned for the epoch {ep} {Emoji.NoLeader}",
                level=NotificationLevel.Info,
            )


class TaskSolanaSkippedSlots(Task):
    def __init__(self, services, checkEvery=hours(6), notifyEvery=hours(6)):
        super().__init__("TaskSolanaSkippedSlots", services, checkEvery, notifyEvery)
        self.prev = None
        self.prevBP = 0
        self.prevM = 0
        self.THRESHOLD_SKIPPED_SLOT = 0.25  # 25 %

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prev is None:
            self.prev = ep

        bp_info = self.s.chain.getBlockProduction()
        if bp_info[0] != 0:
            skipped_perc = (bp_info[0] - bp_info[1]) / bp_info[0]
            if self.prev == ep:
                self.prevBP = bp_info[0]
                self.prevM = bp_info[1]
            if skipped_perc >= self.THRESHOLD_SKIPPED_SLOT:
                skip_p = f"{skipped_perc * 100:.2f}"
                return self.notify(
                    "skipped %s%% of assigned slots (%d/%d) %s"
                    % (skip_p, bp_info[1], bp_info[0], Emoji.BlockMiss),
                    level=NotificationLevel.Warning,
                )
        if self.prev != ep:
            e = self.prev
            self.prev = ep
            if self.prevBP != 0:
                skip_p = f"{(self.prevBP - self.prevM) / self.prevBP * 100:.2f}"
                return self.notify(
                    "skipped %s%% of assigned slots (%d/%d) in the epoch %s %s"
                    % (skip_p, self.prevM, self.prevBP, e, Emoji.BlockProd),
                    level=NotificationLevel.Warning,
                )
        return False


class Solana(Chain):
    TYPE = "solana"
    NAME = ""
    BLOCKTIME = 60
    EP = "http://localhost:8899/"
    CUSTOM_TASKS = [
        TaskSolanaHealthError,
        TaskSolanaDelinquentCheck,
        TaskSolanaBalanceCheck,
        TaskSolanaLastVoteCheck,
        TaskSolanaEpochActiveStake,
        TaskSolanaLeaderSchedule,
        TaskSolanaSkippedSlots,
    ]

    @staticmethod
    def detect(conf):
        try:
            Solana(conf).getVersion()
            return True
        except:
            return False

    def getHealth(self):
        return self.rpcCall("getHealth")

    def getVersion(self):
        return self.rpcCall("getVersion")["solana-core"]

    def getHeight(self):
        return self.rpcCall("getBlockHeight")

    def getBlockHash(self):
        return self.rpcCall("getLatestBlockhash")["value"]["blockhash"]

    def getEpoch(self):
        return self.rpcCall("getEpochInfo")["epoch"]

    def getLeaderSchedule(self):
        identityAddr = self.getIdentityAddress()
        schedule = self.rpcCall("getLeaderSchedule", [None, {"identity": identityAddr}])
        if len(schedule) == 1:
            return schedule[identityAddr]
        raise Exception(
            "No leader slot assigned to your Identity for the current epoch",
            level=NotificationLevel.Warning,
        )

    def getBlockProduction(self):
        identityAddr = self.getIdentityAddress()
        b_prod_info = self.rpcCall("getBlockProduction", [{"identity": identityAddr}])[
            "value"
        ]["byIdentity"]
        if len(b_prod_info) == 1:
            return b_prod_info[identityAddr]
        raise Exception("No blocks produced in the current epoch")

    def getPeerCount(self):
        raise Exception("Abstract getPeerCount()")

    def getNetwork(self):
        raise Exception("Abstract getNetwork()")

    def isStaking(self):
        raise Exception("Abstract isStaking()")

    def isSynching(self):
        return False

    def getIdentityAddress(self):
        return Bash(f"solana address --url {self.EP}").value()

    def getGeneralValidatorsInfo(self):
        return json.loads(
            Bash(f"solana validators --url {self.EP} --output json-compact").value()
        )

    def getValidators(self):
        return self.getGeneralValidatorsInfo()["validators"]

    def isDelinquent(self):
        return self.getValidatorInfo()["delinquent"]

    def getValidatorBalance(self):
        return float(
            Bash(
                f"solana balance {self.getIdentityAddress()} --url {self.EP} | grep -o '[0-9.]*'"
            ).value()
        )

    def getLastVote(self):
        return self.getValidatorInfo()["lastVote"]

    def getActiveStake(self):
        return int(self.getValidatorInfo()["activatedStake"]) / (10**9)

    def getDelinquentStakePerc(self):
        val_info = self.getGeneralValidatorsInfo()
        act_stake = val_info["totalActiveStake"]
        del_stake = val_info["totalDelinquentStake"]
        return f"{del_stake / act_stake * 100:.2f}"

    def getValidatorInfo(self):
        validators = self.getValidators()
        val_info = next(
            (x for x in validators if x["identityPubkey"] == self.getIdentityAddress()),
            None,
        )
        if val_info:
            return val_info
        raise Exception("Identity not found in the validators list")

    def getMedianLastVote(self):
        validators = self.getValidators()
        votes = []
        for v in validators:
            votes.append(v["lastVote"])
        return median(votes)
