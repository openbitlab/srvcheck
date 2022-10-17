import json
from datetime import datetime


class Persistent:
	def __init__(self, fpath):
		self.fpath = fpath

		try:
			self.data = json.loads(open(fpath, 'r').read())
		except:
			self.data = {}

	def save(self):
		f = open(self.fpath, 'w')
		f.write(json.dumps(self.data))
		f.close()

	def set(self, k, v):
		self.data[k] = v
		self.save()

	def get(self, k):
		if k in self.data:
			return self.data[k]
		return None

	def timedAdd(self, k, v):
		if k in self.data:
			self.data[k] = []

		self.data[k].append([datetime.now().isoformat(), v])
		self.save()

