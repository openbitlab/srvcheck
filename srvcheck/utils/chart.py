import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class PlotConf:
	def __init__(self):
		self.name = ""
		self.data = []
		self.label = ""
		self.data_mod = lambda y: y

		self.data2 = None
		self.label2 = ""
		self.data_mod2 = lambda y: y

		self.fpath = ""

def savePlot(c):
	plt.clf()
	fig, ax1 = plt.subplots()

	ax2 = None
	if c.data2:
		ax2 = ax1.twinx()
	ax1.title.set_text(c.name)
	ax1.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), c.data)), list(map(lambda l: (c.data_mod(l[1])), c.data)), 'g-')
	if c.data2:
		ax2.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), c.data2)), list(map(lambda l: (c.data_mod2(l[1])), c.data2)), 'b-')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	ax1.set_xlabel('Date')
	ax1.set_ylabel(c.label, color='g')
	if c.data2:
		ax2.set_ylabel(c.label2, color='b')

	plt.savefig(c.fpath, bbox_inches="tight")


class SubPlotConf:
	def __init__(self):
		self.name = ""

		self.data = []
		self.label = ""
		self.data_mod = lambda y: y
		self.color = "b"

		self.data2 = None
		self.label2 = ""
		self.color2 = "g"
		self.data_mod2 = lambda y: y

		self.share_y = False

class PlotsConf:
	def __init__(self):
		self.title = ""
		self.subplots = []
		self.fpath = ""

def savePlots(c, s1, s2):
	plt.clf()
	fig, axes = plt.subplots(s1, s2, figsize=(12, 7))
	fig.suptitle(c.title)

	if len(fig.get_axes()) != len(c.subplots):
		raise Exception(f"Invalid subplot number: expected {len(fig.get_axes())} got {len(c.subplots)}")

	i = 0
	for ax in fig.get_axes():
		sp = c.subplots[i]
		i += 1
		ax.title.set_text(sp.name)

		if sp.data2 and not sp.share_y:
			ax2 = ax.twinx()
			
		ax.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), sp.data)),
			list(map(lambda l: (sp.data_mod(l[1])), sp.data)), '-' + sp.color)

		if sp.data2 and not sp.share_y:
			ax2.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), sp.data2)), list(map(lambda l: (sp.data_mod2(l[1])), sp.data2)), sp.color2 + '-')
			ax2.set_ylabel(sp.label2, color=sp.color2)
		elif sp.data2 and sp.share_y:
			ax.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), sp.data2)), list(map(lambda l: (sp.data_mod2(l[1])), sp.data2)), sp.color2 + '-')

		# ax.set_xlabel('Date')
		ax.set_ylabel(sp.label, color=sp.color)

		ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
		ax.xaxis.set_major_locator(mdates.MonthLocator())
	plt.savefig(c.fpath, bbox_inches="tight")