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
    echo "Usage: install [options...]
     --active-set <active_set_number> number of the validators in the active set (tendermint chain)
 -b  --block-time <time> expected block time 
 -c  --chat-id <id> telegram chat id where the alerts will be sent [required]
     --min-space <space> minimum space that the specified mount point should have
 -m  --mount <fs> file system where the disk to be monitored (space available) is mounted [required]
 -n  --name <name> monitor name [required]
 -t  --token-api <token> telegram token api [required]
     --validator <address> validator address to monitor (tendermint chain)"
}

install_monitor () {
    wget -q http://<url>/$1.sh
    chmod +x substrate_monitor.sh
    sed -i -e "s/^name=.*/name=$name/" $1.sh
    sed -i -e "s/^chat_id=.*/chat_id=$chat_id/" $1.sh
    sed -i -e "s/^api_token=.*/api_token=$api_token/" $1.sh
    sed -i -e "s/^mount_point=.*/mount_point=$mount_point/" $1.sh
    #### Parse optionals flags
}

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--name)
      name="$2"
      shift # past argument
      shift # past value
      ;;
    -b|--block-time)
      block_time="$2"
      shift # past argument
      shift # past value
      ;;
    -c|--chat-id)
      chat_id="$2"
      shift # past argument
      shift # past value
      ;;
    -t|--token-api)
      api_token="$2"
      shift # past argument
      shift # past value
      ;;
    -m|--mount)
      mount_point="$2"
      shift # past argument
      shift # past value
      ;;
    --validator)
      val_address="$2"
      shift # past argument
      shift # past value
      ;;
    --min-space)
      min_space="$2"
      shift # past argument
      shift # past value
      ;;  
    --active-set)
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
    	install_monitor "substrate_monitor"
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
    	install_monitor "tendermint_monitor"
    fi
fi
