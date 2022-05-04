name=$(hostname)

install() {
    check_docker=$(echo $1 | grep docker)
    if [ ! -z "$check_docker" ]
    then
        echo "It's in a docker container"
    else
        echo "[*] Installing monitor..."
        install_monitor
        echo "[+] Installed monitor!"
        echo "[*] Installing monitor service..."
        install_service "/usr/bin/python3 /root/setup.py"
        ## TODO
        echo "[+] Installed monitor service!"
    fi
}

print_help () {
    echo "Usage: install [options...]
     --active-set <active_set_number> number of the validators in the active set (tendermint chain) [default is the number of active validators]
 -b  --block-time <time> expected block time [default is 60 seconds]
     --git <git_api> git api to query the latest realease version installed
     --rel <version> release version installed (required for tendermint chain if git_api is specified)
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
 -n  --name <name> monitor name [default is the server hostname]
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window" [default is 5 blocks missed out of the latest 100 blocks]
}

install_monitor () {
    ## TODO
}

install_service () {
    wget -q http://raw.githubusercontent.com/openbitlab/srvcheck/main/old/node-monitor.service -O /etc/systemd/system/node-monitor.service ## TODO add args to change service name
    sed -i -e "s,^ExecStart=.*,ExecStart=$1,g" /etc/systemd/system/node-monitor.service
    systemctl daemon-reload 
    systemctl start node-monitor
    systemctl enable node-monitor
}

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--name)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
          name="$2"
      fi
      shift # past argument
      shift # past value
      ;;
    -b|--block-time)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
          block_time="$2"
      fi
      shift # past argument
      shift # past value
      ;;
    -t|--telegram)
      if [[ -z $2 || -z $3 ]]
      then
          print_help
          exit 1
      else
	  chat_id="$2"
          api_token="$3"
      fi
      shift # past argument
      shift # past value
      shift # past value
      ;;
    --git)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
	  git_api="$2"
      fi
      shift # past argument
      shift # past value
      ;;
    --rel)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
	  local_version="$2"
      fi
      shift # past argument
      shift # past value
      ;;
    --signed-blocks)
      threshold_notsigned="$2"
      block_window="$3"
      shift # past argument
      shift # past value
      shift # past value
      ;;
    --active-set)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
          active_set="$2"
      fi
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

if [[ -z $chat_id || -z $api_token ]]
then
    print_help
    exit 1
fi

rpc_substrate=$(lsof -i:$rpc_substrate_port)
#check if we're dealing with a substrate based blockchain
if [ ! -z "$rpc_substrate" ]
then 
    echo "It's a substrate based blockchain"
    install "$rpc_substrate"
fi

rpc_cosmos=$(lsof -i:$rpc_cosmos_port)
#check if we're dealing with a cosmos based blockchain
if [ ! -z "$rpc_cosmos" ]
then 
    echo "It's a cosmos based blockchain"
    install "$rpc_cosmos"
fi
