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
from ..utils import Bash


class TaskSSVCheckAttestationsMiss(Task):
    def __init__(self, services, checkEvery=minutes(30), notifyEvery=minutes(30)):
        super().__init__("TaskSSVCheckAttestationsMiss", services, checkEvery, notifyEvery)
        self.prev = {}
        self.prevEpoch = None

    @staticmethod
    def isPluggable(services):
        c = len(services.chain.getValidators())
        return c > 0

    def run(self):
        ep = self.s.chain.getEpoch()

        if self.prevEpoch is None:
            self.prevEpoch = ep

        print("Epoch: ", ep)
        print("Prev epoch: ", self.prevEpoch)
        if self.prevEpoch != ep:
            submitted = 0
            validators = self.s.chain.getValidators()
            print("Active validators: ", validators)
            out = ""
            for v in validators:
                attestationsSubmitted = [json.loads(d.split("\t")[-1]) for d in self.s.chain.getValidatorDuties(v) if "successfully submitted attestation" in d]
                diff = ep - self.prevEpoch
                for i in range(diff):
                    for attestation in attestationsSubmitted[::-1]:
                        slot = attestation["slot"]
                        print("Slot: ", slot)
                        print("Slot Epoch: ", self.s.chain.getSlotEpoch(slot))
                        if (ep - i - 1) == self.s.chain.getSlotEpoch(slot):
                            print("Submitted")
                            submitted += 1
                            break
                print("Diff: ", diff)
                print("Submitted: ", submitted)
                if submitted != diff:
                    performance = submitted / diff * 100
                    if out != "":
                        out += "\n"
                    out += f"validator {v} missed {submitted} out of {diff} attestations! ({performance:.2f} %)"
            print("Message: ", out)
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
                f"Node operator missed " + f"{downtime}%" + "of attester submissions!"
                + f"{Emoji.BlockMiss}",
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
                f"Beacon client is not available!"
                + f"{Emoji.Health}",
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
                f"Execution client is not available!"
                + f"{Emoji.Health}",
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
                f"SSV node unhealthy!"
                + f"{Emoji.Health}",
                level=NotificationLevel.Error
            )
        return False

def getPrometheusMetricValue(metrics, metric_name):
    metric = list(filter(lambda x: metric_name in x, metrics.split("\n")))[-1]
    return metric.split(" ")[-1]


class Ssv(Ethereum):
    TYPE = "dvt"
    EP_METRICS = "http://localhost:15000"
    CUSTOM_TASKS = [
        TaskSSVCheckAttestationsMiss,
        TaskSSVCheckStatus,
        TaskSSVCheckBNStatus,
        TaskSSVCheckECStatus,
        TaskSSVCheckSubmissionATTESTER,
    ]

    def __init__(self, conf):
        super().__init__(conf)

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
        status = getPrometheusMetricValue(out.text, "ssv:validator:v2:status{pubKey=\""+validatorPubKey+"\"}")
        return int(status)

#Counter metrics
    def getPeerCount(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        peers = getPrometheusMetricValue(out.text, "ssv_p2p_all_connected_peers")
        return int(peers)

    def getSubmittedRoles(self, role):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        submitted = getPrometheusMetricValue(out.text, "ssv_validator_roles_submitted{role=\""+role+"\"}")
        return int(submitted)

    def getFailedRoles(self, role):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        submitted = getPrometheusMetricValue(out.text, "ssv_validator_roles_failed{role=\"" + role + "\"}")
        return int(submitted)

    def getValidatorDuties(self, validatorPubKey, minutes=60):
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