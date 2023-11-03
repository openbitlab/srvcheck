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

import time

from ..notification import Emoji, NotificationLevel
from . import Task, minutes


def elapsedToString(since):
    elapsed = time.time() - since
    if (elapsed / 60) > 60:
        elapsed = (
            str(int(elapsed / 60 / 60))
            + " hours and "
            + str(int(elapsed / 60 % 60))
            + " minutes"
        )
    elif (elapsed / 60) >= 1:
        elapsed = str(int(elapsed / 60)) + " minutes"
    else:
        elapsed = str(int(elapsed)) + " seconds"
    return elapsed


class TaskChainStuck(Task):
    def __init__(self, services):
        super().__init__("TaskChainStuck", services, minutes(5), minutes(5))
        self.prev = None
        self.since = None
        self.oc = 0

        try:
            self.s.chain.getBlockHash()
            self.method = self.s.chain.getBlockHash
        except:
            self.method = self.s.chain.getHeight

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        bh = self.method()

        if self.prev is None:
            self.prev = bh
            self.since = time.time()
            return False

        if bh == self.prev:
            self.oc += 1
            elapsed = elapsedToString(self.since)
            return self.notify(
                f"chain is stuck at block {bh} since {elapsed} ({self.oc}) {Emoji.Stuck}",
                level=NotificationLevel.Error,
            )

        if self.oc > 1:
            elapsed = elapsedToString(self.since)
            self.notify(
                f"chain come back in sync after {elapsed} ({self.oc}) {Emoji.SyncOk}",
                level=NotificationLevel.Warning,
            )

        self.prev = bh
        self.since = time.time()
        self.oc = 0
        return False
