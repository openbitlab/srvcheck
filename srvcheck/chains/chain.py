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

import configparser
import re

import requests

from ..utils import Bash, ConfItem, ConfSet

ConfSet.addItem(ConfItem("chain.endpoint", None, str, "api endpoint"))
ConfSet.addItem(ConfItem("chain.blockTime", 10, int, "block time in seconds"))
ConfSet.addItem(ConfItem("chain.name", None, str, "chain name"))
ConfSet.addItem(ConfItem("chain.ghRepository", None, str, "github repository"))
ConfSet.addItem(ConfItem("chain.service", None, str, "systemd service name"))
ConfSet.addItem(ConfItem("chain.docker", None, str, "docker container id"))
ConfSet.addItem(ConfItem("chain.localVersion", None, str, "local version"))


def rpcCall(url, method, params=[]):
    d = requests.post(
        url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).json()
    return d["result"]


def getCall(url, data):
    return requests.get(url, json=data).json()


class Chain:
    NAME = ""
    BLOCKTIME: float = 10
    EP = ""

    def __init__(self, conf):
        self.conf = conf
        if self.conf.getOrDefault("chain.endpoint") is not None:
            self.EP = self.conf.getOrDefault("chain.endpoint")
        self.NAME = self.conf.getOrDefault("chain.name")

    def rpcCall(self, method, params=[]):
        """Calls the RPC method with the given parameters"""
        return rpcCall(self.EP, method, params)

    def getCall(self, r, data=None):
        """Calls the GET method with the given parameters"""
        return getCall(self.EP + r, data)

    # Abstract methods
    @staticmethod
    def detect(conf):
        """Checks if the current server is running this chain"""
        raise Exception("Abstract detect()")

    def getVersion(self):
        """Returns software version"""
        raise Exception("Abstract getVersion()")

    def getLatestVersion(self):
        """Returns software local version"""
        gh_repo = self.conf.getOrDefault("chain.ghRepository")
        if gh_repo:
            c = requests.get(
                f"https://api.github.com/repos/{gh_repo}/releases/latest"
            ).json()
            return c["tag_name"]
        raise Exception("No github repo specified!")

    def getLocalVersion(self):
        try:
            return self.getVersion()
        except Exception as e:
            ver = self.conf.getOrDefault("chain.localVersion")
            if ver is None:
                raise Exception("No local version of the software specified!") from e
            return ver

    def getHeight(self):
        """Returns the block height"""
        raise Exception("Abstract getHeight()")

    def getBlockHash(self):
        """Returns the block height"""
        raise Exception("Abstract getHeight()")

    def getPeerCount(self):
        """Returns the number of peers"""
        raise Exception("Abstract getPeerCount()")

    def getNetwork(self):
        """Returns network used"""
        raise Exception("Abstract getNetwork()")

    def isStaking(self):
        """Returns true if the node is staking"""
        raise Exception("Abstract isStaking()")

    def isSynching(self):
        """Returns true if the node is synching"""
        raise Exception("Abstract isSynching()")

    def getNodeBinary(self):
        cmd = ""
        if self.conf.getOrDefault("chain.service"):
            c = configparser.ConfigParser()
            serviceName = self.conf.getOrDefault("chain.service")
            c.read(f"/etc/systemd/system/{serviceName}")
            cmd = re.split(" ", c["Service"]["ExecStart"])[0]
        elif self.conf.getOrDefault("chain.docker"):
            containerId = self.conf.getOrDefault("chain.docker")
            cmd = Bash("docker inspect -f '{{ .Path }}' " + containerId).value()
        return cmd
