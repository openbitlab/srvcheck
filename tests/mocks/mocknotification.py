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

from srvcheck.notification.notificationprovider import NotificationProvider


class MockNotification(NotificationProvider):
    def __init__(self, conf):
        self.events = []
        self.onNotifyHandler = lambda x: None
        super().__init__(conf)

    def onNotify(self, l):
        self.onNotifyHandler = l

    def send(self, st, level):
        self.events.append((st, level))
        self.onNotify(st)

    def sendPhoto(self, photo, level):
        f = f"Sending photo: {photo}"
        self.events.append((f, level))
        self.onNotify(f)

    def append(self, s, level):
        super().append(s, level)

    def getLastEvent(self):
        return self.events[-1]

    def getFirstEvent(self):
        return self.events[-1]
