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


class NotificationLevel:
    NotDeclared = 0
    Info = 1
    Warning = 2
    Error = 3


class Emoji:
    Start = "\U0001F514"
    Disk = "\U0001F4BE"
    Stuck = "\U000026D4"
    Rel = "\U0001F4BF"
    Peers = "\U0001F198"
    Sync = "\U00002757"
    SyncOk = "\U00002705"
    PosUp = "\U0001F53C"
    PosDown = "\U0001F53D"
    BlockMiss = "\U0000274C"
    Health = "\U0001F6A8"
    Cpu = "\U000026A0"
    Ram = "\U0001F4A5"
    Proposal = "\U0001f4e5"
    Delinq = "\U0001F46E"
    LowBal = "\U0001F4B8"
    ActStake = "\U0001F37B"
    Leader = "\U0001F7E2"
    NoLeader = "\U0001F534"
    Orbiter = "\U0001F6F8"
    NoOrbiter = "\U00002B55"
    BlockProd = "\U000026CF"
    Slow = "\U0001f40c"
    Unreachable = "\U0001f50c"
    Updated = "\U0001F4E2"
    Floppy = "\U0001F4BE"


class Notification:
    def __init__(self, name):
        self.name = name
        self.providers = []

    def addProvider(self, p):
        self.providers.append(p)

    def append(self, s, level=NotificationLevel.NotDeclared):
        for x in self.providers:
            x.append(self.name + " " + s, level)

    def flush(self):
        for x in self.providers:
            x.flush()

    def send(self, st, level=NotificationLevel.NotDeclared):
        for x in self.providers:
            x.send(x.format(self.name, st), level)

    def sendPhoto(self, photo, level=NotificationLevel.NotDeclared):
        for x in self.providers:
            x.sendPhoto(photo, level)
