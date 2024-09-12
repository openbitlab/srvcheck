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

import configparser

from packaging_legacy import version

from ..notification import Emoji, NotificationLevel
from ..utils import Bash, ConfSet
from . import Task, hours, minutes


def versionCompare(current, latest):
    c_ver = (
        version.parse(current.split("-")[0])
        if isinstance(version.parse(current), version.LegacyVersion) is True
        else version.parse(current)
    )
    l_ver = (
        version.parse(latest.split("-")[0])
        if isinstance(version.parse(latest), version.LegacyVersion) is True
        else version.parse(latest)
    )

    if c_ver < l_ver:
        return -1
    elif c_ver > l_ver:
        return 1
    else:
        return 0


class TaskNewRelease(Task):
    def __init__(self, services):
        super().__init__("TaskNewRelease", services, minutes(15), hours(2))
        self.cf = self.s.conf.getOrDefault("configFile")

    @staticmethod
    def isPluggable(services):
        return True if services.conf.getOrDefault("chain.ghRepository") else False

    def run(self):
        confRaw = configparser.ConfigParser()
        confRaw.optionxform = str
        confRaw.read(self.cf)
        self.conf = ConfSet(confRaw)

        current = self.s.chain.getLocalVersion()
        latest = self.s.chain.getLatestVersion()

        if self.conf.getOrDefault("chain.localVersion") is None:
            Bash(f'sed -i -e "s/^localVersion =.*/localVersion = {current}/" {self.cf}')
            return False

        if versionCompare(current, latest) < 0:
            output = f"has new release: {latest} {Emoji.Rel}"
            if self.s.chain.TYPE == "solana":
                d_stake = self.s.chain.getDelinquentStakePerc()
                output += f"\n\tDelinquent Stake: {d_stake}%"
                output += "\n\tIt's recommended to upgrade when there's less than 5%% "
                output += "delinquent stake"
            return self.notify(output, level=NotificationLevel.Info)

        if versionCompare(current, self.conf.getOrDefault("chain.localVersion")) > 0:
            Bash(f'sed -i -e "s/^localVersion =.*/localVersion = {current}/" {self.cf}')
            self.notify(
                f'is now running latest version: {current.split("-")[0]} {Emoji.Updated}',
                level=NotificationLevel.Info,
            )
            self.s.notification.flush()

        return False
