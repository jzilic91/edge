#############################
###### STD LIBRARIES ########
#############################

import pandas as pd
import re
import numpy as np

from datetime import datetime


#############################
##### CUSTOM LIBRARIES ######
#############################

from failure_provider import FailureProvider
from utilities import NodeCategory, DatasetType


#############################
######### CONSTANTS #########
#############################

HOURS_TO_S = 3600   # one hour to seconds
DAYS_TO_S = 86400   # one day to seconds
WEEKS_TO_S = 604800 # one week to seconds

class DataProvider:

	def __init__(self, file):
		self._dataset = pd.read_csv(file, encoding = 'utf-8', index_col = False)
		self._fat_nodes_failure_provider = None
		self._thin_nodes_failure_provider = None
		self._lustre_servers_failure_provider = None
		self._net_failure_provider = None
		self._other_thin_nodes_failure_provider = None
		self._total_time = 0
		self._dataset_type = DatasetType.PNNL_DATASET

		self.__parse_dataset()


	def get_fat_node_failure_provider(cls):
		return cls._fat_nodes_failure_provider


	def get_thin_node_failure_provider(cls):
		return cls._thin_nodes_failure_provider


	def get_lustre_server_failure_provider(cls):
		return cls._lustre_servers_failure_provider


	def get_other_thin_node_failure_provider(cls):
		return cls._other_thin_nodes_failure_provider


	def get_network_failure_provider(cls):
		return cls._net_failure_provider


	def get_dataset_type(cls):
		return cls._dataset_type


	def plot_fail_rate_dist(cls):
		cls._fat_nodes_failure_provider.plot_fail_rate_dist()
		cls._thin_nodes_failure_provider.plot_fail_rate_dist()
		cls._lustre_servers_failure_provider.plot_fail_rate_dist()
		cls._other_thin_nodes_failure_provider.plot_fail_rate_dist()


	def plot_tbf(cls):
		cls._fat_nodes_failure_provider.plot_tbf()
		cls._thin_nodes_failure_provider.plot_tbf()
		cls._lustre_servers_failure_provider.plot_tbf()
		cls._other_thin_nodes_failure_provider.plot_tbf()


	def plot(cls):
		cls._fat_nodes_failure_provider.plot()
		cls._thin_nodes_failure_provider.plot()
		cls._lustre_servers_failure_provider.plot()
		cls._other_thin_nodes_failure_provider.plot()


	def plot_node_candidate_fr(cls):
		cls._fat_nodes_failure_provider.plot_node_candidate_fr()
		cls._thin_nodes_failure_provider.plot_node_candidate_fr()
		cls._lustre_servers_failure_provider.plot_node_candidate_fr()
		cls._other_thin_nodes_failure_provider.plot_node_candidate_fr()


	def plot_node_candidate_tbf(cls):
		cls._fat_nodes_failure_provider.plot_node_candidate_tbf()
		cls._thin_nodes_failure_provider.plot_node_candidate_tbf()
		cls._lustre_servers_failure_provider.plot_node_candidate_tbf()
		cls._other_thin_nodes_failure_provider.plot_node_candidate_tbf()


	def get_datasets(cls):
		return (cls._fat_nodes_failure_provider, cls._thin_nodes_failure_provider, cls._lustre_servers_failure_provider,\
			cls._other_thin_nodes_failure_provider)


	def get_tbf_data(cls):
		return (cls._fat_nodes_failure_provider.get_tbf_data(), cls._thin_nodes_failure_provider.get_tbf_data(), \
			cls._lustre_servers_failure_provider.get_tbf_data(), cls._other_thin_nodes_failure_provider.get_tbf_data())


	def get_fail_rate_data(cls):
		return (cls._fat_nodes_failure_provider.get_fail_rate_dist(), cls._thin_nodes_failure_provider.get_fail_rate_dist(), \
			cls._lustre_servers_failure_provider.get_fail_rate_dist(), cls._other_thin_nodes_failure_provider.get_fail_rate_dist())


	def print_stats_per_node(cls):
		cls._fat_nodes_failure_provider.print_stats_per_node()
		cls._thin_nodes_failure_provider.print_stats_per_node()
		cls._lustre_servers_failure_provider.print_stats_per_node()
		cls._other_thin_nodes_failure_provider.print_stats_per_node()


	def __parse_dataset(cls):
		fat_nodes_failures = list()
		thin_nodes_failures = list()
		lustre_servers_failures = list()
		net_failures = list()
		other_thin_nodes_failures = list()

		for index, row in cls._dataset.iterrows():
			hw_id = row['Hardware Identifier']			
			node_id = re.findall(r'node (\d+)', hw_id)

			if node_id != []:
				if int(node_id[0]) <= 569:
					fat_nodes_failures.append(row)
				else:
					thin_nodes_failures.append(row)	

			elif re.match(r'Core Switch', hw_id) or re.match(r'quadrics switch [A-Z\d]+', hw_id) or\
				re.match(r'brokade fiber-channel switch \d+', hw_id) or re.match(r'gige switch \d+', hw_id) or\
				re.match(r'ALL', hw_id) or re.match(r'backup-tape library', hw_id):
				net_failures.append(row)

			elif re.match(r'dtemp storage \d+', hw_id):
				lustre_servers_failures.append(row)

			elif re.match(r'home storage TEST', hw_id) or re.match(r'syslog server \d+', hw_id) or\
				re.match(r'test node \d+', hw_id) or re.match(r'cyclade server \d+', hw_id) or\
				re.match(r'home storage \d+', hw_id):
				other_thin_nodes_failures.append(row)

			else:
				print(hw_id)

		cls.__compute_total_time()

		cls._fat_nodes_failure_provider = FailureProvider(fat_nodes_failures, cls._total_time, NodeCategory.ED_DATA)
		cls._thin_nodes_failure_provider = FailureProvider(thin_nodes_failures, cls._total_time, NodeCategory.EC_DATA)
		cls._lustre_servers_failure_provider = FailureProvider(lustre_servers_failures, cls._total_time, NodeCategory.CD_DATA)
		cls._net_failure_provider = FailureProvider(net_failures, cls._total_time, NodeCategory.NET_DATA)
		cls._other_thin_nodes_failure_provider = FailureProvider(other_thin_nodes_failures, cls._total_time, NodeCategory.ER_DATA)

		cls.__distribute_network_failures()


	def __distribute_network_failures(cls):
		sim_failures = list([] for i in range(4))

		fat_node_failures_cnt = cls._fat_nodes_failure_provider.get_number_of_failures()
		thin_node_failures_cnt = cls._thin_nodes_failure_provider.get_number_of_failures()
		lustre_servers_failures_cnt = cls._lustre_servers_failure_provider.get_number_of_failures()
		other_thin_nodes_failure_provider_cnt = cls._other_thin_nodes_failure_provider.get_number_of_failures()
		all_nodes_cnt = fat_node_failures_cnt + thin_node_failures_cnt + lustre_servers_failures_cnt + other_thin_nodes_failure_provider_cnt
	 
		fat_node_prob = round(fat_node_failures_cnt / all_nodes_cnt, 2)
		thin_node_prob = round(thin_node_failures_cnt / all_nodes_cnt, 2)
		lustre_servers_prob = round(lustre_servers_failures_cnt / all_nodes_cnt, 2)
		other_thin_nodes_prob = round(other_thin_nodes_failure_provider_cnt / all_nodes_cnt, 2)
		failures_prob = [fat_node_prob, thin_node_prob, lustre_servers_prob, other_thin_nodes_prob]

		sum_prob = sum(failures_prob)
		residue = 1 - sum_prob

		if residue != 0:
			index = np.random.choice(range(len(failures_prob)))
			failures_prob[index] = failures_prob[index] + residue

		net_failures = cls._net_failure_provider.get_failures()
		for i in range(len(net_failures)):
			index = np.random.choice(range(len(sim_failures)), p = failures_prob)
			sim_failures[index].append(net_failures[i])

		cls._fat_nodes_failure_provider.add_net_failures(sim_failures[0])
		cls._thin_nodes_failure_provider.add_net_failures(sim_failures[1])
		cls._lustre_servers_failure_provider.add_net_failures(sim_failures[2])
		cls._other_thin_nodes_failure_provider.add_net_failures(sim_failures[3])


	def __compute_total_time(cls):		
		date_list = [datetime.strptime(date_frame, '%m/%d/%Y %H:%M') for date_frame in cls._dataset['Date']]
		cls._total_time = max(date_list) - min(date_list)
		total_time_in_t_s = cls._total_time.total_seconds()
		cls._total_time = divmod(total_time_in_t_s, HOURS_TO_S)
		cls._total_time = round(cls._total_time[0] + (cls._total_time[1] / HOURS_TO_S), 2)