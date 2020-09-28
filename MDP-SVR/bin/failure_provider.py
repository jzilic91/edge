#############################
###### STD LIBRARIES ########
#############################

import math
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interpolate

from datetime import datetime
from pandas.plotting import register_matplotlib_converters


#############################
##### CUSTOM LIBRARIES ######
#############################

from utilities import NodeCategory


#############################
######### CONSTANTS #########
#############################

HOURS_TO_S = 3600   # one hour to seconds
DAYS_TO_S = 86400   # one day to seconds
WEEKS_TO_S = 604800 # one week to seconds

class FailureProvider:

	def __init__(self, data_frames, total_time, data_category):
		self._data_frames = data_frames

		self._pdf_data = list()
		self._hist_data = list()
		self._node_failure_data = dict()
		self._mtbf = 0
		self._total_time = total_time
		self._net_failures = list()
		self._data_category = data_category
		self._title = ''
		self._folder_path = ''

		if self._data_category == NodeCategory.ER_DATA:
			self._title = 'Edge Regular Server'
			self._folder_path = 'logs/PNNL/regular/'

		elif self._data_category == NodeCategory.EC_DATA:
			self._title = "Edge Computational Server"
			self._folder_path = 'logs/PNNL/computational/'

		elif self._data_category == NodeCategory.ED_DATA:
			self._title = "Edge Database Server"
			self._folder_path = 'logs/PNNL/database/'

		elif self._data_category == NodeCategory.NET_DATA:
			self._title = "Network"
			self._folder_path = 'logs/PNNL/database/'

		elif self._data_category == NodeCategory.CD_DATA:
			self._title = "Cloud Data Center"
			self._folder_path = 'logs/PNNL/cloud/'
		else:
			exit("Category " + self._data_category + " does not exist!")

		self.__extract_node_failure_data()
		self.__compute_pdf_data()
		self.__compute_hist_data()
		self.__compute_mtbf()

		register_matplotlib_converters()
		

	def get_failures(cls):
		return cls._data_frames


	def get_number_of_failures(cls):
		return len(cls._data_frames)


	def get_failure_event_poisson(cls):
		return np.random.poisson(cls._mtbf)


	def get_failure_event_pdf(cls):
		return int(cls.__get_inverse_cdf_sample())


	def get_failure_transition_probability(cls, t):
		return (round((1 - math.exp(-t / cls._mtbf)), 2))


	def get_server_failure_probability(cls):
		return round((len(cls._data_frames) - len(cls._net_failures)) / len(cls._data_frames), 2)


	def get_network_failure_probability(cls):
		return round(len(cls._net_failures) / len(cls._data_frames), 2)


	def get_node_category(cls):
		return cls._title


	def get_folder_path(cls):
		return cls._folder_path


	def add_net_failures(cls, net_failures):
		for net_failure in net_failures:
			cls._data_frames.append(net_failure)
			cls._net_failures.append(net_failure)

		cls._data_frames.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))
		cls._net_failures.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))


	def plot_pdf(cls, title):
		plt.title(title)
		plt.xlabel('Time duration (hours)')
		plt.ylabel('Probability')
		plt.plot([cls._pdf_data[i][0] for i in range(len(cls._pdf_data))], [cls._pdf_data[i][1] for i in range(len(cls._pdf_data))])
		plt.show()


	def plot_hist(cls, title):
		plt.title(title)
		plt.xlabel('Time duration (hours)')
		plt.ylabel('Frequency')
		plt.hist([cls._hist_data[i][0] for i in range(len(cls._hist_data))], bins = 30)
		plt.show()


	def plot_fail_rate_dist(cls):
		datetime_events = tuple()
		cls._data_frames.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))

		for event in cls.__convert_str_to_datetime(cls._data_frames):
			datetime_events += (event,)

		plt.hist(datetime_events, bins = 30)
		plt.suptitle('#failures = ' + str(len(cls._data_frames)))
		plt.title('Failure Rate Distribution for ' + cls._title + ' (PNNL dataset)')
		plt.xlabel('Date')
		plt.ylabel('Frequency')
		plt.show()


	def get_fail_rate_data(cls):
		datetime_events = tuple()
		cls._data_frames.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))

		for event in cls.__convert_str_to_datetime(cls._data_frames):
			datetime_events += (event,)

		counts, _, _ = plt.hist(datetime_events, bins = 700)
		return counts


	def plot_tbf(cls):
		tbf = tuple()
		cls._data_frames.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))

		datatime_frames = cls.__convert_str_to_datetime(cls._data_frames)

		for i in range(len(datatime_frames) - 1):
			tbf += ((datatime_frames[i + 1] - datatime_frames[i]).total_seconds(),)

		plt.plot(tuple(i for i in range(1, len(datatime_frames))), tbf)
		plt.suptitle('#failures = ' + str(len(cls._data_frames)))
		plt.title('TBF distribution for ' + cls._title + ' (PNNL dataset)')
		plt.xlabel('Failure index')
		plt.ylabel('TBF (seconds)')
		plt.show()


	def get_tbf_data(cls):
		tbf = tuple()
		cls._data_frames.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))

		datatime_frames = cls.__convert_str_to_datetime(cls._data_frames)

		for i in range(len(datatime_frames) - 1):
			tbf += ((datatime_frames[i + 1] - datatime_frames[i]).total_seconds() / (60 * 60 * 24),)

		return tbf


	def plot(cls):
		cls.plot_tbf()
		cls.plot_fail_rate_dist()


	def plot_node_candidate_fr(cls):
		datetime_events = tuple()
		data_frames = cls.get_node_candidate_fr()

		for event in cls.__convert_str_to_datetime(data_frames):
			datetime_events += (event,)

		plt.hist(datetime_events, bins = 10)
		plt.suptitle('#failures = ' + str(len(datetime_events)))
		plt.title('Failure Rate Distribution for ' + cls._title + ' (PNNL dataset)')
		plt.xlabel('Date')
		plt.ylabel('Frequency')
		plt.show()


	def plot_node_candidate_tbf(cls):
		tbf = cls.get_node_candidate_tbf()

		plt.plot(tuple(i for i in range(0, len(tbf))), tbf)
		plt.suptitle('#failures = ' + str(len(tbf)))
		plt.title('TBF distribution for ' + cls._title + ' (PNNL dataset)')
		plt.xlabel('Failure index')
		plt.ylabel('TBF (seconds)')
		plt.show()


	def print_stats_per_node(cls):
		print(cls._title + ' failure log:')
		for key, value in cls._node_failure_data.items():
			print(key + ': ' + str(len(value)) + ' failures')
		print()


	def get_node_candidate_tbf(cls):
		(node_hw_id, node_fail) = None, 0
		for key, value in cls._node_failure_data.items():
			if node_hw_id == None or node_fail < len(value):
				node_hw_id = key
				node_fail = len(value)

		failure_logs = tuple()
		for event in cls._data_frames:
			if event['Hardware Identifier'] == node_hw_id:
				failure_logs += (event,)

		date_time = cls.__convert_str_to_datetime(failure_logs)
		tbf = tuple()
		for i in range(len(date_time) - 1):
			tbf += ((date_time[i + 1] - date_time[i]).total_seconds() / (60 * 60 * 24),)

		return tbf 


	def get_node_candidate_fr(cls):
		(node_hw_id, node_fail) = None, 0
		for key, value in cls._node_failure_data.items():
			if node_hw_id == None or node_fail < len(value):
				node_hw_id = key
				node_fail = len(value)

		failure_logs = tuple()
		for event in cls._data_frames:
			if event['Hardware Identifier'] == node_hw_id:
				failure_logs += (event,)

		return failure_logs


	def __convert_str_to_datetime(cls, data_frames):
		conv_data = tuple()
		for data in data_frames:
			conv_data += (datetime.strptime(data['Date'], '%m/%d/%Y %H:%M'),)

		return conv_data


	def __get_inverse_cdf_sample(cls, n_bins = 40, n_samples = 1):
		hist, bin_edges = np.histogram([element for element in cls.__extract_data_points_for_cdf()], bins = n_bins, density = True)
		cum_values = np.zeros(bin_edges.shape)
		cum_values[1:] = np.cumsum(hist * np.diff(bin_edges))
		inv_cdf = interpolate.interp1d(cum_values, bin_edges)
		r = np.random.rand(n_samples)
		return inv_cdf(r)[0]
		

	def __extract_node_failure_data(cls):
		cls._data_frames.sort(key = lambda x: datetime.strptime(x['Date'], '%m/%d/%Y %H:%M'))

		for data_frame in cls._data_frames:
			if data_frame['Hardware Identifier'] in cls._node_failure_data:
				cls._node_failure_data[data_frame['Hardware Identifier']].append(datetime.strptime(data_frame['Date'], '%m/%d/%Y %H:%M'))
			else:
				cls._node_failure_data[data_frame['Hardware Identifier']] = [datetime.strptime(data_frame['Date'], '%m/%d/%Y %H:%M')]


	def __compute_pdf_data(cls):
		data_points_dict = cls.__extract_data_points_for_pdf()

		for key, value in data_points_dict.items():
			data_points_dict[key] = round(value / sum(data_points_dict.values()), 4)

		for key, value in sorted(data_points_dict.items()):
			cls._pdf_data.append((key, value))


	def __compute_hist_data(cls):
		data_points_dict = cls.__extract_data_points_for_pdf()

		for key, value in sorted(data_points_dict.items()):
			cls._hist_data.append((key, value))


	def __compute_mtbf(cls):
		cls._mtbf = round(cls._total_time / len(cls._data_frames), 4)


	def __extract_data_points_for_pdf(cls):
		data_points_dict = dict()
		for key, value in cls._node_failure_data.items():
			if len(value) == 1:
				continue

			for i in range(len(value) - 1):
				duration = value[i + 1] - value[i]
				duration_in_t_s = duration.total_seconds()
				hours = divmod(duration_in_t_s, HOURS_TO_S)
				
				if hours[0] in data_points_dict:
					data_points_dict[hours[0]] = data_points_dict[hours[0]] + 1
				else:
					data_points_dict[hours[0]] = 1

		return data_points_dict


	def __extract_data_points_for_cdf(cls):
		data_points = list()
		for key, value in cls._node_failure_data.items():
			if len(value) == 1:
				continue

			for i in range(len(value) - 1):
				duration = value[i + 1] - value[i]
				duration_in_t_s = duration.total_seconds()
				hours = divmod(duration_in_t_s, HOURS_TO_S)
				data_points.append(hours[0] + (hours[1] / HOURS_TO_S))

		return data_points