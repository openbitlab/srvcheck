# MIT License

# Copyright (c) 2021-2023 Openbitlab Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
