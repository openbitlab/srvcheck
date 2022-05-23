class NotificationLevel:
	NotDeclared = 0
	Debug = 1
	Info = 2
	Warning = 3
	Error = 4
	Critical = 5

class Emoji:
	Start 		= "\U0001F514"
	Disk 		= "\U0001F4BE"
	Stuck 		= "\U000026D4"
	Rel 		= "\U0001F4BF"
	Peers 		= "\U0001F198"
	Sync 		= "\U00002757"
	SyncOk 		= "\U000FEB4A"
	PosUp 		= "\U0001F53C"
	PosDown 	= "\U0001F53D"
	BlockMiss 	= "\U0000274C"
	Health 		= "\U0001F6A8"
	Cpu 		= "\U000026A0"
	Proposal	= "\U0001f4e5"
	Delinq      = "\U0001F46E"
	LowBal      = "\U0001F4B8"
	ActStake    = "\U0001F37B"

class Notification:
	def __init__(self, name):
		self.name = name
		self.providers = []

	def addProvider(self, p):
		self.providers.append(p)

	def append(self, s, level = NotificationLevel.NotDeclared):
		for x in self.providers:
			if level < x.LOG_LEVEL and level != NotificationLevel.NotDeclared:
				continue
			x.append(self.name + ' ' + s)

	def flush(self):
		for x in self.providers:
			x.flush()

	def send(self, st, level = NotificationLevel.NotDeclared):
		for x in self.providers:
			if level < x.LOG_LEVEL and level != NotificationLevel.NotDeclared:
				continue
			x.send(self.name + ' ' + st)

	def sendPhoto(self, photo):
		for x in self.providers:
			x.sendPhoto(photo)