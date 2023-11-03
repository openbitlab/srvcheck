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
from typing import List

from ..tasks import Task
from ..utils import Bash
from .chain import Chain


class Lisk(Chain):
    TYPE = "lisk"
    NAME = "lisk"
    BLOCKTIME = 15
    EP = "http://localhost:9933/"
    CUSTOM_TASKS: List[Task] = []

    @staticmethod
    def detect(conf):
        try:
            Lisk(conf).getVersion()
            return True
        except:
            return False

    def _nodeInfo(self):
        return json.loads(Bash("sudo -u lisk lisk-core node:info").value())

    def _forgingStatus(self):
        return json.loads(Bash("sudo -u lisk lisk-core forging:info").value())

    def getLatestVersion(self):
        raise Exception("Abstract getLatestVersion()")

    def getVersion(self):
        return self._nodeInfo()["version"]

    def getHeight(self):
        return self._nodeInfo()["height"]

    def getBlockHash(self):
        return self._nodeInfo()["lastBlockID"]

    def getPeerCount(self):
        return len(self._nodeInfo()["network"]["seedPeers"])

    def getNetwork(self):
        return self._nodeInfo()["genesisConfig"]["communityIdentifier"]

    def isStaking(self):
        return len(self._forgingStatus()) > 0

    def isSynching(self):
        return self._nodeInfo()["syncing"]
