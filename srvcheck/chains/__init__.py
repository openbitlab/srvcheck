from .chain import Chain
from .tendermint import Tendermint
from .substrate import Substrate
from .lisk import Lisk
from .tezos import Tezos
from .solana import Solana

CHAINS = [Substrate, Tendermint, Tezos, Lisk, Solana]