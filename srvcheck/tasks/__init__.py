from .task import Task, seconds, minutes, hours
from .taskchainstuck import TaskChainStuck
from .tasksystemusage import TaskSystemUsage
from .tasksystemdiskalert import TaskSystemDiskAlert
from .tasksystemcpualert import TaskSystemCpuAlert
from .tasksystemramalert import TaskSystemRamAlert
from .taskchainlowpeer import TaskChainLowPeer
from .tasknewrelease import TaskNewRelease
from .taskautoupdater import TaskAutoUpdater
from .taskchainunreachable import TaskChainUnreachable
from .taskchainsynching import TaskChainSynching

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
    TaskChainSynching
]
