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
	ax1.plot(list(map(lambda l: dateutil.parser.isoparse(l[0]), c.data)), list(map((lambda l: c.data_mod(l[1])), c.data)), 'g-')
	if c.data2:
		ax2.plot(list(map(lambda l: dateutil.parser.isoparse(l[0]), c.data2)), list(map((lambda l: c.data_mod2(l[1])), c.data2)), 'b-')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	ax1.set_xlabel('Date')
	ax1.set_ylabel(c.label, color='g')
	if c.data2:
		ax2.set_ylabel(c.label2, color='b')

	plt.savefig(c.fpath, bbox_inches="tight")