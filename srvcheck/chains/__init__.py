from .chain import Chain
from .tendermint import Tendermint
from .substrate import Substrate
from .lisk import Lisk
from .tezos import Tezos

CHAINS = [Substrate, Tendermint, Tezos, Lisk]