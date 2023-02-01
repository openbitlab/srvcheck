from srvcheck.chains.aptos import Aptos
from .chain import Chain
from .tendermint import Tendermint
from .substrate import Substrate
from .lisk import Lisk
from .tezos import Tezos
from .solana import Solana
from .aptos import Aptos
from .near import Near
from .amplitude import Amplitude
from .astar import Astar
from .mangata import Mangata
from .moonbeam import Moonbeam

CHAINS = [Substrate, Tendermint, Tezos, Lisk, Solana, Aptos, Near, Amplitude, Astar, Mangata, Moonbeam]
