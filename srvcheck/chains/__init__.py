from srvcheck.chains.aptos import Aptos
from .chain import Chain
from .tendermint import Tendermint
from .substrate import Substrate
from .lisk import Lisk
from .tezos import Tezos
from .solana import Solana
from .aptos import Aptos
from .near import Near

CHAINS = [Substrate, Tendermint, Tezos, Lisk, Solana, Aptos, Near, Dirk]
