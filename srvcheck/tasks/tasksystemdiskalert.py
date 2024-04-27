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
from ..utils import Bash, ConfItem, ConfSet, toGB
from . import Task, hours, minutes

ConfSet.addItem(
    ConfItem("system.log_size_threshold", 4, int, "threshold for log size in GB")
)
ConfSet.addItem(ConfItem("system.disk_limit", 90, int, "threshold for disk usage in %"))
ConfSet.addItem(
    ConfItem(
        "system.disk_limit_critical", 96, int, "critical threshold for disk usage in %"
    )
)


class TaskSystemDiskAlert(Task):
    def __init__(self, services):
        super().__init__("TaskSystemDiskAlert", services, minutes(15), hours(2))
        self.prevDiskSize = None

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        usage = self.s.system.getUsage()

        if self.prevDiskSize is None:
            self.prevDiskSize = usage.diskSize

        dl = self.s.conf.getOrDefault("system.disk_limit")
        cdl = self.s.conf.getOrDefault("system.disk_limit_critical")

        if usage.diskPercentageUsed > dl:
            is_critical = usage.diskPercentageUsed > cdl

            return self.notify(
                "disk usage is above %d%% (%d%%) (/var/log: %.1fG, /: %.1fG) %s"
                % (
                    dl,
                    usage.diskPercentageUsed,
                    toGB(usage.diskUsedByLog),
                    toGB(usage.diskUsed),
                    Emoji.Disk,
                ),
                level=(
                    NotificationLevel.Error
                    if is_critical
                    else NotificationLevel.Warning
                ),
                noCheck=True if is_critical else False,
            )

        if usage.diskSize > self.prevDiskSize:
            c = self.notify(
                "disk size increased (%.1fG -> %.1fG) %s"
                % (toGB(self.prevDiskSize), toGB(usage.diskSize), Emoji.Disk),
                True,
            )
            self.prevDiskSize = usage.diskSize
            return c

        return False

    def canRecover(self):
        return toGB(self.s.system.getUsage().diskUsedByLog) > self.s.conf.getOrDefault(
            "system.log_size_threshold"
        )

    def recover(self):
        Bash("truncate -s 0 /var/log/syslog")
        Bash("rm /var/log/syslog.*")
        Bash("rm -r /var/log/journal/*")
