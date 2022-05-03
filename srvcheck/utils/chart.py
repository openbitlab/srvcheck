
from datetime import datetime, timedelta
import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# def savePlot(self):
# 	plt.clf()
# 	fig, ax1 = plt.subplots()

# 	ax2 = ax1.twinx()
# 	ax1.title.set_text('Border History')
# 	ax1.plot(list(map(lambda l: dateutil.parser.isoparse(l['d']), self.borderHistory)), list(map(lambda l: l['v'], self.borderHistory)), 'g-')
# 	ax2.plot(list(map(lambda l: dateutil.parser.isoparse(l['d']), self.borderHistory)), list(map(lambda l: l['s'] if 's' in l else 0, self.borderHistory)), 'b-')
# 	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
# 	plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
# 	ax1.set_xlabel('Date')
# 	ax1.set_ylabel('Border (LSK)', color='g')
# 	ax2.set_ylabel('102/101 diff (LSK)', color='b')

# 	plt.savefig('border_history.png', bbox_inches="tight")