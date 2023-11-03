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

from ..notification import Emoji, NotificationLevel
from . import Task, hours, minutes

RAM_LIMIT = 85


class TaskSystemRamAlert(Task):
    def __init__(self, services):
        super().__init__("TaskSystemRamAlert", services, minutes(15), hours(2))

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        usage = self.s.system.getUsage()
        ramUsed = round(usage.ramUsed / usage.ramSize * 100, 1)
        if ramUsed > RAM_LIMIT:
            return self.notify(
                "Ram usage is above %d%% (%d%%) %s" % (RAM_LIMIT, ramUsed, Emoji.Ram),
                level=NotificationLevel.Warning,
            )

        return False
