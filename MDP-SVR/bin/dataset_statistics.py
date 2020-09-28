#############################
####### STD LIBRARIES #######
#############################

import operator
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math

from pandas.plotting import register_matplotlib_converters

#############################
##### CUSTOM LIBRARIES ######
#############################

from utilities import NodeCategory, Uptime, DatasetType
from svr_logger import SvrLogger
from mdp_logger import MdpLogger

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


class DatasetStatistics:

	############################
	###### PUBLIC METHODS ######
	############################

	def __init__(self, data_category, dataset_type):
		self._data = tuple()
		self._data_category = data_category
		self._title = ''
		self._folder_path = ''
		self._dataset_type = dataset_type

		self._mtbf = 0
		self._mttr = 0

		if self._dataset_type == DatasetType.LANL_DATASET:

			if self._data_category == NodeCategory.ER_DATA:
				self._title = 'Edge Regular Server'
				self._folder_path = 'logs/LANL/regular/'

			elif self._data_category == NodeCategory.EC_DATA:
				self._title = "Edge Computational Server"
				self._folder_path = 'logs/LANL/computational/'

			elif self._data_category == NodeCategory.ED_DATA:
				self._title = "Edge Database Server"
				self._folder_path = 'logs/LANL/database/'

			elif self._data_category == NodeCategory.CD_DATA:
				self._title = "Cloud Data Center"
				self._folder_path = 'logs/LANL/cloud/'

		elif self._dataset_type == DatasetType.LDNS_DATASET:

			if self._data_category == NodeCategory.ER_DATA:
				self._title = 'Edge Regular Server'
				self._folder_path = 'logs/LDNS/regular/'

			elif self._data_category == NodeCategory.EC_DATA:
				self._title = "Edge Computational Server"
				self._folder_path = 'logs/LDNS/computational/'

			elif self._data_category == NodeCategory.ED_DATA:
				self._title = "Edge Database Server"
				self._folder_path = 'logs/LDNS/database/'

			elif self._data_category == NodeCategory.CD_DATA:
				self._title = "Cloud Data Center"
				self._folder_path = 'logs/LDNS/cloud/'

		else:
			exit("Category " + self._data_category + " does not exist!")

		register_matplotlib_converters()


	def add_item(cls, row):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			row['Prob Started'] = datetime.datetime.strptime(row['Prob Started'], '%m/%d/%Y %H:%M')
			row['Prob Fixed'] = datetime.datetime.strptime(row['Prob Fixed'], '%m/%d/%Y %H:%M')
			cls._data += (row,)

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			# data structure (num_of_intervals, [intervals])
			# interval format: <start> <end>
			cls._data = row

			for i in range(len(cls._data[1])):
				cls._data[1][i] = datetime.datetime.fromtimestamp(cls._data[1][i]).strftime('%m/%d/%Y %H:%M')
				cls._data[1][i] = datetime.datetime.strptime(cls._data[1][i], '%m/%d/%Y %H:%M')


	def get_data_category(cls):
		return cls._data_category


	def compute_mtbf_mttr(cls):
		if len(cls._data) > 1:
			cls._mtbf = cls.__compute_mtbf()
			cls._mttr = cls.__compute_mttr()


	def get_mtbf(cls):
		return cls._mtbf


	def get_mttr(cls):
		return cls._mttr


	def get_failure_transition_probability(cls, t):
		# MdpLogger.write_log('Offloading site: ' + str(cls._data_category))
		# MdpLogger.write_log('Discrete epoch: ' + str(t))
		# MdpLogger.write_log('MTBF:' + str(cls._mtbf))
		# MdpLogger.write_log('Probability: ' + str(round((1 - math.exp(-t / cls._mtbf)), 2)) + '\n')
		return round((1 - math.exp(-t / cls._mtbf)), 2)


	def get_folder_path(cls):
		return cls._folder_path


	def get_node_category(cls):
		return cls._title


	def get_num_of_fail(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			return len(cls._data)

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			return cls._data[0]


	def get_system_ids(cls):
		system_ids = tuple()

		for row in cls._data:
			if not (row['System'] in system_ids):
				system_ids += (row['System'],)

		return sorted(system_ids)


	def get_num_of_nodes(cls):
		system_ids = tuple()
		num_of_nodes = 0

		for row in cls._data:
			if not (row['System'] in system_ids):
				system_ids += (row['System'],)
				num_of_nodes += row['nodes']

		return int(num_of_nodes)


	def get_num_of_procs(cls):
		system_ids = tuple()
		num_of_procs = 0

		for row in cls._data:
			if not (row['System'] in system_ids):
				system_ids += (row['System'],)
				num_of_procs += row['procstot']

		return int(num_of_procs)


	def print_stats(cls):
		system_ids = tuple()
		num_of_nodes = 0
		num_of_procs = 0

		for row in cls._data:
			if not (row['System'] in system_ids):
				system_ids += (row['System'],)
				num_of_nodes += row['nodes']
				num_of_procs += row['procstot']

		print("### " + str(cls._data_category) + " ###")
		print("#failures: " + str(len(cls._data)))
		print("System IDs: " + str(sorted(system_ids)))
		print("#nodes: " + str(int(num_of_nodes)))
		print("#procs_total: " + str(int(num_of_procs)))
		print("#procs_per_nodes: {number:.2f}".format(number = (num_of_procs / num_of_nodes)))

		print()


	def print_failures(cls):
		print("### " + str(cls._data_category) + " FAILURE TRACE LOGS ###")
		cls._data = sorted(cls._data, key = operator.itemgetter('Prob Started'), reverse = False)
		print(cls._data)
		print()


	def plot_fail_rate_dist(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			cls.__plot_fr_lanl()


	def get_fail_rate_data(cls):
		datetime_events = tuple()
		cls._data = sorted(cls._data, key = operator.itemgetter('Prob Started'), reverse = False)

		for event in cls._data:
			datetime_events += (event['Prob Started'],)

		counts, _, _ = plt.hist(datetime_events, bins = 700)

		return counts


	def plot_tbf(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			cls.__plot_tbf_lanl()


	def get_tbf_data(cls):
		tbf = tuple()
		cls._data = sorted(cls._data, key = operator.itemgetter('Prob Started'), reverse = False)

		for i in range(len(cls._data) - 1):
			tbf += ((cls._data[i + 1]['Prob Started'] - cls._data[i]['Prob Started']).total_seconds(),)

		return tbf


	def plot(cls):
		cls.plot_tbf()
		cls.plot_fail_rate_dist()


	def print_stats_per_node(cls):
		nodes_dict = dict()

		for row in cls._data:
			system_id = int(row['System'])
			node_num = int(row['nodenum'])
			found = False

			if system_id in nodes_dict:
				for ele in nodes_dict[system_id]:
					if int(ele[0]['nodenum']) == node_num:
						ele[1] += 1
						found = True
						break

				if not found:
					nodes_dict[system_id].append([row, 1])
			else:
				nodes_dict[system_id] = [[row, 1]]

		print('Node statistics for ' + cls._title + ':')

		cnt_nodes = 0
		cnt_failures = 0
		
		for key, value in nodes_dict.items():
			for node in value:
				print(str(key) + '_' + str(int(node[0]['nodenum'])) + ': #failures: ' + str(int(node[1])) + \
					', #procs: ' + str(int(node[0]['procsinnode'])) + ', #mem: ' + str(int(node[0]['mem'])))
				cnt_failures += node[1]
				cnt_nodes += 1

		print()
		print('#overall_failures: ' + str(cnt_failures))
		print('#num_nodes: ' + str(cnt_nodes))
		print()


	def plot_node_cadidate_tbf(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			tbf = cls.get_node_candidate_tbf()

			plt.plot(tuple(i for i in range(len(tbf))), tbf)
			plt.suptitle('#failures = ' + str(len(tbf) + 1))
			plt.title('TBF distribution for ' + cls._title + " (LANL dataset)")
			plt.xlabel('Failure index')
			plt.ylabel('TBF (hours)')
			plt.show()

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			cls.__plot_node_candidate_tbf_ldns()


	def plot_node_cadidate_fr(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			fr_data = cls.get_node_candidate_fr()

			plt.hist(fr_data, bins = 50)
			plt.suptitle('#failures = ' + str(len(fr_data)))
			plt.title('Failure Rate distribution for ' + cls._title + " (LANL dataset)")
			plt.xlabel('Datetime')
			plt.ylabel('Frequency')
			plt.show()

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			cls.__plot_node_candidate_fr_ldns()


	def plot_node_cadidate_avail(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:
			avail_data = cls.get_node_candidate_avail()

			plt.plot(tuple(i for i in range(len(avail_data))), avail_data)
			plt.suptitle('#data_points = ' + str(len(avail_data) + 1))
			plt.title('Availability distribution for ' + cls._title + " (LANL dataset)")
			plt.xlabel('Failure index')
			plt.ylabel('Availability (per day)')
			plt.show()

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			cls.__plot_node_candidate_avail_ldns()


	def get_node_candidate_tbf(cls):
		tmp_data = tuple()
		tbf_data = tuple()

		if cls._dataset_type == DatasetType.LANL_DATASET:

			if cls._data_category == NodeCategory.ER_DATA:
				for row in cls._data:
					if int(row['System']) == 3 and int(row['nodenum']) == 0:
						tmp_data += (row['Prob Started'],)
				
			elif cls._data_category == NodeCategory.EC_DATA:
				 for row in cls._data:
				 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
				 		tmp_data += (row['Prob Started'],)
				
			elif cls._data_category == NodeCategory.ED_DATA:
				for row in cls._data:
					if int(row['System']) == 1 and int(row['nodenum']) == 0:
						tmp_data += (row['Prob Started'],)
				
			elif cls._data_category == NodeCategory.CD_DATA:
				for row in cls._data:
					if int(row['System']) == 22 and int(row['nodenum']) == 0:
						tmp_data += (row['Prob Started'],)

			for i in range(len(tmp_data) - 1):
				tbf_data += ((tmp_data[i + 1] - tmp_data[i]).total_seconds() / (60 * 60 * 24),)

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			for i in range(len(cls._data[1]) - 1):
				tbf_data += ((cls._data[1][i + 1] - cls._data[1][i]).total_seconds() / (60 * 60),)

		return tbf_data


	def get_node_candidate_fr(cls):
		fr_data = tuple()

		if cls._dataset_type == DatasetType.LANL_DATASET:

			if cls._data_category == NodeCategory.ER_DATA:
				for row in cls._data:
					if int(row['System']) == 3 and int(row['nodenum']) == 0:
						fr_data += (row['Prob Started'],)
				
			elif cls._data_category == NodeCategory.EC_DATA:
				 for row in cls._data:
				 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
				 		fr_data += (row['Prob Started'],)
				
			elif cls._data_category == NodeCategory.ED_DATA:
				for row in cls._data:
					if int(row['System']) == 1 and int(row['nodenum']) == 0:
						fr_data += (row['Prob Started'],)
				
			elif cls._data_category == NodeCategory.CD_DATA:
				for row in cls._data:
					if int(row['System']) == 22 and int(row['nodenum']) == 0:
						fr_data += (row['Prob Started'],)

			count, _, _ = plt.hist(fr_data, bins = 60)

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			count, _, _ = plt.hist(cls._data[1][::2], bins = 30)
		
		return count


	def get_node_candidate_num_failures(cls):
		cnt_failures = 0	
		if cls._data_category == NodeCategory.ER_DATA:
			for row in cls._data:
				if int(row['System']) == 3 and int(row['nodenum']) == 0:
					cnt_failures += 1
			
		elif cls._data_category == NodeCategory.EC_DATA:
			 for row in cls._data:
			 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
			 		cnt_failures += 1
			
		elif cls._data_category == NodeCategory.ED_DATA:
			for row in cls._data:
				if int(row['System']) == 1 and int(row['nodenum']) == 0:
					cnt_failures += 1
			
		elif cls._data_category == NodeCategory.CD_DATA:
			for row in cls._data:
				if int(row['System']) == 22 and int(row['nodenum']) == 0:
					cnt_failures += 1

		return cnt_failures


	def get_node_candidate_num_procs(cls):
		if cls._data_category == NodeCategory.ER_DATA:
			for row in cls._data:
				if int(row['System']) == 3 and int(row['nodenum']) == 0:
					return int(row['procsinnode'])
			
		elif cls._data_category == NodeCategory.EC_DATA:
			 for row in cls._data:
			 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
			 		return int(row['procsinnode'])
			
		elif cls._data_category == NodeCategory.ED_DATA:
			for row in cls._data:
				if int(row['System']) == 1 and int(row['nodenum']) == 0:
					return int(row['procsinnode'])
			
		elif cls._data_category == NodeCategory.CD_DATA:
			for row in cls._data:
				if int(row['System']) == 22 and int(row['nodenum']) == 0:
					return int(row['procsinnode'])


	def get_node_candidate_mem_size(cls):
		if cls._data_category == NodeCategory.ER_DATA:
			for row in cls._data:
				if int(row['System']) == 3 and int(row['nodenum']) == 0:
					return int(row['mem'])
			
		elif cls._data_category == NodeCategory.EC_DATA:
			 for row in cls._data:
			 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
			 		return int(row['mem'])
			
		elif cls._data_category == NodeCategory.ED_DATA:
			for row in cls._data:
				if int(row['System']) == 1 and int(row['nodenum']) == 0:
					return int(row['mem'])
			
		elif cls._data_category == NodeCategory.CD_DATA:
			for row in cls._data:
				if int(row['System']) == 22 and int(row['nodenum']) == 0:
					return int(row['mem'])


	def get_node_candidate_failure_timestamps(cls):
		timestamps = tuple()

		if cls._data_category == NodeCategory.ER_DATA:
			for row in cls._data:
				if int(row['System']) == 3 and int(row['nodenum']) == 0:
					timestamps += (str(row['Prob Started']),)
			
		elif cls._data_category == NodeCategory.EC_DATA:
			 for row in cls._data:
			 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
			 		timestamps += (str(row['Prob Started']),)
			
		elif cls._data_category == NodeCategory.ED_DATA:
			for row in cls._data:
				if int(row['System']) == 1 and int(row['nodenum']) == 0:
					timestamps += (str(row['Prob Started']),)
			
		elif cls._data_category == NodeCategory.CD_DATA:
			for row in cls._data:
				if int(row['System']) == 22 and int(row['nodenum']) == 0:
					timestamps += (str(row['Prob Started']),)

		return timestamps


	def get_node_candidate_id(cls):
		if cls._data_category == NodeCategory.ER_DATA:
			for row in cls._data:
				if int(row['System']) == 3 and int(row['nodenum']) == 0:
					return str(row['System'])+ '_' + str(row['nodenum'])
			
		elif cls._data_category == NodeCategory.EC_DATA:
			 for row in cls._data:
			 	if int(row['System']) == 19 and int(row['nodenum']) == 1:
			 		return str(row['System']) + '_' + str(row['nodenum'])
			
		elif cls._data_category == NodeCategory.ED_DATA:
			for row in cls._data:
				if int(row['System']) == 1 and int(row['nodenum']) == 0:
					return str(row['System']) + '_' + str(row['nodenum'])
			
		elif cls._data_category == NodeCategory.CD_DATA:
			for row in cls._data:
				if int(row['System']) == 22 and int(row['nodenum']) == 0:
					return str(row['System']) + '_' + str(row['nodenum'])


	def get_node_candidate_avail(cls, system_id, node_num):
		if cls._dataset_type == DatasetType.LANL_DATASET:

			# if cls._data_category == NodeCategory.ER_DATA:
			# 	SvrLogger.open_file_log('logs/LANL/regular/node_candidate_log.txt')

			# elif cls._data_category == NodeCategory.EC_DATA:
			# 	SvrLogger.open_file_log('logs/LANL/computational/node_candidate_log.txt')

			# elif cls._data_category == NodeCategory.ED_DATA:
			# 	SvrLogger.open_file_log('logs/LANL/database/node_candidate_log.txt')
													
			# elif cls._data_category == NodeCategory.CD_DATA:
			# 	SvrLogger.open_file_log('logs/LANL/cloud/node_candidate_log.txt')

			rows = cls.__get_data_rows(system_id, node_num)
			cls._mtbf = cls.__compute_mtbf(rows)
			return cls.__evaluate_failure_data(system_id, node_num)

		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			return list(cls.__get_avail_data_ldns().values())


	def get_avail_data(cls):
		if cls._dataset_type == DatasetType.LANL_DATASET:

			if cls._data_category == NodeCategory.ER_DATA:
				# SvrLogger.open_file_log('logs/LANL/regular/node_candidate_log.txt')
				return cls.__evaluate_failure_data(3, 0, entire_dataset = True)

			elif cls._data_category == NodeCategory.EC_DATA:
				# SvrLogger.open_file_log('logs/LANL/computational/node_candidate_log.txt')
				return cls.__evaluate_failure_data(19, 1, entire_dataset = True)

			elif cls._data_category == NodeCategory.ED_DATA:
				# SvrLogger.open_file_log('logs/LANL/database/node_candidate_log.txt')
				return cls.__evaluate_failure_data(1, 0, entire_dataset = True)
													
			elif cls._data_category == NodeCategory.CD_DATA:
				# SvrLogger.open_file_log('logs/LANL/cloud/node_candidate_log.txt')
				return cls.__evaluate_failure_data(22, 0, entire_dataset = True)

		# not sure about this
		elif cls._dataset_type == DatasetType.LDNS_DATASET:
			return list(cls.__get_avail_data_ldns().values())



	############################
	###### PRIVATE METHODS #####
	############################

	def __get_data_rows(cls, system_id, node_num):
		data = tuple()

		for row in cls._data:
			if int(row['System']) == system_id and int(row['nodenum']) == node_num:
				data += (row,)

		return data


	def __convert_system_id(cls, node_system_id, node_num):
		for key in  CONVERSION_SYSTEM_ID_DICT.keys():
			if CONVERSION_SYSTEM_ID_DICT[key][0] == node_system_id:
				return str(key) + '_' + str(node_num)

		return None


	def __compute_mtbf(cls):
		#total_time = (cls.__get_max_failure_date() - cls.__get_min_failure_date()).seconds / (60 * 60 * 24)
		total_time = (cls.__get_max_failure_date() - cls.__get_min_failure_date()).days
		# MdpLogger.write_log('Computing MTBF')
		# MdpLogger.write_log('Min datetime:' + str(cls.__get_min_failure_date()))
		# MdpLogger.write_log('Max datetime:' + str(cls.__get_max_failure_date()))
		# MdpLogger.write_log('Total time (in days): ' + str(total_time))
		# MdpLogger.write_log('Total time (in seconds): ' + str((cls.__get_max_failure_date() - cls.__get_min_failure_date())))
		# MdpLogger.write_log('Number of failures: ' + str(len(cls._data)))
		return total_time / (cls._data)


	def __compute_mtbf(cls, data):
		#total_time = (cls.__get_max_failure_date() - cls.__get_min_failure_date()).seconds / (60 * 60 * 24)
		total_time = (cls.__get_max_failure_date(data) - cls.__get_min_failure_date(data)).days * 24
		# MdpLogger.write_log('Computing MTBF')
		# MdpLogger.write_log('Min datetime:' + str(cls.__get_min_failure_date(data)))
		# MdpLogger.write_log('Max datetime:' + str(cls.__get_max_failure_date(data)))
		# MdpLogger.write_log('Total time (in hours): ' + str(total_time))
		# MdpLogger.write_log('Total time (in days): ' + str((cls.__get_max_failure_date(data) - cls.__get_min_failure_date(data))))
		# MdpLogger.write_log('Number of failures: ' + str(len(data)))
		return total_time / len(data)

	def __compute_mttr(cls):
		time_to_repairs = tuple()
		
		for row in cls._data:
			time_to_repairs += (abs((row['Prob Fixed'] - row['Prob Started']).seconds) / (60 * 60 * 24),)

		return sum(time_to_repairs) / len(time_to_repairs)


	def __get_min_failure_date(cls):
		return min(row['Prob Started'] for row in cls._data if isinstance(row['Prob Started'], datetime.datetime))


	def __get_max_failure_date(cls):
		return max(row['Prob Started'] for row in cls._data if isinstance(row['Prob Started'], datetime.datetime))


	def __get_min_failure_date(cls, data):
		return min(row['Prob Started'] for row in data if isinstance(row['Prob Started'], datetime.datetime))


	def __get_max_failure_date(cls, data):
		return max(row['Prob Started'] for row in data if isinstance(row['Prob Started'], datetime.datetime))


	def __plot_node_candidate_avail_ldns(cls):
		avail_data = cls.__get_avail_data_ldns()

		plt.plot(list(avail_data.keys()), list(avail_data.values()))
		plt.suptitle('#data_points = ' + str(len(avail_data) + 1))
		plt.title('Availability distribution for ' + cls._title + " (LDNS dataset)")
		plt.xlabel('Failure index')
		plt.ylabel('Availability (per day)')
		plt.show()


	def __plot_node_candidate_fr_ldns(cls):
		plt.hist(cls._data[1][::2], bins = 30)
		plt.suptitle('#failures = ' + str(cls._data[0]))
		plt.title('Failure Rate Distribution for ' + cls._title + " (LDNS dataset)")
		plt.xlabel('Datetime')
		plt.ylabel('Frequency')
		plt.show()


	def __plot_fr_lanl(cls):
		datetime_events = tuple()
		cls._data = sorted(cls._data, key = operator.itemgetter('Prob Started'), reverse = False)

		for event in cls._data:
			datetime_events += (event['Prob Started'],)

		plt.hist(datetime_events, bins = 550)
		plt.suptitle('#failures = ' + str(len(cls._data)))
		plt.title('Failure Rate Distribution for ' + cls._title + " (LANL dataset)")
		plt.xlabel('Datetime')
		plt.ylabel('Frequency')
		plt.show()


	def __plot_node_candidate_tbf_ldns(cls):
		tbf = tuple()

		for i in range(len(cls._data[1]) - 1):
			tbf += ((cls._data[1][i + 1] - cls._data[1][i]).total_seconds(),)

		plt.plot(tuple(i for i in range(len(tbf))), tbf)
		plt.suptitle('#failures = ' + str(cls._data[0]))
		plt.title('TBF distribution for ' + cls._title + " (LDNS dataset)")
		plt.xlabel('Failure index')
		plt.ylabel('TBF (seconds)')
		plt.show()


	def __plot_tbf_lanl(cls):
		tbf = tuple()
		cls._data = sorted(cls._data, key = operator.itemgetter('Prob Started'), reverse = False)

		for i in range(len(cls._data) - 1):
			tbf += ((cls._data[i + 1]['Prob Started'] - cls._data[i]['Prob Started']).total_seconds(),)

		plt.plot(tuple(i for i in range(1, len(cls._data))), tbf)
		plt.suptitle('#failures = ' + str(len(cls._data)))
		plt.title('TBF distribution for ' + cls._title + " (LANL dataset)")
		plt.xlabel('Failure index')
		plt.ylabel('TBF (seconds)')
		plt.show()


	def __evaluate_failure_data(cls, system_id, node_num, entire_dataset = False):
		# collect failures only that happend on the node candidate
		avail = tuple()
		node_dataset = tuple()

		if entire_dataset == False:
			for row in cls._data:
				if int(row['System']) == system_id and int(row['nodenum']) == node_num:
			 		node_dataset += (row,)
		else:
			for row in cls._data:
				node_dataset += (row,)

		node_dataset = sorted(node_dataset, key = operator.itemgetter('Prob Started'), reverse = False)

		# take first failure date as starting point
		date_time = node_dataset[0]['Prob Started']

		# iterate all failures that happend on the node candidate
		downtime_transit = 0
		while date_time.date() <= node_dataset[-1]['Prob Started'].date():
			# SvrLogger.write_log('')
			# SvrLogger.write_log('Datetime: ' + str(date_time))

			failures_per_date = tuple()
			downtime_acc = 0

			# if transit downtime is greater then single day duration then node was unavailable for entire day
			if downtime_transit > Uptime.DAY_IN_MINUTES:
				# SvrLogger.write_log('Downtime transit: ' + str(downtime_transit) + ' > ' + str(Uptime.DAY_IN_MINUTES))
				downtime_transit = downtime_transit - Uptime.DAY_IN_MINUTES
				# SvrLogger.write_log('New downtime transit: ' + str(downtime_transit))
				avail += (0,)
				# SvrLogger.write_log('Availability on ' + str(date_time) + ' is ' + str(avail[-1]))
				date_time += datetime.timedelta(days = 1)
				continue

			# if transit downtime exists then accumulate it for current day
			elif downtime_transit != 0:
				downtime_acc += downtime_transit
				downtime_transit = 0
								
			# filter out failures that did not happen on specific date
			for failure_row in node_dataset:
				if failure_row['Prob Started'].date() == date_time.date():
					failures_per_date += (failure_row,)

				elif failure_row['Prob Started'].date() > date_time.date():
					break

			# SvrLogger.write_log('Failures are: ')
			for failure in failures_per_date:
				# SvrLogger.write_log('Prob Started:' + str(failure['Prob Started']) + ', Prob Fixed: ' + str(failure['Prob Fixed']) + ', Down Time: ' + \
				# 	str(failure['Down Time']))
				continue

			failures_per_date = cls.__duplicate_overlap_check(failures_per_date, downtime_acc)
			# SvrLogger.write_log('After duplicate and overlap filtering, failures are:')
			for failure in failures_per_date:
				# SvrLogger.write_log('Prob Started:' + str(failure['Prob Started']) + ', Prob Fixed: ' + str(failure['Prob Fixed']) + ', Down Time: ' + \
				# 	str(failure['Down Time']))
				continue

			# failures that happen on the same date classify into two groups based on the date when failure is removed
			# 1st group takes into account failures that are removed on the current day
			# 2nd group takes into account failures which downtime exhibits the current day
			for failure in failures_per_date:
				# failures that happend and recovered on the same date accumulate downtime to compute availability for the current day
				if failure['Prob Started'].date() == failure['Prob Fixed'].date():
					downtime_acc += failure['Down Time']

				# failures which downtime exhibits current day are memorized to compute availability for following days
				elif downtime_transit == 0:
					downtime_until_end_of_day = (date_time + datetime.timedelta(days = 1)).replace(hour = 0, minute = 0) - failure['Prob Started']
					downtime_acc += (downtime_until_end_of_day.seconds // 60)
					downtime_transit = failure['Down Time'] - (downtime_until_end_of_day.seconds // 60)

				else:
					# SvrLogger.write_log('Failure [Prob Started = ' + str(failure['Prob Started'].date()) + ', Prob Fixed = ' + str(failure['Prob Fixed'].date()) + \
					# 	'] was ignored due to downtime overcapacity!')
					continue

			# compute availability for the current day
			# SvrLogger.write_log('Accumulated downtime is ' + str(downtime_acc))
			# SvrLogger.write_log('Transit downtime is ' + str(downtime_transit))

			uptime = Uptime.DAY_IN_MINUTES - downtime_acc
			# SvrLogger.write_log('Uptime is ' + str(uptime))
			uptime = uptime / (uptime + downtime_acc)				
			avail += (uptime,)
			# SvrLogger.write_log('Availability is ' + str(avail[-1]))
			
			# update datetime to next day for next iteration
			date_time += datetime.timedelta(days = 1)

		return avail


	def __duplicate_overlap_check(cls, failures, downtime_acc):
		tmp_data = list()

		for failure in failures:
			add_flag = True
			if ((failure['Prob Fixed'] - failure['Prob Started'].replace(hour = 0, minute = 0)).seconds // 60) < downtime_acc:
				# SvrLogger.write_log('Failure [' + str(failure['Prob Started']) + ', ' + str(failure['Prob Fixed']) + \
				# 	'] is ignored due to downtime_acc = ' + str(downtime_acc))
				continue

			elif ((failure['Prob Started'] - failure['Prob Started'].replace(hour = 0, minute = 0)).seconds // 60) < downtime_acc:
				# SvrLogger.write_log('Failure [' + str(failure['Prob Started']) + ', ' + str(failure['Prob Fixed']) + \
				# 	'] changed to')
				failure['Prob Started'] = failure['Prob Started'].replace(hour = downtime_acc // 60, minute = downtime_acc % 60)
				# SvrLogger.write_log(failure['Prob Started'])

			if len(tmp_data) == 0:
				tmp_data.append(failure)

			for i in range(len(tmp_data)):
				# TC1
				if failure['Prob Started'] < tmp_data[i]['Prob Started'] and failure['Prob Fixed'] > tmp_data[i]['Prob Started']\
					and failure['Prob Fixed'] < tmp_data[i]['Prob Fixed']:
					# SvrLogger.write_log('Failures [' + str(failure['Prob Started']) + ', ' + str(failure['Prob Fixed']) + '], [' \
					# 	+ str(tmp_data[i]['Prob Started']) + ', ' + str(tmp_data[i]['Prob Fixed']) + '] are merged!')
					tmp_data[i]['Prob Started'] = failure['Prob Started']
					tmp_data[i]['Down Time'] = (tmp_data[i]['Prob Fixed'] - tmp_data[i]['Prob Started']).seconds // 60
					add_flag = False
				
				# TC2
				elif failure['Prob Started'] > tmp_data[i]['Prob Started'] and failure['Prob Started'] < tmp_data[i]['Prob Fixed']\
					and failure['Prob Fixed'] > tmp_data[i]['Prob Fixed']:
					# SvrLogger.write_log('Failures [' + str(failure['Prob Started']) + ', ' + str(failure['Prob Fixed']) + '], [' \
					# 	+ str(tmp_data[i]['Prob Started']) + ', ' + str(tmp_data[i]['Prob Fixed']) + '] are merged!')
					tmp_data[i]['Prob Fixed'] = failure['Prob Fixed']
					tmp_data[i]['Down Time'] = (tmp_data[i]['Prob Fixed'] - tmp_data[i]['Prob Started']).seconds // 60
					add_flag = False

				# TC3
				elif failure['Prob Started'] < tmp_data[i]['Prob Started'] and failure['Prob Fixed'] > tmp_data[i]['Prob Fixed']:
					# SvrLogger.write_log('Failure [' + str(failure['Prob Started']) + ', ' + str(failure['Prob Fixed']) + '] is ignored due to overlapping with failure ['+\
					# 	str(tmp_data[i]['Prob Started']) + ', ' + str(tmp_data[i]['Prob Fixed']) + ']')
					tmp_data[i]['Prob Started'] = failure['Prob Started']
					tmp_data[i]['Prob Fixed'] = failure['Prob Fixed']
					tmp_data[i]['Down Time'] = (tmp_data[i]['Prob Fixed'] - tmp_data[i]['Prob Started']).seconds // 60
					add_flag = False

				# TC4
				elif failure['Prob Started'] > tmp_data[i]['Prob Started'] and failure['Prob Fixed'] < tmp_data[i]['Prob Fixed']:
					add_flag = False

				# TC5
				elif failure['Prob Started'] == tmp_data[i]['Prob Started'] and failure['Prob Fixed'] == tmp_data[i]['Prob Fixed']:
					add_flag = False 

			if add_flag:
				tmp_data.append(failure)

		# SvrLogger.write_log('')

		return tuple(tmp_data)


	def __get_avail_data_ldns(cls):
		date_time = cls._data[1][0].replace(hour = 0, minute = 0)
		downtime_acc = 0
		avail_data = dict()

		for i in range(cls._data[0] - 2):

			if date_time.date() != cls._data[1][2 * i + 1]:
				while date_time.date() != cls._data[1][2 * i + 1].date():
					uptime = Uptime.DAY_IN_MINUTES - downtime_acc
					uptime = uptime / (uptime + downtime_acc)
					date_time += datetime.timedelta(days = 1)
					avail_data[date_time] =  uptime
					downtime_acc = 0

			if cls._data[1][2 * i + 2].date() == cls._data[1][2 * i + 1].date() and date_time.date() == cls._data[1][2 * i + 1].date():
				downtime_acc = downtime_acc + ((cls._data[1][2 * i + 2] - cls._data[1][2 * i + 1]).total_seconds() // 60)
			
			elif cls._data[1][2 * i + 2].date() != cls._data[1][2 * i + 1].date():
				while date_time.date() != cls._data[1][2 * i + 1].date():
					uptime = 1
					date_time += datetime.timedelta(days = 1)
					avail_data[date_time] =  uptime

				date_time += datetime.timedelta(days = 1)
				downtime_acc = (downtime_acc + (date_time - cls._data[1][2 * i + 1]).total_seconds() // 60)			
				uptime = Uptime.DAY_IN_MINUTES - downtime_acc
				uptime = uptime / (uptime + downtime_acc)
				avail_data[date_time] =  uptime

				while date_time.date() != cls._data[1][2 * i + 2].date():
					uptime = 0
					avail_data[date_time] =  uptime
					date_time += datetime.timedelta(days = 1)

				downtime_acc = (cls._data[1][2 * i + 2] - date_time).total_seconds() // 60

		return avail_data
			

	def __bootstrap(cls, data):
		sample = np.random.choice(data, size = round(len(data) / 2))
		boot_means = tuple()

		for _ in range(1000):
		    bootsample = np.random.choice(sample, size = round(len(data) / 2), replace = True)
		    boot_means += (bootsample.mean(),)

		bootmean = np.mean(boot_means)
		bootmean_std = np.std(boot_means)


	def __sma(cls, tbf):
		smoothed_data = tuple()

		if len(tbf) < utils.TRAIN_DATA_SIZE:
			window_size = 4
		else:
			window_size = round(len(tbf) / utils.TRAIN_DATA_SIZE)

		for i in range(len(tbf) - window_size):
			sma_avg = 0
			
			for j in range(window_size):
				sma_avg += tbf[i + j]

			smoothed_data += (sma_avg / window_size,)

		return smoothed_data