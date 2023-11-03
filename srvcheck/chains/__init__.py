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

from .amplitude import Amplitude  # noqa: F401
from .aptos import Aptos  # noqa: F401
from .astar import Astar  # noqa: F401
from .bridgeHubPolka import BridgeHubPolka  # noqa: F401
from .chain import Chain  # noqa: F401
from .lisk import Lisk  # noqa: F401
from .mangata import Mangata  # noqa: F401
from .moonbeam import Moonbeam  # noqa: F401
from .near import Near  # noqa: F401
from .solana import Solana  # noqa: F401
from .substrate import Polkasama, Substrate  # noqa: F401
from .t3rn import T3rn  # noqa: F401
from .tendermint import Tendermint  # noqa: F401
from .tezos import Tezos  # noqa: F401

CHAINS = [
    Substrate,
    Tendermint,
    Tezos,
    Lisk,
    Solana,
    Aptos,
    Near,
    Amplitude,
    Astar,
    Mangata,
    Moonbeam,
    Polkasama,
    T3rn,
    BridgeHubPolka,
]
