from .task import Task
from .taskchainstuck import TaskChainStuck
from .tasksystemusage import TaskSystemUsage
from .tasksystemdiskalert import TaskSystemDiskAlert
from .tasksystemcpualert import TaskSystemCpuAlert
from .taskchainlowpeer import TaskChainLowPeer

TASKS = [ 
    TaskChainStuck, 
    TaskChainLowPeer,
    
    TaskSystemUsage, 
    TaskSystemDiskAlert, 
    TaskSystemCpuAlert 
]