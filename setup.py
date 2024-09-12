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

from setuptools import find_packages, setup

import srvcheck

setup(
    name="srvcheck",
    version=srvcheck.__version__,
    description="",
    author="Davide Gessa",
    setup_requires="setuptools",
    author_email="gessadavide@gmail.com",
    packages=[
        "srvcheck",
        "srvcheck.chains",
        "srvcheck.utils",
        "srvcheck.tasks",
        "srvcheck.notification",
    ],
    entry_points={
        "console_scripts": [
            "srvcheck=srvcheck.main:main",
            "srvcheck-defaultconf=srvcheck.main:defaultConf",
        ],
    },
    zip_safe=False,
    install_requires=[
        "requests",
        "psutil",
        "substrate-interface",
        "packaging_legacy",
        "python-dateutil",
        "matplotlib",
        "prometheus-client",
    ],
)
