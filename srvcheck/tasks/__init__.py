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
