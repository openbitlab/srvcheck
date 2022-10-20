import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class PlotConf:
	name = ""
	data = []
	label = ""
	data_mod = lambda y: y

	data2 = None
	label2 = ""
	data_mod2 = lambda y: y

	fpath = ""

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
	name = ""
	data = []
	label = ""
	data_mod = lambda y: y

	data2 = None
	label2 = ""
	data_mod2 = lambda y: y

class PlotsConf:
	title = ""
	subplots = []
	fpath = ""

def savePlots(c, s1, s2):
	plt.clf()
	plt.figure(figsize=(12, 9))
	fig, axes = plt.subplots(s1, s2)
	fig.suptitle(c.title)

	if len(fig.get_axes()) != len(c.subplots):
		raise Exception("Invalid subplot number")

	i = 0
	for ax in fig.get_axes():
		sp = c.subplots[i]
		i += 1
		ax.title.set_text(sp.name)

		if sp.data2:
			ax2 = ax.twinx()
			
		ax.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), sp.data)),
			list(map(lambda l: (sp.data_mod(l[1])), sp.data)), '-')

		if sp.data2:
			ax2.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), sp.data2)), list(map(lambda l: (sp.data_mod2(l[1])), sp.data2)), 'b-')
			ax2.set_ylabel(sp.label2)

		ax.set_xlabel('Date')
		ax.set_ylabel(sp.label)

	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	plt.savefig(c.fpath)