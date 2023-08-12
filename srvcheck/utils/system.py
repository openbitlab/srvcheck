import datetime

import psutil
import requests

from .bash import Bash
from .confset import ConfItem, ConfSet

ConfSet.addItem(
    ConfItem("chain.mountPoint", defaultValue="/", description="Mount point")
)


def toGB(size):
    return size / 1024 / 1024 / 1024


def toMB(size):
    return size / 1024 / 1024


def toPrettySize(size):
    v = toMB(size)
    if v > 1024:
        return "%.1f GB" % (v / 1024.0)
    else:
        return "%d MB" % (int(v))


class SystemUsage:
    bootTime = ""
    diskSize = 0
    diskUsed = 0
    diskUsedByLog = 0
    diskPercentageUsed = 0

    ramSize = 0
    ramUsed = 0
    ramFree = 0

    cpuUsage = 0

    def __str__(self):
        return (
            "\n\tBoot time: %s\n\tDisk (size, used, %%): %.1fG %.1fG %d%% (/var/log: %.1fG)\n\tRam (size, used, free): %.1fG %.1fG %.1fG\n\tCPU: %d%%"  # noqa: 501
            % (
                datetime.datetime.fromtimestamp(self.bootTime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                toGB(self.diskSize),
                toGB(self.diskUsed),
                self.diskPercentageUsed,
                toGB(self.diskUsedByLog),
                toGB(self.ramSize),
                toGB(self.ramUsed),
                toGB(self.ramFree),
                self.cpuUsage,
            )
        )

    def __repr__(self):
        return self.__str__()


class System:
    def __init__(self, conf):
        self.conf = conf

    def getIP(self):
        """Return IP address"""
        return requests.get("http://zx2c4.com/ip").text.split("\n")[0]

    def getServiceUptime(self):
        serv = self.conf.getOrDefault("chain.service")
        if serv:
            return " ".join(
                Bash(f"systemctl status {serv}")
                .value()
                .split("\n")[2]
                .split(";")[-1]
                .strip()
                .split()[:-1]
            )
        return "na"

    def getUsage(self):
        """Returns an usage object"""
        u = SystemUsage()
        u.bootTime = psutil.boot_time()

        dd = psutil.disk_usage(self.conf.getOrDefault("chain.mountPoint"))

        u.diskSize = dd.total
        u.diskUsed = dd.used
        u.diskPercentageUsed = dd.percent
        u.diskUsedByLog = psutil.disk_usage("/var/log/").used

        mem = psutil.virtual_memory()
        u.ramSize = mem.total
        u.ramUsed = mem.used
        u.ramFree = mem.free

        u.cpuUsage = psutil.cpu_percent()
        return u
