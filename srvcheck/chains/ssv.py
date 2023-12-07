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
        ssvStatus = list(filter(lambda x: "ssv_node_status" in x, out.text.split("\n")))[-1]
        return ssvStatus.split(" ")[-1]
