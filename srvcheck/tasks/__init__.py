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

from .task import Task, hours, minutes, seconds  # noqa: F401
from .taskapt import TaskAPT  # noqa: F401
from .taskautoupdater import TaskAutoUpdater  # noqa: F401
from .taskchainlowpeer import TaskChainLowPeer  # noqa: F401
from .taskchainstuck import TaskChainStuck  # noqa: F401
from .taskchainsynching import TaskChainSynching  # noqa: F401
from .taskchainunreachable import TaskChainUnreachable  # noqa: F401
from .tasknewrelease import TaskNewRelease, versionCompare  # noqa: F401
from .tasksystemcpualert import TaskSystemCpuAlert  # noqa: F401
from .tasksystemdiskalert import TaskSystemDiskAlert  # noqa: F401
from .tasksystemramalert import TaskSystemRamAlert  # noqa: F401
from .tasksystemusage import TaskSystemUsage  # noqa: F401

TASKS = [
    TaskChainStuck,
    TaskChainLowPeer,
    TaskSystemUsage,
    TaskSystemDiskAlert,
    TaskSystemCpuAlert,
    TaskSystemRamAlert,
    TaskNewRelease,
    TaskAutoUpdater,
    TaskChainUnreachable,
    TaskChainSynching,
    TaskAPT,
]
