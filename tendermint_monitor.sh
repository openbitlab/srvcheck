#!/bin/bash
name=
chat_id=
api_token=
local_version=
block_time=60
git_api=
rpc_api=http://localhost:26657
val_address=
active_set=100
min_space=10000000
mount_point=
threshold_notsigned=5
block_window=20

curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name monitor started" -d chat_id=$chat_id

st_block=$(curl -s $rpc_api/status | jq '.result.sync_info.latest_block_height' | sed s/\"//)
st_block=$(echo $st_block | sed s/\"//)
starting_mod=0
if [ ! -z "$st_block" ]
then
    starting_mod=$(( $st_block % $block_window ))
fi

while true; do
    first_block=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"status", "params":[], "id": 1 }' $rpc_api | jq '.result.sync_info.latest_block_height')
    if [ ! -z $val_address ]
    then
        first_pos=$(curl -s $rpc_api/validators?per_page=$active_set | grep address | grep -n $val_address | cut -f1 -d ":")
    fi
    prev_peers=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"net_info", "params":[], "id": 1}' $rpc_api | jq '.result.n_peers'| cut -f2 -d '"')

    sleep $block_time

    new_block=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"status", "params":[], "id": 1 }' $rpc_api | jq '.result.sync_info.latest_block_height')
    if [ ! -z $val_address ]
    then
        new_pos=$(curl -s $rpc_api/validators?per_page=$active_set | grep address | grep -n $val_address | cut -f1 -d ":")
    fi
    new_peers=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"net_info", "params":[], "id": 1}' $rpc_api | jq '.result.n_peers'| cut -f2 -d '"')

    #check for missed blocks
    block_missed=0
    a=$(echo $first_block | sed s/\"//)
    a=$(echo $a | sed s/\"//)
    b=$(echo $new_block | sed s/\"//)
    b=$(echo $b | sed s/\"//)

    if [ ! -z $val_address ]
    then
	if [ ! -z $a ]
        then
            if [[ $a -ne $b ]]
            then
	        new_mod=$(( $a % $block_window ))
	        if [[ $new_mod == $starting_mod ]]
	        then
	            block_missed=0
	        fi
	        block_val_signed=$(curl -s $rpc_api/block?height=${a} | jq '.result.block.last_commit.signatures' | grep $val_address)
	        #check for block not signed
	        if [[ "$?" == "1" ]]
	        then 
    	            block_missed=$(($block_missed+1))
	        fi
	        #echo "Block: " $a - "missed: " $block_missed - "starting mod: " $starting_mod - "new mod: " $new_mod
            fi

            i=$(($a+1))
            while [[ $i -lt $b ]]; do
                #echo "Block: " $i
                block_val_signed=$(curl -s $rpc_api/block?height=${i} | jq '.result.block.last_commit.signatures' | grep $val_address)
	        #check for block not signed
	        if [[ "$?" == "1" ]]
	        then 
    	            block_missed=$(($block_missed+1))
	        fi
                i=$(($i+1))
            done
        fi

        if [ ! -z $b ]
        then
            new_mod=$(( $b % $block_time ))
            if [[ $new_mod == $starting_mod ]]
            then
	        block_missed=0
            fi
            block_val_signed=$(curl -s $rpc_api/block?height=${b} | jq '.result.block.last_commit.signatures' | grep $val_address)
            echo "Block: " $b

            #check for block not signed
            if [[ "$?" == "1" ]]
            then 
    	        block_missed=$(($block_missed+1))
            fi
        fi
    fi

    if [[ $block_missed > $threshold_notsigned ]]
    then
	echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name hasn't signed $block_missed of the blocks in the latest $block_window" -d chat_id=$chat_id
    fi

    #check on block height
    if [[ "$first_block" == "$new_block" ]]
    then
        echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name has block height stuck" -d chat_id=$chat_id
    else
        echo "$name Signaloff: OK"
    fi

    #check for error status
    health=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"health", "params":[], "id": 1 }' $rpc_api | jq '.error')

    if [[ "$health" == "null"  ]]
    then
        echo "$name Signaloff: OK"
    else
        echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name error: $health" -d chat_id=$chat_id
    fi

    #check new version
    if [[ ! -z $git_api && ! -z $local_version ]] 
    then
        git_version=$(curl -s -H 'Content-Type: application/json' $git_api |  jq -r ".tag_name")

        v1=$(echo $git_version | sed 's/[^0-9]*//g')
        v2=$(echo $local_version | sed 's/[^0-9]*//g')
        if [[ $v2 -ge $v1 ]]
        then
            echo "$name Signaloff: OK"
        else
            echo "$name Signaloff: FAIL"
            curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name has new release: $git_version" -d chat_id=$chat_id
        fi
    fi

    #check on chatching up flag
    catching_up=$(curl -s -H 'Content-Type: application/json' -d '{ "jsonrpc": "2.0", "method":"status", "params":[], "id": 1 }' $rpc_api | jq '.result.sync_info.catching_up')
    if [[ "$catching_up" == "false" ]]
    then
        echo "$name Signaloff: OK"
    else
        echo "$name Signaloff: FAIL"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is not sync" -d chat_id=$chat_id
    fi

    #check for position changes
    if [[ "$first_pos" == "$new_pos" ]]
    then
        echo "$name Signaloff: OK"
    else
        echo "$name Signaloff: position changed"
        curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name position changed to $new_pos" -d chat_id=$chat_id
    fi

    #check disk free
    if [ ! -z $mount_point ]
    then
	avail=$(df --output=source,avail | grep $mount_point | xargs | cut -d " " -f2)
        if [[ $avail -lt $min_space  ]]
        then
            echo "$name Singaloff: running out of space $((avail/1000000)) GB left"
            curl -s -X POST https://api.telegram.org/bot$api_token/sendMessage -d text="$name is running out of space, $((avail/1000000)) GB left" -d chat_id=$chat_id
        else
            echo "$name Signaloff: OK"
        fi
    fi
done
