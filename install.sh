rpc_substrate_port=9933
rpc_cosmos_port=26657

check_docker () {
    check=$(echo $1 | grep docker)
    if [ ! -z "$check" ]
    then
	return true
	echo "It's in a docker container"
    else
	return false
    fi
}

print_help () {
    echo "Help output"
}

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--name)
      name="$2"
      shift # past argument
      shift # past value
      ;;
    -b|--blocktime)
      block_time="$2"
      shift # past argument
      shift # past value
      ;;
    -c|--chat)
      chat_id="$2"
      shift # past argument
      shift # past value
      ;;
    -t|--token)
      api_token="$2"
      shift # past argument
      shift # past value
      ;;
    -m|--mount)
      mount_point="$2"
      shift # past argument
      shift # past value
      ;;
    -v|--validator)
      val_address="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--space)
      min_space="$2"
      shift # past argument
      shift # past value
      ;;  
    -n|--validators-set)
      active_set="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      print_help
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

if [[ -z $name || -z $chat_id || -z $api_token || -z $mount_point ]]
then
    print_help
    exit 1
fi

rpc_substrate=$(lsof -i:$rpc_substrate_port)
#check if we're dealing with a substrate based blockchain
if [ ! -z "$rpc_substrate" ]
then 
    echo "It's a substrate based blockchain"
    check_docker "$rpc_substrate"
    if [ -d "$1" ]
    then
        echo "It's in a docker container"
    else
    	#wget substrate_monitor.sh
    fi
fi

rpc_cosmos=$(lsof -i:$rpc_cosmos_port)
#check if we're dealing with a cosmos based blockchain
if [ ! -z "$rpc_cosmos" ]
then 
    echo "It's a cosmos based blockchain"
    check_docker "$rpc_cosmos"
    if [ -d "$1" ]
    then
        echo "It's in a docker container"
    else
    	#wget tendermint_monitor.sh
    fi
fi
