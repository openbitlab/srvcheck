# SRVCHECK

![Status](https://circleci.com/gh/openbitlab/srvcheck.svg?style=svg)

Srvcheck helps you to monitor blockchain nodes.

It supports these ecosystems:
- Substrate
- Tendermint
- Lisk
- Tezos
- Solana
- Aptos
- Near

It supports these notification outputs:
- stdout
- telegram chats 


And offer tasks for checking:
- TaskAutoUpdater
- TaskChainStuck
- TaskChainLowPeer
- TaskChainUnreachable
- TaskSystemCpuAlert
- TaskSystemUsage
- TaskNewRelease
- TaskSystemDiskAlert

Solana specific tasks:
- TaskSolanaHealthError
- TaskSolanaDelinquentCheck
- TaskSolanaBalanceCheck
- TaskSolanaLastVoteCheck
- TaskSolanaEpochActiveStake
- TaskSolanaLeaderSchedule
- TaskSolanaSkippedSlots

Aptos specific tasks:
- TaskAptosHealthError
- TaskAptosValidatorProposalCheck
- TaskAptosCurrentConsensusStuck

Tendermint specific tasks
- TaskTendermintBlockMissed
- TaskTendermintNewProposal
- TaskTendermintPositionChanged
- TaskTendermintHealthError

Substrate specific tasks:
- TaskSubstrateNewReferenda
- TaskBlockProductionCheck
- TaskBlockProductionReport

Near specific tasks:
- TaskNearBlockMissed
- TaskNearChunksMissed
- TaskCheckProposal

We suggest adding the binary of the node to the PATH in order to benefit from all the monitor features' 


## Install & Update

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/srvcheck/main/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -s <service_name> <optional_flags>
```

The install script can be customized with these flags:

```
install --help
     --active-set <active_set_number> number of the validators in the active set (tendermint chain) [default is the number of active validators]
 -b  --block-time <time> expected block time [default is 60 seconds]
     --branch <name> name of the branch to use for the installation [default is main]
 -c  --collator <address> enable checks on block production and collation (parachain)
     --git <git_api> git api to query the latest realease version installed
     --rel <version> release version installed (required for tendermint chain if git_api is specified)
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
     --mount <mount_point> mount point where the node is installed
 -n  --name <name> monitor name [default is the server hostname]
     --signed-blocks <max_misses> <blocks_window> max number of blocks not signed in a specified blocks window [default is 5 blocks missed out of the latest 100 blocks]
 -s  --service <name> service name of the node to monitor [required]
     --gov enable checks on new governance proposals (tendermint)
 -v  --verbose enable verbose installation
```


## Configuration
Edit /etc/srvcheck.conf:

```
; telegram notifications 
[notification.telegram]
enabled = true
apiToken = 
chatIds = 

; a dummy notification wich prints to stdout
[notification.dummy]
enabled = true

; chain settings
[chain]
; name to be displayed on notifications
name = 
; chain type (e.g. "tendermint" | "substrate")
type = 
; systemd service name
service = 
; endpoint uri, if different from default
endpoint = 
; block time
blockTime =
activeSet = 
thresholdNotsigned = 
blockWindow = 
; Github repository (org/repo)
ghRepository = 
; software version
localVersion = 
; parachain collator address
collatorAddress = 
; mount point
mountPoint = 

; task specific settings
[tasks]
; comma separated list of disabled tasks
disabled = TaskTendermintNewProposal
; enable auto recovery
autoRecover = true 
```

## Credits

Made with love by the [Openbitlab](https://openbitlab.com) team


## License

Read the LICENSE file.
