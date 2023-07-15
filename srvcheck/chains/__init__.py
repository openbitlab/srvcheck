from .amplitude import Amplitude  # noqa: F401
from .aptos import Aptos  # noqa: F401
from .astar import Astar  # noqa: F401
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
]
