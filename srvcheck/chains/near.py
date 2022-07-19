import json
from ..notification import Emoji
from .chain import Chain
from ..tasks import Task, seconds, hours, minutes

class Near (Chain):
    TYPE = "near"
    NAME = ""
    BLOCKTIME = 60
    EP = "http://localhost:3030/"
    CUSTOM_TASKS = [ ]

    @staticmethod
    def detect(conf):
        try:
            Near(conf).getVersion()
            return True
        except:
            return False

    def getPeerCount(self):
        return int(self.rpcCall("network_info")["result"]["num_active_peers"])

    def getHeight(self):
        return int(self.rpcCall("block", [{ "finality": "final" }]))

