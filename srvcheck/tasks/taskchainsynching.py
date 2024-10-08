# MIT License

# Copyright (c) 2021-2024 Openbitlab Team

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

from ..notification import Emoji, NotificationLevel
from . import Task, minutes


class TaskChainSynching(Task):
    def __init__(self, services):
        super().__init__("TaskChainSynching", services, minutes(5), minutes(5))
        self.prev = False

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        # TODO: make this code chain agnostic
        if self.s.chain.isSynching():
            self.prev = True
            if self.s.chain.TYPE == "Validator node":
                return self.notify(
                    f"chain is synching {Emoji.Slow}", level=NotificationLevel.Info
                )
            else:
                return self.notify(
                    f"is synching data availability samples {Emoji.Slow}",
                    level=NotificationLevel.Info,
                )
        elif self.prev:
            self.prev = False
            if self.s.chain.TYPE == "Validator node":
                return self.notify(
                    f"chain synched {Emoji.SyncOk}", level=NotificationLevel.Info
                )
            else:
                return self.notify(
                    f"synched all data availability samples {Emoji.SyncOk}",
                    level=NotificationLevel.Info,
                )

        return False
