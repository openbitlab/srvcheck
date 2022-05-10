from .task import Task, minutes, hours
from .taskchainstuck import TaskChainStuck
from .tasksystemusage import TaskSystemUsage
from .tasksystemdiskalert import TaskSystemDiskAlert
from .tasksystemcpualert import TaskSystemCpuAlert
from .taskchainlowpeer import TaskChainLowPeer
from .tasknewrelease import TaskNewRelease

TASKS = [ 
    TaskChainStuck, 
    TaskChainLowPeer,
    TaskSystemUsage, 
    TaskSystemDiskAlert, 
    TaskSystemCpuAlert,
    TaskNewRelease
]