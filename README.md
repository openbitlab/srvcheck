# SRVCHECK

![Status](https://circleci.com/gh/openbitlab/srvcheck.svg?style=svg)

Supported ecosystems:
- Substrate
- Tendermint
- Lisk

## Install & Update

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/srvcheck/main/install.sh | bash -s -- -t <tg_chat_id> <tg_token> --branch <branch_name> -s <service_name>  <optional_flags>
```


## Configuration
Edit /etc/srvcheck.conf:

```
[notification.telegram]
enabled = true
apiToken = 
chatIds = 

[notification.dummy]
enabled = true

[chain]
name = test-chain
type = tendermint
service = validator-node.service
endpoint = localhost:26657
blockTime = 60
activeSet =
ghRepository = chain-org/reponame


[tendermint]
thresholdNotsigned = 
blockWindow = 

[version]
localVersion = 
gitApi = 

[tasks]
disabled = name_of_a_task_to_disable
```

## Usage
```
install --help
     --active-set <active_set_number> number of the validators in the active set (tendermint chain) [default is the number of active validators]
 -b  --block-time <time> expected block time [default is 60 seconds]
     --branch <name> name of the branch to use for the installation
     --git <git_api> git api to query the latest realease version installed
     --rel <version> release version installed (required for tendermint chain if git_api is specified)
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
 -n  --name <name> monitor name [default is the server hostname]
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window [default is 5 blocks missed out of the latest 100 blocks]
 -s  --service <name> service name of the node to monitor [required]
```
