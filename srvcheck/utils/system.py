from .bash import Bash
from .confset import ConfItem, ConfSet

ConfSet.addItem(ConfItem('chain.mountPoint', defaultValue="/", description='Mount point'))

def toGB(size):
	return size / 1024 / 1024
	
def toMB(size):
	return size / 1024

def toPrettySize(size):
	v = size / 1024
	if v > 1024:
		return '%.1f GB' % (v/1024.)
	else:
		return '%d MB' % (int(v))

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
		return Bash('ip addr').value().rsplit('inet ', 1)[-1].split('/')[0]

	def getServiceUptime(self):
		serv = self.conf.getOrDefault('chain.service')
		if serv:
			return " ".join(Bash(f"systemctl status {serv}").value().split('\n')[2].split(";")[-1].strip().split()[:-1])
		return 'na'

	def getUsage(self):
		""" Returns an usage object """
		u = SystemUsage()
		mp =  self.conf.getOrDefault('chain.mountPoint')
		u.uptime = Bash('uptime').value().split('up ')[1].split(',')[0]
		u.diskSize = int(Bash(f'df {mp}').value().split('\n')[1].split()[1])
		u.diskUsed = int(Bash(f'df {mp}').value().split('\n')[1].split()[2])
		u.diskPercentageUsed = float(Bash(f'df {mp}').value().split('\n')[1].split()[4].replace('%', ''))
		u.diskUsedByLog = int(Bash('du /var/log').value().rsplit('\n', 1)[-1].split()[0])

		u.ramSize = int(Bash('free').value().split('\n')[1].split()[1])
		u.ramUsed = int(Bash('free').value().split('\n')[1].split()[2])
		u.ramFree = int(Bash('free').value().split('\n')[1].split()[4])

		u.cpuUsage = float(Bash('top -b -n 1 | grep Cpu').value().split()[1].replace(',', '.'))
		return u
