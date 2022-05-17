from .chain import Chain
from .tendermint import Tendermint
from .substrate import Substrate
from .solana import Solana

CHAINS = [Substrate, Tendermint, Solana]