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

import time

from ..notification import NotificationLevel


def seconds(m):
    return m


def minutes(m):
    return m * 60


def hours(h):
    return h * 60 * 60


class Task:
    def __init__(
        self,
        name,
        services,
        checkEvery=minutes(15),
        notifyEvery=minutes(15),
        recoverEvery=hours(2),
    ):
        self.name = name
        self.s = self.services = services
        self.checkEvery = checkEvery
        self.notifyEvery = notifyEvery
        self.recoverEvery = recoverEvery

        self.lastCheck = 0
        self.lastNotify = 0
        self.lastRecover = 0

    @staticmethod
    def isPluggable(services):
        """Returns true if the task can be plugged in"""
        raise Exception("Abstract isPluggable()")

    def shouldBeChecked(self):
        return (self.lastCheck + self.checkEvery) < time.time()

    def shouldBeNotified(self):
        return (self.lastNotify + self.notifyEvery) < time.time()

    def markChecked(self):
        self.lastCheck = time.time()

    def notify(self, nstr, noCheck=False, level=NotificationLevel.NotDeclared):
        if self.shouldBeNotified() or noCheck:
            self.lastNotify = time.time()
            self.s.notification.append(nstr, level)
            return True
        return False

    def run(self):
        raise Exception("Abstract run()")

    def shouldBeRecovered(self):
        return (self.lastRecover + self.recoverEvery) < time.time()

    def canRecover(self):
        return False

    def recover(self):
        return None

    def markRecovered(self):
        self.lastRecover = time.time()
