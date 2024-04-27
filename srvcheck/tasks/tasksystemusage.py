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

from ..notification import NotificationLevel
from ..utils import PlotsConf, SubPlotConf, cropData, savePlots, toGB, toPrettySize
from . import Task, hours


class TaskSystemUsage(Task):
    def __init__(self, services):
        super().__init__("TaskSystemUsage", services, hours(24), hours(24))

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        usage = self.s.system.getUsage()

        # Burnrate estimation
        rate = self.s.persistent.getAveragedDiff("TaskSystemUsage_diskUsed", 7)
        if rate:
            days = (usage.diskSize - usage.diskUsed) / rate
            sv = "\n\tDisk burnrate: %.1f days left (%s/day rate)" % (
                days,
                toPrettySize(rate),
            )
            out = str(usage) + sv
        else:
            out = str(usage)

        serviceUptime = self.s.system.getServiceUptime()
        self.notify(
            out + "\n\tService uptime: " + str(serviceUptime),
            level=NotificationLevel.Info,
        )

        # Saving historical data
        if self.s.persistent.hasPassedNHoursSinceLast(self.name + "_ramSize", 23):
            self.s.persistent.timedAdd(self.name + "_diskUsed", usage.diskUsed)
            self.s.persistent.timedAdd(
                self.name + "_diskPercentageUsed", usage.diskPercentageUsed
            )
            self.s.persistent.timedAdd(
                self.name + "_diskUsedByLog", usage.diskUsedByLog
            )
            self.s.persistent.timedAdd(self.name + "_ramUsed", usage.ramUsed)
            self.s.persistent.timedAdd(self.name + "_ramSize", usage.ramSize)

        # Sending a chart
        pc = PlotsConf()
        pc.title = self.s.conf.getOrDefault("chain.name") + " - System usage"

        sp = SubPlotConf()
        # sp.name = self.s.conf.getOrDefault('chain.name') + " - Disk"
        sp.data = cropData(self.s.persistent.getN(self.name + "_diskUsed", 30))
        sp.label = "Used (GB)"
        sp.data_mod = lambda y: toGB(y)
        sp.color = "b"

        # sp.data2 = data['TaskSystemUsage_diskPercentageUsed'][-14::]
        # sp.label2 = 'Used (%)'
        # sp.data_mod2 = lambda y: y
        pc.subplots.append(sp)

        sp = SubPlotConf()
        sp.data = cropData(
            self.s.persistent.getN(self.name + "_diskPercentageUsed", 30)
        )
        sp.label = "Used (%)"
        sp.data_mod = lambda y: y
        sp.color = "r"
        pc.subplots.append(sp)

        sp = SubPlotConf()
        sp.data = cropData(self.s.persistent.getN(self.name + "_diskUsedByLog", 30))
        sp.label = "Used by log (GB)"
        sp.data_mod = lambda y: toGB(y)
        sp.color = "g"
        pc.subplots.append(sp)

        sp = SubPlotConf()
        sp.data = cropData(self.s.persistent.getN(self.name + "_ramUsed", 30))
        sp.label = "Ram used (GB)"
        sp.data_mod = lambda y: toGB(y)
        sp.color = "y"

        sp.label2 = "Ram size (GB)"
        sp.data2 = cropData(self.s.persistent.getN(self.name + "_ramSize", 30))
        sp.data_mod2 = lambda y: toGB(y)
        sp.color2 = "r"

        sp.share_y = True

        pc.subplots.append(sp)

        pc.fpath = "/tmp/t.png"

        if len(self.s.persistent.getN(self.name + "_diskPercentageUsed", 30)) >= 2:
            savePlots(pc, 2, 2)
            self.s.notification.sendPhoto("/tmp/t.png")

        return False
