from srvcheck.chains.aptos import Aptos
from .chain import Chain
from .tendermint import Tendermint
from .substrate import Substrate
from .lisk import Lisk
from .tezos import Tezos
from .aptos import Aptos

CHAINS = [Substrate, Tendermint, Tezos, Lisk, Aptos]