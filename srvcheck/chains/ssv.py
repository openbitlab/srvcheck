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

import requests, json

from ..tasks import Task, minutes, seconds
from ..notification import Emoji, NotificationLevel
from .ethereum import Ethereum
from ..utils import Bash, ConfSet, ConfItem

ConfSet.addItem(ConfItem("chain.dkgEndpoint", description="Ssv dkg client endpoint"))


def getPrometheusMetricValue(metrics, metric_name):
    metric = list(filter(lambda x: metric_name in x, metrics.split("\n")))[-1]
    return metric.split(" ")[-1]


class TaskSSVCheckAttestationsMiss(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        super().__init__("TaskSSVCheckAttestationsMiss", services, checkEvery, notifyEvery)
        self.prevEpoch = None

    @staticmethod
    def isPluggable(services):
        c = len(services.chain.getValidators())
        return c > 0

    def run(self):
        debug = "ATTESTATION -"
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        print(f"{debug} Epoch: ", ep)
        print(f"{debug} Prev epoch: ", self.prevEpoch)
        if self.prevEpoch != ep:
            validators = self.s.chain.getValidators()
            print(f"{debug} Active validators: ", validators)
            out = ""
            for v in validators:            
                submitted = 0
                attestationsSubmitted = [
                    json.loads(d.split("\t")[-1]) 
                    for d in self.s.chain.getValidatorDuties(v)
                    if "successfully submitted attestation" in d
                ]
                diff = ep - self.prevEpoch
                for i in range(diff - 1):
                    for attestation in attestationsSubmitted[::-1]:
                        slot = attestation["slot"]
                        print(f"{debug} Slot - Epoch: {slot} - {self.s.chain.getSlotEpoch(slot)}")
                        if (ep - i - 1) == self.s.chain.getSlotEpoch(slot):
                            print(f"{debug} Submitted\n")
                            submitted += 1
                            break
                print(f"{debug} Diff: ", diff)
                print(f"{debug} Submitted: ", submitted)
                missed = diff - submitted
                if missed > 0:
                    performance = submitted / diff * 100
                    if out != "":
                        out += "\n"
                    out += f"validator {v} missed {missed} attestations in the last hour!"
                    out += f" ({performance:.2f} %)"
            self.prevEpoch = ep
            if out != "":
                out += f" {Emoji.BlockMiss}"
                return self.notify(out, level=NotificationLevel.Info)
        return False


class TaskSSVCheckSyncCommitteeMiss(Task):
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(5)):
        super().__init__("TaskSSVCheckSyncCommitteeMiss", services, checkEvery, notifyEvery)
        self.prevEpoch = None
        self.SLOTS_IN_EPOCH = 31

    @staticmethod
    def isPluggable(services):
        c = len(services.chain.getValidators())
        return c > 0

    def run(self):
        debug = "SYNC COMMITTEE -"
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        print(f"{debug} Epoch: ", ep)
        print(f"{debug} Prev epoch: ", self.prevEpoch)
        if self.prevEpoch != ep:
            validators = self.s.chain.getValidators()
            print(f"{debug} Active validators: ", validators)
            out = ""
            for v in validators:
                submitted = 0
                validatorIndex = self.s.chain.getValidatorIndexFromPubKey(v)
                duty = self.s.chain.getValidatorSyncDuty(validatorIndex, ep - 1)
                if duty != -1:
                    syncCommitteeSubmitted = [
                        json.loads(d.split("\t")[-1]) 
                        for d in self.s.chain.getValidatorDuties(v)
                        if "successfully submitted sync committee" in d
                    ]
                    for syncCommittee in syncCommitteeSubmitted[::-1]:
                        slot = syncCommittee["slot"]
                        print(f"{debug} Slot - Epoch: {slot} - {self.s.chain.getSlotEpoch(slot)}")
                        if (ep - 1) == self.s.chain.getSlotEpoch(slot):
                            print(f"{debug} Submitted\n")
                            submitted += 1
                            break
                    print(f"{debug} Submitted: ", submitted)
                    missed = self.SLOTS_IN_EPOCH - submitted
                    if missed > 0:
                        performance = submitted / self.SLOTS_IN_EPOCH * 100
                        if out != "":
                            out += "\n"
                        out += f"validator {v} missed {missed} sync committee in the last epoch!"
                        out += f" ({performance:.2f} %)"
            self.prevEpoch = ep
            if out != "":
                out += f" {Emoji.BlockMiss}"
                return self.notify(out, level=NotificationLevel.Info)
        return False
    

class TaskSSVCheckProposalMiss(Task):
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(5)):
        super().__init__("TaskSSVCheckProposalMiss", services, checkEvery, notifyEvery)
        self.prevEpoch = None

    @staticmethod
    def isPluggable(services):
        c = len(services.chain.getValidators())
        return c > 0

    def run(self):
        debug = "BLOCK PROPOSER -"
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        print(f"{debug} Epoch: ", ep)
        print(f"{debug} Prev epoch: ", self.prevEpoch)
        if self.prevEpoch != ep:
            validators = self.s.chain.getValidators()
            print(f"{debug} Active validators: ", validators)
            out = ""
            for v in validators:
                submitted = 0
                validatorIndex = self.s.chain.getValidatorIndexFromPubKey(v)
                duty = self.s.chain.getValidatorProposerDuty(validatorIndex, ep - 1)
                if duty != -1:
                    blockProposalSubmitted = [
                        json.loads(d.split("\t")[-1]) 
                        for d in self.s.chain.getValidatorDuties(v)
                        if "successfully submitted block proposal" in d
                    ]
                    for proposal in blockProposalSubmitted[::-1]:
                        slot = proposal["slot"]
                        print(f"{debug} Slot - Epoch: {slot} - {self.s.chain.getSlotEpoch(slot)}")
                        if (ep - 1) == self.s.chain.getSlotEpoch(slot):
                            print(f"{debug} Submitted\n")
                            submitted += 1
                            break
                    print(f"{debug} Submitted: ", submitted)
                    if submitted == 0:
                        if out != "":
                            out += "\n"
                        out += f"validator {v} missed block proposal duty in the last epoch!"
            self.prevEpoch = ep
            if out != "":
                out += f" {Emoji.BlockMiss}"
                return self.notify(out, level=NotificationLevel.Info)
        return False


class TaskSSVCheckSubmissionATTESTER(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        self.prevFailed = None
        self.prevSubmitted = None
        self.prev = None

        super().__init__(
            "TaskSSVCheckSubmissionATTESTER",
            services,
            checkEvery=checkEvery,
            notifyEvery=notifyEvery,
        )

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        failed = self.s.chain.getFailedRoles("ATTESTER")
        success = self.s.chain.getSubmittedRoles("ATTESTER")

        if not self.prev:
            self.prev = failed
            self.prevSubmitted = success
            return False

        total = failed - self.prev + success - self.prevSubmitted
        downtime = ((failed - self.prev) / total) * 100
        if downtime > 10:
            return self.notify(
                f"node operator missed {downtime:.2f} % of attester submissions!"
                + f" {Emoji.BlockMiss}",
                level=NotificationLevel.Error
            )
        return False


class TaskSSVCheckBNStatus(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(5)):
        super().__init__(
            "TaskSSVCheckBNStatus",
            services,
            checkEvery=seconds(services.chain.BLOCKTIME),
            notifyEvery=notifyEvery,
        )

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        bn = self.s.chain.getBeaconStatus()
        if int(bn) != 2:
            return self.notify(
                f"beacon client is not available! {Emoji.Health}",
                level=NotificationLevel.Error
            )
        return False


class TaskSSVCheckECStatus(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(5)):
        super().__init__(
            "TaskSSVCheckECStatus",
            services,
            checkEvery=seconds(services.chain.BLOCKTIME),
            notifyEvery=notifyEvery,
        )

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        ec = self.s.chain.getECStatus()
        if int(ec) != 2:
            return self.notify(
                f"execution client is not available! {Emoji.Health}",
                level=NotificationLevel.Error
            )
        return False


class TaskSSVCheckStatus(Task):
    def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(5)):
        super().__init__(
            "TaskSSVCheckStatus",
            services,
            checkEvery=seconds(services.chain.BLOCKTIME),
            notifyEvery=notifyEvery,
        )

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        health = self.s.chain.getHealth()
        if int(health) != 1:
            return self.notify(
                f"SSV node unhealthy! {Emoji.Health}",
                level=NotificationLevel.Error
            )
        return False


class TaskSSVDKGHealth(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        super().__init__("TaskSSVDKGHealth", services, checkEvery, notifyEvery)

    @staticmethod
    def isPluggable(services):
        return services.conf.exists("chain.dkgEndpoint")

    def run(self):
        try:
            res = requests.get(self.s.chain.DKG)
            print(res.status_code)
            return False
        except:
            return self.notify(
                f"SSV DKG client unhealthy! {Emoji.Health}",
                level=NotificationLevel.Error
            )


class Ssv(Ethereum):
    TYPE = "dvt"
    EP_METRICS = "http://localhost:15000"
    CUSTOM_TASKS = [
        TaskSSVCheckAttestationsMiss,
        TaskSSVCheckStatus,
        TaskSSVCheckBNStatus,
        TaskSSVCheckECStatus,
        TaskSSVCheckSubmissionATTESTER,
        TaskSSVDKGHealth,
        TaskSSVCheckSyncCommitteeMiss,
        TaskSSVCheckProposalMiss,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        if conf.exists("chain.dkgEndpoint"):
            self.DKG = conf.getOrDefault('chain.dkgEndpoint')

    @staticmethod
    def detect(conf):
        try:
            return Ssv(conf).getHealth()
        except:
            return False

    def getHealth(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        ssvStatus = getPrometheusMetricValue(out.text, "ssv_node_status")
        return ssvStatus

    def getBeaconStatus(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        beaconStatus = getPrometheusMetricValue(out.text, "ssv_beacon_status")
        return beaconStatus

    def getECStatus(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        ecStatus = getPrometheusMetricValue(out.text, "ssv_eth1_status")
        return ecStatus

    def getValidators(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        out = list(filter(lambda x: "ssv:validator:v2:status" in x, out.text.split("\n")))
        return list(map(lambda x: x.split("pubKey=\"")[1].split("\"")[0], out[2:]))

    def getValidatorStatus(self, validatorPubKey):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        metricStr = "ssv:validator:v2:status{pubKey=\""+validatorPubKey+"\"}"
        status = getPrometheusMetricValue(out.text, metricStr)
        return int(status)

#Counter metrics
    def getPeerCount(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        peers = getPrometheusMetricValue(out.text, "ssv_p2p_all_connected_peers")
        return int(peers)

    def getSubmittedRoles(self, role):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        metricStr = "ssv_validator_roles_submitted{role=\""+role+"\"}"
        submitted = getPrometheusMetricValue(out.text, metricStr)
        return int(submitted)

    def getFailedRoles(self, role):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        metricStr = "ssv_validator_roles_failed{role=\"" + role + "\"}"
        submitted = getPrometheusMetricValue(out.text, metricStr)
        return int(submitted)

    def getValidatorDuties(self, validatorPubKey, minutes=120):
        if self.conf.getOrDefault("chain.service"):
            s = self.conf.getOrDefault("chain.service")
            cmd = f"journalctl -u {s} --no-pager --since '{minutes} min ago'"
        elif self.conf.getOrDefault("chain.docker"):
            containerId = self.conf.getOrDefault("chain.docker")
            cmd = f"docker logs --since {minutes}m {containerId}"
        duties = (
            Bash(
                f"{cmd} | grep duty | grep {validatorPubKey} | "
                + "awk -F'Validator'  '{ print $2 }'"
            )
            .value()
            .split("\n")
        )
        logs = [b.strip() for b in duties if b != ""]
        return logs