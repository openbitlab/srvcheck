def _linearize(e, cc = {}, xx = ''):
	for x in e:
		if type(e[x]) == dict:
			cc = _linearize(e[x], cc, (xx + '.' + x) if (xx != '') else x)
		else:
			cc[xx + ('.' if xx != '' else '') + x] = e[x]			
	return cc


class ConfItem:
	def __init__(self, name, defaultValue=None, cast=lambda y: y, description=None):
		self.name = name
		self.defaultValue = defaultValue
		self.cast = cast
		self.description = description


class ConfSet:
	items = {} 

	def __init__(self, conf):
		self.conf = _linearize(conf)

	@staticmethod
	def addItem(item: ConfItem):
		ConfSet.items[item.name] = item

	@staticmethod
	def setDefaultValue (name: str, value):
		ConfSet.items[name].defaultValue = value

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

	def getOrDefault(self, name: str, failSafe=True, cast=lambda y: y):
		if not (name in self.items):
			if failSafe:
				return None 
			raise Exception('missing definition for conf item %s' % name)
		
		v = None
		if not (name in self.conf):
			v = self.items[name].defaultValue
		else:
			v = self.conf[name]

		return cast(self.items[name].cast(v))


	def help():	
		d = {}

		for k in ConfSet.items:
			ks = k.split('.')
			ks = ['.'.join(ks[:-1]), ks[-1]]

			if len(ks) == 1:
				d[k] = ConfSet.items[k]
			else:
				if not (ks[0] in d):
					d[ks[0]] = {}
				d[ks[0]][ks[1]] = ConfSet.items[k]

		# dump d as an ini file
		s = ''
		for k in d:
			s += '[' + k + ']\n'
			for kk in d[k]:
				nl = kk + ' = ' 
				if d[k][kk].defaultValue:
					nl +=  str(d[k][kk].defaultValue)
				else:
					nl = '; ' + nl
					
				if d[k][kk].description:
					nl += '\t\t; ' + d[k][kk].description
					if d[k][kk].cast:
						nl += ' (' + str(d[k][kk].cast).split("'")[1] + ')'
				else:
					nl += '\t\t; ' + '(' + str(d[k][kk].cast).split("'")[1] + ')'

				s += nl + '\n'
			s += '\n'
		return s

