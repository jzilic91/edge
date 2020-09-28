#############################
###### STD LIBRARIES ########
#############################

import pandas as pd

#############################
##### CUSTOM LIBRARIES ######
#############################

from utilities import NodeCategory, DatasetType
from dataset_statistics import DatasetStatistics

#############################
######### CONSTANTS #########
#############################

CONVERSION_SYSTEM_ID_DICT = {2: (20, NodeCategory.EC_DATA),
			   				 3: (9, NodeCategory.ER_DATA),
			   				 4: (10, NodeCategory.ER_DATA),
							 5: (11, NodeCategory.ER_DATA),
							 6: (12, NodeCategory.ED_DATA),
							 7: (1, NodeCategory.ED_DATA),
							 8: (4, NodeCategory.ER_DATA),
							 9: (13, NodeCategory.ER_DATA),
							 10: (14, NodeCategory.ER_DATA),
							 11: (15, NodeCategory.ER_DATA),
							 12: (18, NodeCategory.ER_DATA),
							 13: (16, NodeCategory.ER_DATA),
							 14: (17, NodeCategory.ER_DATA),
							 15: (22, NodeCategory.CD_DATA),
							 16: (19, NodeCategory.EC_DATA),
							 18: (7, NodeCategory.ED_DATA),
							 19: (8, NodeCategory.ED_DATA),
							 20: (5, NodeCategory.ED_DATA),
							 21: (6, NodeCategory.ED_DATA),
							 22: (3, NodeCategory.ER_DATA),
							 23: (21, NodeCategory.EC_DATA),
							 24: (2, NodeCategory.ER_DATA)}

EMPTY_SYSTEM_ID = 17


class DataStorage:

	############################
	###### PUBLIC METHODS ######
	############################

	def __init__(self, file, dataset_type):
		if dataset_type == DatasetType.LANL_DATASET:
			self._dataset = pd.read_csv(file, encoding = 'utf-8', index_col = False)
		
		elif dataset_type == DatasetType.LDNS_DATASET:
			self._dataset = open(file, 'r')

		self._ec_data_stats = DatasetStatistics(NodeCategory.EC_DATA, dataset_type)
		self._ed_data_stats = DatasetStatistics(NodeCategory.ED_DATA, dataset_type)
		self._er_data_stats = DatasetStatistics(NodeCategory.ER_DATA, dataset_type)
		self._cd_data_stats = DatasetStatistics(NodeCategory.CD_DATA, dataset_type)

		self._dataset_type = dataset_type
		self._acc_num_fail = 0

		self.__parse_dataset()


	def print_stats(cls):
		cls._ec_data_stats.print_stats()
		cls._ed_data_stats.print_stats()
		cls._er_data_stats.print_stats()
		cls._cd_data_stats.print_stats()

		print("#########################")
		print("###### TOTAL STATS ######")
		print("#########################\n")
		print("#failures: " + str(cls.__get_tot_num_of_fail()))
		print("System IDs: " + str(sorted(cls.__get_system_ids())))
		print("#nodes: " + str(cls.__get_num_of_nodes()))
		print("#procs: " + str(cls.__get_num_of_procs()))


	def print_stats_per_node(cls):
		cls._ec_data_stats.print_stats_per_node()
		cls._ed_data_stats.print_stats_per_node()
		cls._er_data_stats.print_stats_per_node()
		cls._cd_data_stats.print_stats_per_node()


	def plot_fail_rate_dist(cls):
		cls._ec_data_stats.plot_fail_rate_dist()
		cls._ed_data_stats.plot_fail_rate_dist()
		cls._er_data_stats.plot_fail_rate_dist()
		cls._cd_data_stats.plot_fail_rate_dist()


	def plot_tbf(cls):
		cls._ec_data_stats.plot_tbf()
		cls._ed_data_stats.plot_tbf()
		cls._er_data_stats.plot_tbf()
		cls._cd_data_stats.plot_tbf()


	def plot(cls):
		cls._ec_data_stats.plot()
		cls._ed_data_stats.plot()
		cls._er_data_stats.plot()
		cls._cd_data_stats.plot()


	def plot_node_candidate_avail(cls):
		cls._ec_data_stats.plot_node_cadidate_avail()
		cls._ed_data_stats.plot_node_cadidate_avail()
		cls._er_data_stats.plot_node_cadidate_avail()
		cls._cd_data_stats.plot_node_cadidate_avail()


	def plot_node_candidate_tbf(cls):
		cls._ec_data_stats.plot_node_cadidate_tbf()
		cls._ed_data_stats.plot_node_cadidate_tbf()
		cls._er_data_stats.plot_node_cadidate_tbf()
		cls._cd_data_stats.plot_node_cadidate_tbf()


	def plot_node_candidate_fr(cls):
		cls._ec_data_stats.plot_node_cadidate_fr()
		cls._ed_data_stats.plot_node_cadidate_fr()
		cls._er_data_stats.plot_node_cadidate_fr()
		cls._cd_data_stats.plot_node_cadidate_fr()
		

	def get_datasets(cls):
		return (cls._ec_data_stats, cls._ed_data_stats, cls._er_data_stats, cls._cd_data_stats)


	def get_tbf_data(cls):
		return (cls._ec_data_stats.get_tbf_data(), cls._ed_data_stats.get_tbf_data(), \
			cls._er_data_stats.get_tbf_data(), cls._cd_data_stats.get_tbf_data())


	def get_fail_rate_data(cls):
		return (cls._ec_data_stats.get_fail_rate_data(), cls._ed_data_stats.get_fail_rate_data(), \
			cls._er_data_stats.get_fail_rate_data(), cls._cd_data_stats.get_fail_rate_data())


	def get_dataset_type(cls):
		return cls._dataset_type


	def get_ec_data_stats(cls):
		return cls._ec_data_stats


	def get_ed_data_stats(cls):
		return cls._ed_data_stats


	def get_er_data_stats(cls):
		return cls._er_data_stats


	def get_cd_data_stats(cls):
		return cls._cd_data_stats


	def get_acc_num_fail_ldns(cls):
		return cls._acc_num_fail


	############################
	###### PRIVATE METHODS #####
	############################

	def __parse_dataset(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			cls.__parse_lanl_dataset()

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			cls.__parse_ldns_dataset()


	def __parse_ldns_dataset(cls):
		top_4_dict = dict()

		for line in cls._dataset.readlines():
			elements = line.split()
			ip_addr = elements[0]
			num_of_intervals = int(elements[1])
			cls._acc_num_fail += num_of_intervals - 1
			intervals = [float(ele) for ele in elements[2:]]

			if len(top_4_dict.keys()) < 4:
				top_4_dict[ip_addr] = (num_of_intervals, intervals)
				top_4_dict = {k: v for k, v in sorted(top_4_dict.items(), key = lambda item: item[1][0])}
				continue

			flag = True
			key_to_pop = None
			value_to_pop = 0

			while flag:
				flag = False

				for key, value in top_4_dict.items():
					if value[0] < num_of_intervals:
						key_to_pop = key
						value_to_pop = value
						break

				if key_to_pop != None:
					if key_to_pop in top_4_dict:
						del top_4_dict[key_to_pop]
						top_4_dict[ip_addr] = (num_of_intervals, intervals)
						top_4_dict = {k: v for k, v in sorted(top_4_dict.items(), key = lambda item: item[1][0])}
						ip_addr = key_to_pop
						num_of_intervals = value_to_pop[0]
						intervals = value_to_pop[1]
						flag = True

		keys = list(top_4_dict.keys())
		cls._ec_data_stats.add_item(top_4_dict[keys[0]])
		cls._er_data_stats.add_item(top_4_dict[keys[1]])
		cls._ed_data_stats.add_item(top_4_dict[keys[2]])
		cls._cd_data_stats.add_item(top_4_dict[keys[3]])


	def __parse_lanl_dataset(cls):
		for index, row in cls._dataset.iterrows():
			system_id = int(row['System'])

			if system_id == EMPTY_SYSTEM_ID:
				continue

			(row['System'], data_category) = cls.__get_system_data(system_id)

			if data_category == cls._ec_data_stats.get_data_category():
				cls._ec_data_stats.add_item(row)

			elif data_category == cls._ed_data_stats.get_data_category():
				cls._ed_data_stats.add_item(row)

			elif data_category == cls._er_data_stats.get_data_category():
				cls._er_data_stats.add_item(row)

			elif data_category == cls._cd_data_stats.get_data_category():
				cls._cd_data_stats.add_item(row)

			else:
				exit("Data row must correspond to one of data categories!\n Data: " + str(row))


	def __get_system_data(cls, system_id):
		return (CONVERSION_SYSTEM_ID_DICT[system_id][0], CONVERSION_SYSTEM_ID_DICT[system_id][1])


	def __get_tot_num_of_fail(cls):
		return (cls._cd_data_stats.get_num_of_fail() + cls._er_data_stats.get_num_of_fail() + \
			cls._ed_data_stats.get_num_of_fail()  + cls._ec_data_stats.get_num_of_fail())


	def __get_system_ids(cls):
		return (cls._cd_data_stats.get_system_ids() + cls._er_data_stats.get_system_ids() + \
			cls._ed_data_stats.get_system_ids()  + cls._ec_data_stats.get_system_ids()) 


	def __get_num_of_nodes(cls):
		return (cls._cd_data_stats.get_num_of_nodes() + cls._er_data_stats.get_num_of_nodes() + \
			cls._ed_data_stats.get_num_of_nodes()  + cls._ec_data_stats.get_num_of_nodes())


	def __get_num_of_procs(cls):
		return (cls._cd_data_stats.get_num_of_procs() + cls._er_data_stats.get_num_of_procs() + \
			cls._ed_data_stats.get_num_of_procs()  + cls._ec_data_stats.get_num_of_procs())