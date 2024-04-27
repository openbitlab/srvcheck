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

import unittest
import urllib.parse

from srvcheck.notification import Notification
from srvcheck.utils import ConfSet

from .mocks import MockNotification


class TestNotification(unittest.TestCase):
    def test_send(self):
        n = Notification("Test")
        mn = MockNotification(ConfSet({}))
        n.addProvider(mn)
        n.send("Hello WorldS!")
        self.assertEqual(
            mn.getFirstEvent()[0], urllib.parse.quote("#Test Hello WorldS!")
        )

    def test_sendPhoto(self):
        n = Notification("Test")
        mn = MockNotification(ConfSet({}))
        n.addProvider(mn)
        n.sendPhoto("/tmp/test.jpg")
        self.assertEqual(mn.getFirstEvent()[0], "Sending photo: /tmp/test.jpg")

    def test_append(self):
        n = Notification("Test")
        mn = MockNotification(ConfSet({}))
        n.addProvider(mn)
        n.append("Hello WorldA!")
        n.append("Hello WorldB!")
        n.flush()
        self.assertEqual(
            mn.getFirstEvent()[0],
            urllib.parse.quote("#Test Hello WorldA!\nTest Hello WorldB! "),
        )
