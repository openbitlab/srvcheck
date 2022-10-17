import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def savePlot(name, data, label, f):
	plt.clf()
	fig, ax1 = plt.subplots()

	#ax2 = ax1.twinx()
	ax1.title.set_text(name)
	ax1.plot(list(map(lambda l: dateutil.parser.isoparse(l[0]), data)), list(map(lambda l: l[1], data)), 'g-')
	# ax2.plot(list(map(lambda l: dateutil.parser.isoparse(l[0]), data)), list(map(lambda l: l['s'] if 's' in l else 0, self.borderHistory)), 'b-')
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
	ax1.set_xlabel('Date')
	ax1.set_ylabel(label, color='g')
	#ax2.set_ylabel('102/101 diff (LSK)', color='b')

	plt.savefig(f, bbox_inches="tight")