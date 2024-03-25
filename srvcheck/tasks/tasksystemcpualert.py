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

CPU_LIMIT = 90
TIME_SERIES_LENGTH = 2



class TaskSystemCpuAlert(Task):
    def __init__(self, services):
        super().__init__("TaskSystemCpuAlert", services, minutes(15), hours(2))
        self.timeSeries = []

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        usage = self.s.system.getUsage()
        cpuUsage = usage.cpuUsage
        
        self.timeSeries.append(cpuUsage)
        self.timeSeries = self.timeSeries[:TIME_SERIES_LENGTH]
        
        averageCPU = sum(self.timeSeries)/len(self.timeSeries)

        if averageCPU > CPU_LIMIT:
            return self.notify(
                "CPU average usage is above %d%% (%d%% in the last %d) %s"
                % (CPU_LIMIT, averageCPU, TIME_SERIES_LENGTH, Emoji.Cpu),
                level=NotificationLevel.Warning,
            )

        return False
