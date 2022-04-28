from .chain import Chain
import requests

class Tendermint (Chain):
    NAME = "Tendermint"
    BLOCKTIME = 15 

    def detect():
        """ Checks if the current server is running this chain """
        raise Exception('Abstract detect()')

    def getVersion(self):
        """ Returns software version """
        raise Exception('Abstract getVersion()')

    def getHeight(self):
        """ Returns the block height """
        raise Exception('Abstract getHeight()')

    def getNetwork(self):
        """ Returns network used """
        raise Exception('Abstract getNetwork()')

    def isStaking(self):
        """ Returns true if the node is staking """
        raise Exception('Abstract isStaking()')