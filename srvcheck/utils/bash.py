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

from subprocess import PIPE, Popen

SUBPROCESS_HAS_TIMEOUT = True


class Bash(object):
    def __init__(self, *args, **kwargs):
        self.p = None
        self.code = None
        self.stdout = None
        self.stderr = None
        self.bash(*args, **kwargs)

    def bash(self, cmd, env=None, stdout=PIPE, stderr=PIPE, timeout=None, sync=True):
        self.p = Popen(
            cmd, shell=True, stdout=stdout, stdin=PIPE, stderr=stderr, env=env
        )
        if sync:
            self.sync(timeout)
        return self

    def sync(self, timeout=None):
        kwargs = {"input": self.stdout}
        if timeout:
            kwargs["timeout"] = timeout
            if not SUBPROCESS_HAS_TIMEOUT:
                raise ValueError(
                    "Timeout given but subprocess doesn't support it. "
                    "Install subprocess32 and try again."
                )
        self.stdout, self.stderr = self.p.communicate(**kwargs)
        self.code = self.p.returncode
        return self

    def __repr__(self):
        return self.value()

    def __unicode__(self):
        return self.value()

    def __str__(self):
        return self.value()

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        return bool(self.value())

    def value(self):
        if self.stdout:
            return self.stdout.strip().decode(encoding="UTF-8")
        return ""

    def error(self):
        if self.stderr:
            return self.stderr.strip().decode(encoding="UTF-8")
        return ""
