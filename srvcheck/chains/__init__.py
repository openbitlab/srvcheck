from .chain import Chain, rpcCall
from .tendermint import Tendermint
from .substrate import Substrate

CHAINS = [Substrate, Tendermint]