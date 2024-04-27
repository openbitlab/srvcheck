import json, requests
import configparser
import re
from ..notification import Emoji
from .chain import Chain
from ..tasks import Task,  hours, minutes
from ..utils import ConfItem, ConfSet

ConfSet.addItem(ConfItem('chain.thresholdNotsigned', 5, int))
ConfSet.addItem(ConfItem('chain.attestationSeconds', 0.004, float))

def getPrometheusMetricValue(metrics, metric_name):
    metric = list(filter(lambda x: metric_name in x, metrics.split("\n")))[-1]
    return metric.split(" ")[-1]


class TaskDirkFailedAttestationSign(Task):
	def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(5)):
		super().__init__('TaskDirkFailedAttestationSign',
		      services, checkEvery, notifyEvery)

		self.THRESHOLD_FAILED = self.s.conf.getOrDefault('chain.thresholdNotsigned')
		self.prev = None

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		if self.prev is None:
			self.prev = self.s.chain.getAttestationSign()
		missed = (self.s.chain.getAttestationSign() - self.s.chain.getAttestationSignSuccess())/self.prev

		if missed >= self.THRESHOLD_NOTSIGNED:
			return self.notify(f'Failed {missed}% of attestations signatures {Emoji.BlockMiss}')

		return False

class TaskDirkAttestationSignDuration(Task):
	def __init__(self, services, checkEvery=minutes(1), notifyEvery=minutes(5)):
		super().__init__('TaskDirkAttestationSignDuration',
		      services, checkEvery, notifyEvery)

		self.THRESHOLD_DURATION = self.s.conf.getOrDefault('chain.attestationSeconds')

	@staticmethod
	def isPluggable(services):
		return True

	def run(self):
		duration = (self.s.chain.getAttestationSignSeconds()/self.s.chain.getAttestationSign())
		if duration >= self.THRESHOLD_DURATION:
			return self.notify(f'Attestation signature duration is breaching threshold: {duration}s > {self.THRESHOLD_DURATION} {Emoji.Slow}')

		return False


class Dirk (Chain):
	TYPE = "dirk"
	NAME = ""
	BLOCKTIME = 60
	EP = "http://localhost:8181/"
	CUSTOM_TASKS = [TaskDirkFailedAttestationSign, TaskDirkAttestationSignDuration]

	@staticmethod
	def detect(conf):
		try:
			Dirk(conf).getVersion()
			return True
		except:
			return False


	def getLocalVersion(self):
		ver = self.conf.getOrDefault('chain.localVersion')
		if ver is None:
			raise Exception('No local version of the software specified!') from e
		return ver

	def getAttestationSign(self):
		out = requests.get(f"{self.EP_METRICS}/metrics")
		metricStr = "dirk_signer_process_duration_seconds_count{request=\"attestation\"}"
		submitted = getPrometheusMetricValue(out.text, metricStr)
		return int(submitted)

	def getAttestationSignSuccess(self):
		out = requests.get(f"{self.EP_METRICS}/metrics")
		metricStr = "dirk_signer_process_requests_total{request=\"attestation\",result=\"succeeded\"}"
		submitted = getPrometheusMetricValue(out.text, metricStr)
		return int(submitted)

	def getAttestationSignSeconds(self):
		out = requests.get(f"{self.EP_METRICS}/metrics")
		metricStr = "dirk_signer_process_duration_seconds_sum{request=\"attestation\"}"
		submitted = getPrometheusMetricValue(out.text, metricStr)
		return float(submitted)


