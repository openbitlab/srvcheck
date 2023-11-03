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

from typing import Any, Dict


def _linearize(e, cc={}, xx=""):
    for x in e:
        if isinstance(e[x], dict):
            cc = _linearize(e[x], cc, (xx + "." + x) if (xx != "") else x)
        else:
            cc[xx + ("." if xx != "" else "") + x] = e[x]
    return cc


class ConfItem:
    def __init__(self, name, defaultValue=None, cast=lambda y: y, description=None):
        self.name = name
        self.defaultValue = defaultValue
        self.cast = cast
        self.description = description


class ConfSet:
    items: Dict[str, Any] = {}

    def __init__(self, conf):
        self.conf = _linearize(conf)

    @staticmethod
    def addItem(item: ConfItem):
        ConfSet.items[item.name] = item

    @staticmethod
    def setDefaultValue(name: str, value):
        ConfSet.items[name].defaultValue = value

    @staticmethod
    def getDefaultValue(name: str):
        return ConfSet.items[name].defaultValue

    def exists(self, name):
        items = []
        for x in self.conf.items():
            if len(x) > 0:
                for k in x[1]:
                    items.append(f"{x[0]}.{k}")
        return name in self.conf or name in items

    def retrieve(self, key, default=None, cast=lambda y: y):
        def iteOver(c, k):
            if len(k) == 1:
                out = c[k[0]] if k[0] in c else default
                return cast(out) if out != "" else default
            else:
                ke = k[0]
                k = k[1:]
                return iteOver(c[ke], k) if ke in self.conf else default

        if isinstance(key, str):
            key = key.rsplit(".", 1)

        return iteOver(self.conf, key)

    def getOrDefault(self, name: str, failSafe=True, cast=lambda y: y):
        if name not in self.items:
            if failSafe:
                return None
            raise Exception(f"missing definition for conf item {name}")

        v = None
        if not self.exists(name):
            v = self.getDefaultValue(name)
        else:
            v = self.retrieve(name, self.getDefaultValue(name))

        if v is None:
            return None

        return cast(self.items[name].cast(v))

    @staticmethod
    def help():
        d = {}

        for k, v in ConfSet.items.items():
            ks = k.split(".")
            ks = [".".join(ks[:-1]), ks[-1]]

            if len(ks) == 1:
                d[k] = v
            else:
                if ks[0] not in d:
                    d[ks[0]] = {}
                d[ks[0]][ks[1]] = v

        # dump d as an ini file
        s = ""
        for k, v in d.items():
            s += "[" + k + "]\n"
            for kk in v:
                nl = kk + " = "
                if v[kk].defaultValue:
                    nl += str(v[kk].defaultValue)
                else:
                    nl = "; " + nl

                if v[kk].description:
                    nl += "\t\t; " + v[kk].description
                    if v[kk].cast:
                        cst = str(v[kk].cast)
                        if cst.find("'") != -1:
                            nl += " (" + cst.split("'")[1] + ")"
                else:
                    nl += "\t\t; " + "(" + str(v[kk].cast).split("'")[1] + ")"

                s += nl + "\n"
            s += "\n"
        return s
