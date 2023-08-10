import dateutil.parser
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime

def clearData(data):
    clean = 0
    for i in range(len(data) - 1):
        first_date = datetime.strptime(data[i][0].split("T")[0], '%Y-%m-%d')
        second_date = datetime.strptime(data[i + 1][0].split("T")[0], '%Y-%m-%d')
        if int(str(second_date - first_date).split(' ', maxsplit=1)[0]) > 5:
            clean = i + 1
    dataCleared = data[clean:]
    return dataCleared

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
    ax1.plot(
        list(map(lambda line: (dateutil.parser.isoparse(line[0])), c.data)),
        list(map(lambda line: (c.data_mod(line[1])), c.data)),
        "g-",
    )
    if c.data2:
        ax2.plot(
            list(map(lambda line: (dateutil.parser.isoparse(line[0])), c.data2)),
            list(map(lambda line: (c.data_mod2(line[1])), c.data2)),
            "b-",
        )
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax1.set_xlabel("Date")
    ax1.set_ylabel(c.label, color="g")
    if c.data2:
        ax2.set_ylabel(c.label2, color="b")

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
        self.set_bottom_y = False


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
        raise Exception(
            f"Invalid subplot number: expected {len(fig.get_axes())} got {len(c.subplots)}"
        )

    i = 0
    for ax in fig.get_axes():
        sp = c.subplots[i]
        i += 1
        ax.title.set_text(sp.name)

        if sp.data2 and not sp.share_y:
            ax2 = ax.twinx()

        ax.plot(
            list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data)),
            list(map(lambda line: (sp.data_mod(line[1])), sp.data)),
            "-" + sp.color,
        )
        ax.fill_between(
            list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data)),
            list(map(lambda line: (sp.data_mod(line[1])), sp.data)),
            facecolor=setColor(sp.color),
            interpolate=True,
            alpha=0.3,
        )

        if sp.data2 and not sp.share_y:
            ax2.plot(
                list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data2)),
                list(map(lambda line: (sp.data_mod2(line[1])), sp.data2)),
                sp.color2 + "-",
            )
            ax2.fill_between(
                list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data2)),
                list(map(lambda line: (sp.data_mod2(line[1])), sp.data2)),
                facecolor=setColor(sp.color2),
                interpolate=True,
                alpha=0.3,
            )
            ax2.set_ylabel(sp.label2, color=sp.color2)
        elif sp.data2 and sp.share_y:
            ax.plot(
                list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data2)),
                list(map(lambda line: (sp.data_mod2(line[1])), sp.data2)),
                sp.color2 + "-",
            )
            ax.fill_between(
                list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data2)),
                list(map(lambda line: (sp.data_mod2(line[1])), sp.data2)),
                facecolor=setColor(sp.color2),
                interpolate=True,
                alpha=0.8,
            )
            ax.fill_between(
                list(map(lambda line: (dateutil.parser.isoparse(line[0])), sp.data)),
                list(map(lambda line: (sp.data_mod(line[1])), sp.data)),
                facecolor=setColor(sp.color),
                interpolate=True,
                alpha=0.8,
            )

        # ax.set_xlabel('Date')
        ax.set_ylabel(sp.label, color=sp.color)

        if sp.set_bottom_y:
            ax.set_ylim(bottom=0)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.savefig(c.fpath, bbox_inches="tight")


def setColor(color):
    if color == "b":
        return "#58508d"
    elif color == "r":
        return "#ff6361"
    elif color == "y":
        return "#ffa600"
    elif color == "g":
        return "#558f4c"
    else:
        return "none"
