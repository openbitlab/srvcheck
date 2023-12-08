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

import requests

from .ethereum import (
    Ethereum
)


def getPrometheusMetricValue(metrics, metric_name):
    metric = list(filter(lambda x: metric_name in x, metrics.split("\n")))[-1]
    return metric.split(" ")[-1]


class Ssv(Ethereum):
    TYPE = "dvt"
    EP_METRICS = "http://localhost:15000"
    CUSTOM_TASKS = [
        
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

#Counter metrics
    def getPeers(self):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        peers = getPrometheusMetricValue(out.text, "ssv_p2p_all_connected_peers")
        return peers

    def getSubmittedRoles(self, role):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        submitted = getPrometheusMetricValue(out.text, "ssv_validator_roles_submitted{role='"+role+"'}")
        return submitted

    def getFailedRoles(self, role):
        out = requests.get(f"{self.EP_METRICS}/metrics")
        submitted = getPrometheusMetricValue(out.text, "ssv_validator_roles_failed{role='" + role + "'}")
        return submitted
