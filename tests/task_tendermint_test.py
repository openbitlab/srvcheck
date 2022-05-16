import unittest
from .task_test import buildTaskEnv
from srvcheck.chains.tendermint import TaskTendermintHealthError, TaskTendermintNewProposal


class TestTaskTendermintHealthError(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskTendermintHealthError)
        c.healthOk = True
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)

    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskTendermintHealthError)
        c.healthOk = False
        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], 'Health error! 🚨')

class TestTaskTendermintNewProposal(unittest.TestCase):
    def test_noalert(self):
        c, n, t, s = buildTaskEnv(TaskTendermintNewProposal)
        t.run()
        n.flush()
        print(n.events)
        self.assertEqual(len(n.events), 0)
    
    def test_alert(self):
        c, n, t, s = buildTaskEnv(TaskTendermintNewProposal)
        t.prev = """{"proposals":[{"proposal_id":"1","content":{"@type":"/ibc.core.client.v1.ClientUpdateProposal","title":"upgrade client","description":"upgrade light client","subject_client_id":"07-tendermint-0","substitute_client_id":"07-tendermint-2"},
        "status":"PROPOSAL_STATUS_FAILED","final_tally_result":{"yes":"103022468704","abstain":"56100000","no":"115992000","no_with_veto":"90000000"},"submit_time":"2022-04-25T06:22:25.564973762Z","deposit_end_time":"2022-05-09T06:22:25.564973762Z","total_deposit":[{"denom":"ufis","amount":"1000000000"}],
        "voting_start_time":"2022-04-25T06:23:01.163682205Z","voting_end_time":"2022-04-26T06:23:01.163682205Z"}],"pagination":{"next_key":"AAAAAAAAAAI=","total":"0"}}"""

        t.run()
        n.flush()
        self.assertEqual(len(n.events), 1)
        self.assertEqual(n.events[0], '  got new proposal: Upgrade IBC client')

