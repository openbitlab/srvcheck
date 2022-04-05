#!/bin/bash
chat_id=
api_token=
name=
min_space=10000000
block_time=60
git_api=

start_e=$'\360\237\224\224'
disk_e=$'\360\237\222\276'
stuck_e=$'\342\233\224'
rel_e=$'\360\237\222\277'
peers_down_e=$'\360\237\206\230'
sync_e=$'\342\235\227'

curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name monitor started $start_e" -d chat_id=$chat_id

i_rel=0
sync_mod=$(( 3600 / $block_time ))
i_sync=$sync_mod
is_stuck=0
while true; do
    a=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"chain_getBlockHash", "params":[], "id": 1 }' http://localhost:9933/ | jq '.result')
    peers_a=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"system_health", "params":[], "id": 1}' http://localhost:9933 | jq '.result.peers')
    sleep $block_time 
    b=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"chain_getBlockHash", "params":[], "id": 1 }' http://localhost:9933/ | jq '.result')
    peers_b=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"system_health", "params":[], "id": 1}' http://localhost:9933 | jq '.result.peers')
    echo $a
    echo $b

    if [[ "$a" == "$b" ]]
    then
        echo "$name Signaloff: FAIL"
        is_stuck=1

        i_sync_mod=$(( $i_sync % $sync_mod ))
        if [[ $i_sync_mod -eq 0 ]]
        then 
            i_sync=0
            curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is stuck $stuck_e" -d chat_id=$chat_id
        fi
        i_sync=$(( $i_sync + 1 ))

    else
        echo "$name Signaloff: OK"
        i_sync=$sync_mod
        is_stuck=0
    fi

    #check disk free
    avail=$(df --output=target,avail | grep -E "^/ +" | xargs | cut -d " " -f2)
    if [[ $avail -lt $min_space  ]]
    then
        echo "$name Singaloff: running out of space $((avail/1000000)) GB left"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is running out of space, $((avail/1000000)) GB left $disk_e" -d chat_id=$chat_id
    else
        echo "$name Signaloff: OK"
    fi

    #check new version
    i_rel_mod=$(( $i_rel % 50 ))
    local_version=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"system_version", "params":[], "id": 1 }' http://localhost:9933/ | jq '.result')
    if [[ $i_rel_mod -eq 0 && ! -z $git_api && ! -z $local_version ]] 
    then
        i_rel=0
        git_version=$(curl -s -H 'Content-Type: application/json' $git_api |  jq -r ".tag_name")

        v1=$(echo $git_version | sed 's/\-.*//g' | sed 's/[^0-9]//g')
        v2=$(echo $local_version | sed 's/\-.*//g' | sed 's/[^0-9]//g')
        echo $v1 - $v2
	if [[ $v2 -ge $v1 ]]
        then
            echo "$name Signaloff: UPDATED"
        else
            echo "$name Signaloff: NEW VERSION AVAILABLE $git_version09oo"
            curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name has new release: $git_version $rel_e" -d chat_id=$chat_id
        fi
    fi
    i_rel=$(( $i_rel + 1 ))

    #check on chatching up flag
    catching_up=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"system_health", "params":[], "id": 1}' http://localhost:9933/ | jq '.result.isSyncing')
    if [[ "$catching_up" == "false" ]]
    then
        echo "$name Signaloff: OK"
    else
        echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is not sync $sync_e" -d chat_id=$chat_id
    fi

    #check on n_peers
    if [ $(($peers_a)) -gt $(($peers_b)) ]
    then
        echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$apiToken/sendMessage -d text="$name peers decreased from $peers_a to $peers_b $peers_down_e" -d chat_id=$chat_id
    else
        echo "$name Signaloff: OK"
    fi
done
