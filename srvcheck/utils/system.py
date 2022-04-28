from .bash import Bash 

class Usage:
    diskSize = 0
    diskUsed = 0
    diskPercentageUsed = 0

    ramSize = 0
    ramUsed = 0
    ramFree = 0

    cpuUsage = 0

    def __str__(self):
        return 'Disk: %s %s %s; Ram: %s %s %s; CPU: %s' % (
            self.diskSize, self.diskUsed, self.diskPercentageUsed,
            self.ramSize, self.ramUsed, self.ramFree,
            self.cpuUsage)

    def __repr__(self):
        return self.__str__()
        
class Node:
    def getIP(self):
        """ Return IP address """
        return Bash('ip addr').value().split('inet ')[1].split('/')[-1]

    def getUsage(self):
        """ Returns an usage object """
        u = Usage()
        u.diskSize = Bash('df -h /').value().split('\n')[1].split()[1]
        u.diskUsed = Bash('df -h /').value().split('\n')[1].split()[2]
        u.diskPercentageUsed = Bash('df -h /').value().split('\n')[1].split()[4]

        u.ramSize = Bash('free -h').value().split('\n')[1].split()[1]
        u.ramUsed = Bash('free -h').value().split('\n')[1].split()[2]
        u.ramFree = Bash('free -h').value().split('\n')[1].split()[4]

        u.cpuUsage = Bash('top -b -n 1 | grep Cpu').value().split()[1] + '%'
        return u 