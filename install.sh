rpc_substrate_port=9933
rpc_cosmos_port=26657
name=$(hostname)

check_docker () {
    check=$(echo $1 | grep docker)
    if [ ! -z "$check" ]
    then
	return 1
	echo "It's in a docker container"
    else
	return 0
    fi
}

print_help () {
    echo "Usage: install [options...]
     --active-set <active_set_number> number of the validators in the active set (tendermint chain)
 -b  --block-time <time> expected block time 
     --git <git_api> <local_version> git api to query the latest realease version and local version installed to check if there are new versions realeased
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
     --min-space <space> minimum space that the specified mount point should have
 -n  --name <name> monitor name
     --validator <address> validator address to monitor (tendermint chain)
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window"
}

install_monitor () {
    wget -q http://raw.githubusercontent.com/openbitlab/srvcheck/dev/$1.sh -O /root/$1.sh # to change in main when merged in the main branch ## TODO add args to change file path
    chmod +x /root/$1.sh
    sed -i -e "s/^name=.*/name=$name/" /root/$1.sh
    sed -i -e "s/^chat_id=.*/chat_id=\"$chat_id\"/" /root/$1.sh
    sed -i -e "s/^api_token=.*/api_token=\"$api_token\"/" /root/$1.sh
    if [ ! -z "$block_time" ]
    then
        sed -i -e "s/^block_time=.*/block_time=$block_time/" /root/$1.sh
    fi
    if [[ "$1" == "tendermint_monitor" && ! -z "$active_set"]]
    then
        sed -i -e "s/^active_set=.*/active_set=$active_set/" /root/$1.sh
    fi
    if [ ! -z "$min_space" ]
    then
        sed -i -e "s/^min_space=.*/min_space=$min_space/" /root/$1.sh
    fi
    if [[ "$1" == "tendermint_monitor" && ! -z "$val_address"]]
    then
        sed -i -e "s/^val_address=.*/val_address=$val_address/" /root/$1.sh
    fi
    if [[ ! -z "$git_api" && ! -z "$local_version" ]]
    then
        sed -i -e "s/^git_api=.*/git_api=$git_api/" /root/$1.sh
        sed -i -e "s/^local_version=.*/local_version=$local_version/" /root/$1.sh
    fi
    if [[ "$1" == "tendermint_monitor" && ! -z "$threshold_notsigned" && ! -z "$block_window" ]]
    then
        sed -i -e "s/^threshold_notsigned=.*/threshold_notsigned=$threshold_notsigned/" /root/$1.sh
        sed -i -e "s/^block_window=.*/block_window=$block_window/" /root/$1.sh
    fi
}

install_service () {
    wget -q http://raw.githubusercontent.com/openbitlab/srvcheck/dev/node-monitor.service -O /etc/systemd/system/node-monitor.service # to change in main when merged in the main branch ## TODO add args to change service name
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
      if [[ -z $2 || -z $3 ]]
      then
          print_help
          exit 1
      else
	  git_api="$2"
          local_version="$3"
      fi
      shift # past argument
      shift # past value
      shift # past value
      ;;
    --signed-blocks)
      threshold_notsigned="$2"
      block_window="$3"
      shift # past argument
      shift # past value
      shift # past value
      ;;
    --validator)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
          val_address="$2"
      fi
      shift # past argument
      shift # past value
      ;;
    --min-space)
      if [[ -z $2 ]]
      then
          print_help
          exit 1
      else
          min_space="$2"
      fi
      shift # past argument
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
    check_docker "$rpc_substrate"
    if [[ $1 -eq 1 ]]
    then
        echo "It's in a docker container"
    else
    	echo "[*] Installing substrate monitor..."
	install_monitor "substrate_monitor"
	echo "[+] Installed substrate monitor!"
	echo "[*] Installing substrate monitor service..."
	install_service "/bin/bash /root/substrate_monitor.sh"
    	echo "[+] Installed substrate monitor service!"
    fi
fi

rpc_cosmos=$(lsof -i:$rpc_cosmos_port)
#check if we're dealing with a cosmos based blockchain
if [ ! -z "$rpc_cosmos" ]
then 
    echo "It's a cosmos based blockchain"
    check_docker "$rpc_cosmos"
    if [[ $1 -eq 1 ]]
    then
        echo "It's in a docker container"
    else 	
    	echo "[*] Installing substrate monitor..."
	install_monitor "tendermint_monitor"
    	echo "[+] Installed tendermint monitor!"
	echo "[*] Installing tendermint monitor..."
	install_service "/bin/bash /root/tendermint_monitor.sh"
    	echo "[+] Installed tendermint monitor service!"
    fi
fi
