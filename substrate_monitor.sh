#!/bin/bash
chat_id=
api_token=
name=
min_space=10000000
local_version=
block_time=60
git_api=

curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name monitor started" -d chat_id=$chat_id

while true; do
    a=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"chain_getBlockHash", "params":[], "id": 1 }' http://localhost:9933/ | jq '.result')
    sleep $block_time 
    b=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"chain_getBlockHash", "params":[], "id": 1 }' http://localhost:9933/ | jq '.result')
    echo $a
    echo $b

    if [[ "$a" == "$b" ]]
    then
        echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is stuck" -d chat_id=$chat_id
    else
        echo "$name Signaloff: OK"
    fi

    #check disk free
    avail=$(df --output=target,avail | grep -E "^/ +" | xargs | cut -d " " -f2)
    if [[ $avail -lt $min_space  ]]
    then
        echo "$name Singaloff: running out of space $((avail/1000000)) GB left"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is running out of space, $((avail/1000000)) GB left" -d chat_id=$chat_id
    else
        echo "$name Signaloff: OK"
    fi

    #check new version
    if [[ ! -z $git_api && ! -z $local_version ]]
    then
        git_version=$(curl -s -H 'Content-Type: application/json' $git_api |  jq -r ".tag_name")

        v1=$(echo $git_version | sed 's/[^0-9]*//g')
        v2=$(echo $local_version | sed 's/[^0-9]*//g')
        echo $v1 - $v2
	if [[ $v2 -ge $v1 ]]
        then
            echo "$name Signaloff: OK"
        else
            echo "$name Signaloff: FAIL"
            curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name has new release: $git_version" -d chat_id=$chat_id
        fi
    fi
done
