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

import psutil

from ..notification import Emoji
from ..tasks import Task, minutes
from .chain import Chain


class TaskTezosValidatorProcesses(Task):
    def __init__(self, services, checkEvery=minutes(5), notifyEvery=minutes(10)):
        super().__init__(
            "TaskTezosValidatorProcesses", services, checkEvery, notifyEvery
        )

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        baker = False
        accuser = False

        for proc in psutil.process_iter(["name"]):
            pn = proc.info["name"]
            if pn.find("tez-baker") != -1:
                baker = True
            if pn.find("tez-accuser") != -1:
                accuser = True

        if not baker or not accuser:
            return self.notify(
                f"Baker or accuser not running! (Baker: {baker}, "
                + f"Accuser: {accuser}) {Emoji.BlockMiss}"
            )

        return False


class Tezos(Chain):
    TYPE = "tezos"
    NAME = "tezos"
    BLOCKTIME = 60
    EP = "http://127.0.0.1:8732/"
    CUSTOM_TASKS = [TaskTezosValidatorProcesses]

    @staticmethod
    def detect(conf):
        try:
            Tezos(conf).getVersion()
            return True
        except:
            return False

    def getLatestVersion(self):
        raise Exception("Abstract getLatestVersion()")

    def getVersion(self):
        a = self.getCall("version")["version"]
        return f"v{a['major']}.{a['minor']}%s.0"

    def getHeight(self):
        return self.getCall("chains/main/blocks/head/helpers/current_level")["level"]

    def getBlockHash(self):
        return self.getCall("chains/main/blocks/head")["hash"]

    def getPeerCount(self):
        return len(self.getCall("network/peers"))

    def getNetwork(self):
        return self.getCall("network/version")["chain_name"]

    def isStaking(self):
        return False

    def isSynching(self):
        return False
