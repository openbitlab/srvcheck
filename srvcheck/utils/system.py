from .bash import Bash 

def toGB(size):
    return size / 1024 / 1024

class SystemUsage:
    uptime = ''
    diskSize = 0
    diskUsed = 0
    diskUsedByLog = 0
    diskPercentageUsed = 0

    ramSize = 0
    ramUsed = 0
    ramFree = 0

    cpuUsage = 0

    def __str__(self):
        return '\n\tUptime: %s\n\tDisk (size, used, %%): %.1fG %.1fG %d%% (/var/log: %.1fG)\n\tRam (size, used, free): %.1fG %.1fG %.1fG\n\tCPU: %d%%' % (
            self.uptime,
            toGB(self.diskSize), toGB(self.diskUsed), self.diskPercentageUsed,
            toGB(self.diskUsedByLog),
            toGB(self.ramSize), toGB(self.ramUsed), toGB(self.ramFree),
            self.cpuUsage)

    def __repr__(self):
        return self.__str__()
        
class System:
    def __init__(self, conf):
        self.conf = conf

    def getIP(self):
        """ Return IP address """
        return Bash('ip addr').value().split('inet ')[-1].split('/')[0]

    def getServiceUptime(self):
        if 'service' in self.conf['chain']:
            return " ".join(Bash('systemctl status ' + self.conf['chain']['service']).value().split('\n')[1].split()[-3:-1])
        return 'na'

    def getUsage(self):
        """ Returns an usage object """
        u = SystemUsage()
        u.uptime = Bash('uptime').value().split('up ')[1].split(',')[0]
        u.diskSize = int(Bash('df /').value().split('\n')[1].split()[1])
        u.diskUsed = int(Bash('df /').value().split('\n')[1].split()[2])
        u.diskPercentageUsed = float(Bash('df /').value().split('\n')[1].split()[4].replace('%', ''))
        u.diskUsedByLog = int(Bash('du /var/log').value().split('\n')[-1].split()[0])

        u.ramSize = int(Bash('free').value().split('\n')[1].split()[1])
        u.ramUsed = int(Bash('free').value().split('\n')[1].split()[2])
        u.ramFree = int(Bash('free').value().split('\n')[1].split()[4])

        u.cpuUsage = float(Bash('top -b -n 1 | grep Cpu').value().split()[1])
        return u 