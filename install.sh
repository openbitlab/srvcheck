rpc_substrate_port=9933
rpc_cosmos_port=26657

rpc_substrate=$(lsof -i:$rpc_substrate_port)
#check if we're dealing with a substrate based blockchain
if [ ! -z "$rpc_substrate" ]
then 
    echo "It's a substrate based blockchain"
    check=$(echo $rpc_substrate | grep docker)
    if [ ! -z "$check" ]
    then
	echo "It's in a docker container"
    fi
fi

rpc_cosmos=$(lsof -i:$rpc_cosmos_port)
#check if we're dealing with a cosmos based blockchain
if [ ! -z "$rpc_cosmos" ]
then 
    echo "It's a cosmos based blockchain"
    check=$(echo $rpc_cosmos | grep docker)
    if [ ! -z "$check" ]
    then
	echo "It's in a docker container"
    fi
fi
