import json
from datetime import datetime, timedelta

import dateutil.parser


class Persistent:
    def __init__(self, fpath):
        self.fpath = fpath

        try:
            self.data = json.loads(open(fpath, "r").read())
        except:
            self.data = {}

    def save(self):
        f = open(self.fpath, "w")
        f.write(json.dumps(self.data))
        f.close()

    def set(self, k, v):
        self.data[k] = v
        self.save()

    def get(self, k):
        if k in self.data:
            return self.data[k]
        return None

    def getAveragedDiff(self, k, n=None):
        if k in self.data:
            if not n or n is None:
                n = len(self.data[k])

            if n is not None:
                dd = self.data[k][-n:]
                diffs = [dd[i + 1][1] - dd[i][1] for i in range(len(dd) - 1)]
            
            return None if len(diffs) == 0 else sum(diffs) / len(diffs)


    def getN(self, k, n):
        if k in self.data:
            return self.data[k][-n:]
        return None

    def timedAdd(self, k, v):
        if k not in self.data:
            self.data[k] = []

        self.data[k].append([datetime.now().isoformat(), v])
        self.save()

    def lastTime(self, k):
        if k not in self.data:
            return datetime.now() - timedelta(days=1)
        else:
            return dateutil.parser.isoparse(self.data[k][-1][0])

    def hasPassedNHoursSinceLast(self, k, n):
        return datetime.now() > (self.lastTime(k) + timedelta(hours=n))
