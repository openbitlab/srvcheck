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

import requests
from packaging_legacy import version
# from packaging import version

import srvcheck

from ..utils import Bash
from . import Task, hours, minutes


def versionCompare(v1, v2):
    v1 = (
        version.parse(v1.split("-")[0])
        if isinstance(version.parse(v1), version.LegacyVersion) is True
        else version.parse(v1)
    )
    v2 = (
        version.parse(v2.split("-")[0])
        if isinstance(version.parse(v2), version.LegacyVersion) is True
        else version.parse(v2)
    )

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


class TaskAutoUpdater(Task):
    def __init__(self, services):
        super().__init__("TaskAutoUpdater", services, minutes(60), hours(48))

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        nTag = (
            requests.get(
                "https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags"
            )
            .json()[-1]["ref"]
            .split("/")[-1]
            .split("v")[1]
        )

        if versionCompare(nTag, srvcheck.__version__) > 0:
            self.notify(f"New monitor version detected: v{nTag}")
            self.s.notification.flush()

            pr = Bash("pip install --dry-run requests").value()

            break_system_param = ""
            if pr.find("error: externally-managed-environment") != -1:
                break_system_param = "--break-ssytem-packages"

            inst_val = Bash(
                f"pip install --force-reinstall {break_system_param} "
                + f"git+https://github.com/openbitlab/srvcheck@v{nTag}"
            ).value()

            if inst_val.index("Successfully installed") != -1:
                self.notify("Srvcheck update succesfully, restarting...")
                Bash("systemctl restart node-monitor.service")
            else:
                self.notify(
                    "Srvcheck is unable to auto-update itself. Please check the logs."
                )
                print(inst_val)
