from substrateinterface import SubstrateInterface

from srvcheck.tasks.task import hours, minutes

from ..notification import Emoji
from ..tasks import Task
from ..utils import Bash, ConfItem, ConfSet, PlotsConf, SubPlotConf, savePlots
from .chain import Chain

ConfSet.addItem(ConfItem("chain.validatorAddress", description="Validator address"))


class SubstrateInterfaceWrapper(SubstrateInterface):
    def query(self, **kwargs):
        try:
            return super(SubstrateInterface, self).query(**kwargs)
        except (WebSocketConnectionClosedException, ConnectionRefusedError,
                WebSocketBadStatusException, BrokenPipeError, SubstrateRequestException) as e:
            self.connect_websocket()

    def rpc_request(self, **kwargs):
        try:
            return super(SubstrateInterface, self).rpc_request(**kwargs)
        except (WebSocketConnectionClosedException, ConnectionRefusedError,
                WebSocketBadStatusException, BrokenPipeError, SubstrateRequestException) as e:
            self.connect_websocket()


class TaskSubstrateNewReferenda(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=60 * 10 * 60):
        super().__init__("TaskSubstrateNewReferenda", services, checkEvery, notifyEvery)
        self.prev = None

    @staticmethod
    def getCount(si):
        return si.query(
            module="Referenda", storage_function="ReferendumCount", params=[]
        ).value

    @staticmethod
    def isPluggable(services):
        if services.chain.getNetwork() in ["Kusama", "Polkadot"]:
            return True
        return False

    def run(self):
        net = self.s.chain.getNetwork()
        count = self.getCount(self.s.chain.sub_iface)

        if self.prev is None:
            self.prev = count
            return False

        if count > self.prev:
            self.prev = count
            return self.notify(
                f"New referendum found on {net}: {count - 1} {Emoji.Proposal}"
            )


class TaskSubstrateReferendaVotingCheck(Task):
    def __init__(self, services, checkEvery=hours(1), notifyEvery=60 * 10 * 60):
        super().__init__(
            "TaskSubstrateReferendaVotingCheck", services, checkEvery, notifyEvery
        )
        self.prev = None

    @staticmethod
    def isPluggable(services):
        if services.chain.getNetwork() in ["Kusama", "Polkadot"]:
            return services.conf.exists("chain.validatorAddress")
        return False

    def run(self):
        si = self.s.chain.sub_iface
        net = self.s.chain.getNetwork()
        validator = self.s.conf.getOrDefault("chain.validatorAddress")
        result = si.query_map(
            module="ConvictionVoting",
            storage_function="VotingFor",
            params=[validator],
            max_results=1000,
        )
        count = TaskSubstrateNewReferenda.getCount(si)

        vt = {}
        vtl = []
        for votes in map(
            lambda y: list(y.values())[0]["votes"], map(lambda y: y[1].value, result)
        ):
            for n, v in votes:
                vt[n] = v
                vtl.append(n)
        nv = []
        for x in range(count - 16, count):
            if x in vt:
                continue

            c = si.query(
                module="Referenda",
                storage_function="ReferendumInfoFor",
                params=[x],
            ).value
            if "Approved" not in c and "Rejected" not in c:
                nv.append(x)

        if len(nv) > 0:
            return self.notify(
                f"Validator {validator} is not voting on {net} Referenda {str(nv)} {Emoji.Proposal}"
            )


class TaskSubstrateRelayChainStuck(Task):
    def __init__(self, services, checkEvery=30, notifyEvery=60 * 5):
        super().__init__(
            "TaskSubstrateRelayChainStuck", services, checkEvery, notifyEvery
        )
        self.prev = None

    @staticmethod
    def isPluggable(services):
        return services.chain.isParachain()

    def run(self):
        if self.prev is None:
            self.prev = self.s.chain.getRelayHeight()
        elif self.prev == self.s.chain.getRelayHeight():
            return self.notify(f"relay is stuck at block {self.prev} {Emoji.Stuck}")
        return False


class TaskSubstrateBlockProductionReport(Task):
    def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(1)):
        super().__init__(
            "TaskSubstrateBlockProductionReport", services, checkEvery, notifyEvery
        )
        self.prev = None
        self.lastBlockChecked = None
        self.totalBlockChecked = 0
        self.oc = 0

    @staticmethod
    def isPluggable(services):
        return not services.chain.isParachain()

    def run(self):
        era = self.s.chain.getEra()
        if self.prev is None:
            self.prev = era

        if self.s.chain.isStaking():
            currentBlock = self.s.chain.getHeight()
            blocksToCheck = [
                b
                for b in self.s.chain.getExpectedBlocks()
                if b <= currentBlock
                and (self.lastBlockChecked is None or b > self.lastBlockChecked)
            ]
            for b in blocksToCheck:
                a = self.s.chain.getBlockAuthor(b)
                collator = self.s.conf.getOrDefault("chain.validatorAddress")
                if a.lower() == collator.lower():
                    self.oc += 1
                self.lastBlockChecked = b
                self.totalBlockChecked += 1

        if self.prev != era:
            self.s.persistent.timedAdd(
                self.s.conf.getOrDefault("chain.name") + "_sessionBlocksProduced",
                self.prev,
            )
            self.s.persistent.timedAdd(
                self.s.conf.getOrDefault("chain.name") + "_blocksChecked",
                self.totalBlockChecked,
            )
            self.prev = era
            perc = 0
            if self.totalBlockChecked > 0:
                perc = self.oc / self.totalBlockChecked * 100
                self.totalBlockChecked = 0
                self.s.persistent.timedAdd(
                    self.s.conf.getOrDefault("chain.name") + "_blocksProduced", self.oc
                )
                self.s.persistent.timedAdd(
                    self.s.conf.getOrDefault("chain.name")
                    + "_blocksPercentageProduced",
                    perc,
                )
                self.oc = 0
        return False


class TaskSubstrateBlockProductionReportParachain(Task):
    def __init__(self, services, checkEvery=minutes(10), notifyEvery=hours(1)):
        super().__init__(
            "TaskSubstrateBlockProductionReportParachain",
            services,
            checkEvery,
            notifyEvery,
        )
        self.prev = None
        self.prevBlock = None
        self.lastBlockChecked = None
        self.totalBlockChecked = 0
        self.oc = 0

    @staticmethod
    def isPluggable(services):
        return services.chain.isParachain()

    def run(self):
        session = self.s.chain.getSessionWrapped()

        if self.prev is None:
            self.prev = session

        if self.s.chain.isCollating():
            startingRoundBlock = self.s.chain.getStartingRoundBlock()
            currentBlock = self.s.chain.getHeight()
            blocksToCheck = [
                b
                for b in self.s.chain.getExpectedBlocks()
                if b <= currentBlock
                and (self.lastBlockChecked is None or b > self.lastBlockChecked)
                and b >= startingRoundBlock
            ]
            for b in blocksToCheck:
                a = self.s.chain.getBlockAuthor(b)
                collator = self.s.conf.getOrDefault("chain.validatorAddress")
                if a.lower() == collator.lower():
                    self.oc += 1
                self.lastBlockChecked = b
                self.totalBlockChecked += 1

        if self.prev != session:
            self.s.persistent.timedAdd(
                self.s.conf.getOrDefault("chain.name") + "_sessionBlocksProduced",
                self.prev,
            )
            self.s.persistent.timedAdd(
                self.s.conf.getOrDefault("chain.name") + "_blocksChecked",
                self.totalBlockChecked,
            )
            self.prev = session
            perc = 0
            if self.totalBlockChecked > 0:
                perc = self.oc / self.totalBlockChecked * 100
                self.totalBlockChecked = 0
            self.s.persistent.timedAdd(
                self.s.conf.getOrDefault("chain.name") + "_blocksProduced", self.oc
            )
            self.s.persistent.timedAdd(
                self.s.conf.getOrDefault("chain.name") + "_blocksPercentageProduced",
                perc,
            )
            self.oc = 0
        return False


class TaskSubstrateBlockProductionReportCharts(Task):
    def __init__(self, services, checkEvery=hours(24), notifyEvery=hours(24)):
        super().__init__(
            "TaskSubstrateBlockProductionReportCharts",
            services,
            checkEvery,
            notifyEvery,
        )

    @staticmethod
    def isPluggable(services):
        return True

    def run(self):
        pc = PlotsConf()
        pc.title = self.s.conf.getOrDefault("chain.name") + " - Block production"

        sp = SubPlotConf()
        sp.data = self.s.persistent.getN(
            self.s.conf.getOrDefault("chain.name") + "_blocksProduced", 30
        )
        sp.label = "Produced"
        sp.data_mod = lambda y: y
        sp.color = "y"

        sp.label2 = "Produced"
        sp.data2 = self.s.persistent.getN(
            self.s.conf.getOrDefault("chain.name") + "_blocksChecked", 30
        )
        sp.data_mod2 = lambda y: y
        sp.color2 = "r"

        sp.share_y = True
        sp.set_bottom_y = True
        pc.subplots.append(sp)

        sp = SubPlotConf()
        sp.data = self.s.persistent.getN(
            self.s.conf.getOrDefault("chain.name") + "_blocksPercentageProduced", 30
        )
        sp.label = "Produced (%)"
        sp.data_mod = lambda y: y
        sp.color = "b"

        sp.set_bottom_y = True
        pc.subplots.append(sp)

        pc.fpath = "/tmp/p.png"

        lastSessions = self.s.persistent.getN(
            self.s.conf.getOrDefault("chain.name") + "_sessionBlocksProduced", 30
        )
        if lastSessions and len(lastSessions) >= 3:
            savePlots(pc, 1, 2)
            self.s.notification.sendPhoto("/tmp/p.png")


class Substrate(Chain):
    TYPE = "substrate"
    NAME = ""
    BLOCKTIME = 15
    EP = "http://localhost:9933/"
    CUSTOM_TASKS = [
        TaskSubstrateRelayChainStuck,
        TaskSubstrateNewReferenda,
        TaskSubstrateReferendaVotingCheck,
        TaskSubstrateBlockProductionReport,
        TaskSubstrateBlockProductionReportCharts,
    ]

    def __init__(self, conf):
        super().__init__(conf)
        self.sub_iface = SubstrateInterfaceWrapper(url=self.EP)
        self.rpcMethods = self.sub_iface.rpc_request("rpc_methods", [])["result"][
            "methods"
        ]

    def rpcCall(self, method, params=[]):
        if method in self.rpcMethods:
            return self.sub_iface.rpc_request(method, params)["result"]
        return None

    @staticmethod
    def detect(conf):
        try:
            Substrate(conf).getVersion()
            return not Substrate(conf).isParachain()
        except:
            return False

    def getVersion(self):
        return self.rpcCall("system_version")

    def getHeight(self):
        return int(self.rpcCall("chain_getHeader", [self.getBlockHash()])["number"], 16)

    def getBlockHash(self):
        return self.rpcCall("chain_getBlockHash")

    def getPeerCount(self):
        return int(self.rpcCall("system_health")["peers"])

    def getNetwork(self):
        return self.rpcCall("system_chain")

    def isStaking(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        era = self.getEra()
        result = self.sub_iface.query(
            module="Staking", storage_function="ErasStakers", params=[era, collator]
        )
        if result.value["total"] > 0:
            return True

    def isSynching(self):
        c = self.rpcCall("system_syncState")["currentBlock"]
        h = self.getHeight()
        return abs(c - h) > 32

    def getRelayHeight(self):
        result = self.sub_iface.query(
            module="ParachainSystem", storage_function="ValidationData", params=[]
        )
        return result.value["relay_parent_number"]

    def getParachainId(self):
        result = self.sub_iface.query(
            module="ParachainInfo", storage_function="ParachainId", params=[]
        )
        return result.value

    def getNodeName(self):
        return self.rpcCall("system_name")

    def isParachain(self):
        try:
            self.getParachainId()
            return True
        except:
            return False

    def getSession(self):
        result = self.sub_iface.query(
            module="Session", storage_function="CurrentIndex", params=[]
        )
        return result.value

    def getEra(self):
        result = self.sub_iface.query(
            module="Staking", storage_function="ActiveEra", params=[]
        )
        return result.value["index"]

    def isValidator(self):
        collator = self.conf.getOrDefault("chain.validatorAddress")
        if collator:
            result = self.sub_iface.query(
                module="Session", storage_function="QueuedKeys", params=[]
            )
            for v in result.value:
                if v[0].lower() == f"{collator}".lower():
                    return True
        return False

    def getExpectedBlocks(self, since=60):
        serv = self.conf.getOrDefault("chain.service")
        if serv:
            blocks = (
                Bash(
                    f"journalctl -u {serv} --no-pager --since '{since} min ago' | grep -Eo "
                    + "'Prepared block for proposing at [0-9]+' | sed 's/[^0-9]'//g"
                )
                .value()
                .split("\n")
            )
            blocks = [int(b) for b in blocks if b != ""]
            return blocks
        return []

    def getBlockAuthor(self, block):
        return self.checkAuthoredBlock(block)

    def getSeals(self, block):
        seals = (
            Bash(
                "grep -Eo 'block for proposal at {}. Hash now 0x[0-9a-fA-F]+' /var/log/syslog --text | rev | cut -d ' ' -f1 | rev".format(  # noqa: E501
                    block
                )
            )
            .value()
            .split("\n")
        )
        return seals

    def checkAuthoredBlock(self, block):
        bh = self.rpcCall("chain_getBlockHash", [block])
        seals = self.getSeals(block)
        for b in seals:
            if b == bh:
                return self.conf.getOrDefault("chain.validatorAddress")
        return "0x0"

    def getSessionWrapped(self):
        return self.getSession()


class Polkasama(Substrate):
    TYPE = "polkasama"
    EP = "ws://localhost:9944/"
    BLOCKTIME = 15
    CUSTOM_TASKS = [
        TaskSubstrateRelayChainStuck,
        TaskSubstrateNewReferenda,
        TaskSubstrateReferendaVotingCheck,
        TaskSubstrateBlockProductionReport,
        TaskSubstrateBlockProductionReportCharts,
    ]

    def __init__(self, conf):
        super().__init__(conf)

    @staticmethod
    def detect(conf):
        try:
            return Polkasama(conf).getNodeName() == "Parity Polkadot"
        except:
            return False
