rpc_substrate_port=9933
rpc_cosmos_port=26657
rpc_solana_port=8899
name=$(hostname)
branch="main"

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
        install_service "/usr/local/bin/srvcheck"
        echo "[+] Installed monitor service!"
    fi
}

print_help () {
    echo "Usage: install [options...]
     --active-set <active_set_number> number of the validators in the active set (tendermint chain) [default is the number of active validators]
 -b  --block-time <time> expected block time [default is 60 seconds]
     --branch <name> name of the branch to use for the installation [default is main]
     --git <git_api> git api to query the latest realease version installed
     --rel <version> release version installed (required for tendermint chain if git_api is specified)
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
 -n  --name <name> monitor name [default is the server hostname]
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window [default is 5 blocks missed out of the latest 100 blocks]
 -s  --service <name> service name of the node to monitor [required]
 -g  --gov enable checks on new governance proposals (tendermint)"
}

install_monitor () {
    config_file="/etc/srvcheck.conf"
    apt -qq update
    apt -qq install git python3-pip -y
    pip3 -q install git+https://github.com/openbitlab/srvcheck.git@$branch#egg=srvcheck
    wget -q https://raw.githubusercontent.com/openbitlab/srvcheck/$branch/conf/srvcheck.conf -O $config_file ## TODO add args to change service name
    sed -i -e "s/^apiToken =.*/apiToken = \"$api_token\"/" $config_file
    sed -i -e "s/^chatIds =.*/chatIds = [\"$chat_id\"]/" $config_file
    sed -i -e "s/^tagVersion =.*/tagVersion = $(curl https://api.github.com/repos/openbitlab/srvcheck/git/refs/tags -s | jq .[-1] | jq .ref | grep -oP '(?<=v).*?(?=\")')/" $config_file
    sed -i -e "s/^commit =.*/commit = $(curl https://api.github.com/repos/openbitlab/srvcheck/git/refs/heads/main -s | jq .object.sha -r | head -c 7)/" $config_file
    sed -i -e "s/^name =.*/name = $name/" $config_file
    sed -i -e "s/^service =.*/service = $service/" $config_file
    if [ ! -z "$block_time" ]
    then
        sed -i -e "s/^blockTime =.*/blockTime = $block_time/" $config_file
    fi
    if [ ! -z "$active_set" ]
    then
        sed -i -e "s/^activeSet =.*/activeSet = $active_set/" $config_file
    fi
    if [ ! -z "$git_api" ]
    then
        sed -i -e "s,^ghRepository =.*,ghRepository = $git_api,g" $config_file
    fi
    if [ ! -z "$local_version" ]
    then
        sed -i -e "s/^localVersion =.*/localVersion = $local_version/" $config_file
    fi
    if [[ ! -z "$threshold_notsigned" && ! -z "$block_window" ]]
    then
        sed -i -e "s/^thresholdNotsigned =.*/thresholdNotsigned = $threshold_notsigned/" $config_file
        sed -i -e "s/^blockWindow =.*/blockWindow = $block_window/" $config_file
    fi
    if [ "$enable_gov" = true ]
    then
        sed -i -r 's/(.TaskTendermintNewProposal?;|.TaskTendermintNewProposal?;?$)//' $config_file #enable checks on tendermint governance module
    fi
}

install_service () {
    wget -q https://raw.githubusercontent.com/openbitlab/srvcheck/$branch/conf/node-monitor.service -O /etc/systemd/system/node-monitor.service ## TODO add args to change service name
    sed -i -e "s,^ExecStart=.*,ExecStart=$1,g" /etc/systemd/system/node-monitor.service
    systemctl daemon-reload 
    systemctl start node-monitor
    systemctl enable node-monitor
}

POSITIONAL_ARGS=()

enable_gov = false

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
    --branch)
        if [[ -z $2 ]]
        then
            print_help
            exit 1
        else
            branch="$2"
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
    -s|--service)
        if [[ -z $2 ]]
        then
            print_help
            exit 1
        else
            service="$2"
        fi
        shift # past argument
        shift # past value
    ;;
    -g|--gov)
        if [[ -z $2 ]]
        then
            enable_gov = true
        else
            print_help
            exit 1
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

if [[ -z $chat_id || -z $api_token || -z $service ]]
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

rpc_solana=$(lsof -i:$rpc_solana_port)
#check if we're dealing with solana blockchain
if [ ! -z "$rpc_solana" ]
then 
    echo "It's solana blockchain"
    install "$rpc_solana"
fi
