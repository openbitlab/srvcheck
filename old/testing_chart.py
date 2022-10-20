import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def toGB(size):
	return size / 1024 / 1024

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
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d'))
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
	color = "b"

	data2 = None
	label2 = ""
	color2 = "g"
	data_mod2 = lambda y: y

class PlotsConf:
	title = ""
	subplots = []
	fpath = ""

def savePlots(c, s1, s2):
	plt.clf()
	fig, axes = plt.subplots(s1, s2, figsize=(12, 7))
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
			list(map(lambda l: (sp.data_mod(l[1])), sp.data)), '-' + sp.color)

		if sp.data2:
			ax2.plot(list(map(lambda l: (dateutil.parser.isoparse(l[0])), sp.data2)), list(map(lambda l: (sp.data_mod2(l[1])), sp.data2)), sp.color2 + '-')
			ax2.set_ylabel(sp.label2, color=sp.color2)

		# ax.set_xlabel('Date')
		ax.set_ylabel(sp.label, color=sp.color)

		ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
		ax.xaxis.set_major_locator(mdates.MonthLocator())
	plt.savefig(c.fpath, bbox_inches="tight")



import os

def main():
	data = {"TaskSystemUsage_diskUsed": [["2022-10-17T09:53:34.015590", 9590444], ["2022-10-18T10:05:31.331664", 10458216], ["2022-10-18T12:57:31.290490", 10474220], ["2022-10-19T12:58:24.590939", 11362044]], "TaskSystemUsage_diskPercentageUsed": [["2022-10-17T09:53:34.015787", 45.0], ["2022-10-18T10:05:31.332466", 49.0], ["2022-10-18T12:57:31.290720", 49.0], ["2022-10-19T12:58:24.591911", 53.0]], "TaskSystemUsage_diskUsedByLog": [["2022-10-17T09:53:34.015885", 2362536], ["2022-10-18T10:05:31.332554", 2454320], ["2022-10-18T12:57:31.290829", 2367280], ["2022-10-19T12:58:24.592008", 2486844]], "TaskSystemUsage_ramUsed": [["2022-10-17T09:53:34.015992", 922120], ["2022-10-18T10:05:31.332621", 915488], ["2022-10-18T12:57:31.290918", 929564], ["2022-10-19T12:58:24.592080", 919964]]}


	pc = PlotsConf ()
	pc.title = "test - System usage"

	sp = SubPlotConf()
	sp.data = data['TaskSystemUsage_diskUsed'][-14::]
	sp.label = 'Used (GB)'
	sp.color = 'b'
	sp.data_mod = lambda y: toGB(y)

	# sp.data2 = data['TaskSystemUsage_diskPercentageUsed'][-14::]
	# sp.label2 = 'Used (%)'
	# sp.data_mod2 = lambda y: y

	pc.subplots.append(sp)

	sp = SubPlotConf()
	sp.data = data['TaskSystemUsage_diskPercentageUsed'][-14::]
	sp.label = 'Used (%)'
	sp.data_mod = lambda y: y
	sp.color = 'r'
	pc.subplots.append(sp)

	sp = SubPlotConf()
	sp.data = data['TaskSystemUsage_diskUsedByLog'][-14::]
	sp.label = 'Used by log (GB)'
	sp.data_mod = lambda y: toGB(y)
	sp.color = 'y'
	pc.subplots.append(sp)

	sp = SubPlotConf()
	sp.data = data['TaskSystemUsage_ramUsed'][-14::]
	sp.label = 'Ram used (GB)'
	sp.data_mod = lambda y: toGB(y)
	sp.color = 'g'
	pc.subplots.append(sp)


	pc.fpath = '/tmp/t.png'

	savePlots(pc, 2, 2)

	os.system('eog ' + pc.fpath)

main()