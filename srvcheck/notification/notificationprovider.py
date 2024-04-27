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

import urllib.parse


class NotificationProvider:
    def __init__(self, conf):
        self.conf = conf
        self.notifies = []

    def __del__(self):
        self.flush()

    def send(self, st, level):
        raise Exception("Abstract send()")

    def sendPhoto(self, photo, level):
        pass

    def append(self, s, level):
        self.notifies.append((s, level))

    def format(self, name, string):
        return urllib.parse.quote("#" + name + " " + string)

    def flush(self):
        if len(self.notifies) > 0:
            levelGroups = {}
            for s, level in self.notifies:
                if level not in levelGroups:
                    levelGroups[level] = []
                levelGroups[level].append(s)

            for level in levelGroups.keys():
                st = "\n".join(levelGroups[level])
                self.send(self.format(st, ""), level)

            self.notifies = []
