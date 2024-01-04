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

import subprocess

from ..notification import Emoji, NotificationLevel
from . import Task, hours


def indexOf(a, v):
    try:
        return a.index(v)
    except ValueError:
        return -1


class TaskAPT(Task):
    def __init__(self, services):
        super().__init__("TaskAPT", services, hours(12), hours(24))

    @staticmethod
    def isPluggable(services):
        try:
            import apt  # noqa: F401

            subprocess.check_call(["apt", "--version"])
            return True
        except ModuleNotFoundError:            
            return False
        except subprocess.CalledProcessError:
            return False

    def run(self):
        import apt

        cache = apt.Cache()
        cache.update()
        security_updates = []
        updates = []

        for pkg in cache:
            if not pkg.is_installed:
                continue
            if pkg.is_upgradable and indexOf(pkg.candidate.uri, "security") != -1:
                security_updates.append(pkg.name)
            elif pkg.is_upgradable:
                updates.append(pkg.name)

        if security_updates:
            return self.notify(
                f"has {len(security_updates)} security updates pending "
                + f"({len(updates)+len(security_updates)} pending updates total): "
                + f'{", ".join(security_updates)} {Emoji.Floppy}',
                level=NotificationLevel.Info,
            )

        return False
