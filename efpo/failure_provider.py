import math
import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate as interpolate

from datetime import datetime

HOURS_TO_S = 3600   # one hour to seconds
DAYS_TO_S = 86400   # one day to seconds
WEEKS_TO_S = 604800 # one week to seconds

class FailureProvider:

	def __init__(self, data_frames, total_time):
		self._data_frames = data_frames

		self._pdf_data = list()
		self._hist_data = list()
		self._node_failure_data = dict()
		self._mtbf = 0
		self._total_time = total_time
		self._net_failures = list()

		self.__extract_node_failure_data()
		self.__compute_pdf_data()
		self.__compute_hist_data()
		self.__compute_mtbf()

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