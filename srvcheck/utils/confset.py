class ConfItem:
	def __init__(self, name, defaultValue=None, type=str, description=None):
		self.name = name
		self.defaultValue = defaultValue
		self.type = type
		self.description = description

class ConfSet:
	def __init__(self, conf):
		self.conf = conf
		self.items = {}

	def addItem(self, item: ConfItem):
		if not (item.name in self.items):
			if item.defaultValue is None:
				raise Exception('default value is not set for item %s and value is missing in conf' % item.name)
			self.conf[item.name] = item.defaultValue

	def getOrDefault(self, name: str, failSafe=True):
		if not (name in self.items):
			if failSafe:
				return None 
			raise Exception('conf item %s not found' % name)

		return self.conf[name]