def _linearize(e, cc = {}, xx = ''):
	for x in e:
		if type(e[x]) == dict:
			cc = _linearize(e[x], cc, (xx + '.' + x) if (xx != '') else x)
		else:
			cc[xx + '.' + x] = e[x]			
	return cc


class ConfItem:
	def __init__(self, name, defaultValue=None, type=str, description=None):
		self.name = name
		self.defaultValue = defaultValue
		self.type = type
		self.description = description


class ConfSet:
	def __init__(self, conf):
		self.conf = _linearize(conf)
		self.items = {}

	def addItem(self, item: ConfItem):
		if not (item.name in self.items):
			if item.defaultValue is None:
				raise Exception('default value is not set for item %s and value is missing in conf' % item.name)
			self.conf[item.name] = item.defaultValue

	def exists(self, name):
		return name in self.conf

	def retrieve (self, key, default=None, cast=lambda y: y):
		def iteOver(c, k):
			if len(k) == 1:
				out = c[k[0]] if k[0] in c else default
				return cast(out) if out != '' else default
			else:
				ke = k[0]
				k = k[1:]
				return iteOver (c[ke], k) if ke in self.conf else default
				
		if type(key) == str:
			key = key.split('.')

		return iteOver(self.conf, key)

	def getOrDefault(self, name: str, failSafe=True):
		if not (name in self.items):
			if failSafe:
				return None 
			raise Exception('conf item %s not found' % name)

		i = self.items[name]

		if i.type:
			return i.type(self.conf[name])
		else:
			return self.conf[name]