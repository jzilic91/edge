import numpy as np

class Statistics:

	def __init__(self, offloading_sites):
		self._time_completion = tuple()
		self._energy_consumption = tuple()
		self._rewards = tuple()
		self._offloading_distribution_dict = dict()
		self._off_fail_freq_per_off_site_dict = dict()
		self._single_app_time_comp = list()
		self._single_app_energy_consum = list()
		self._failure_rates = tuple()

		for offloading_site in offloading_sites:
			self._offloading_distribution_dict[offloading_site.get_name()] = 0
			self._off_fail_freq_per_off_site_dict[offloading_site.get_name()] = 0
			

	def print_average_time_completion(cls):		
		for key, value in cls._time_completion_dict.items():
			print("After " + str(key) + " executions, average is " + str(round(np.mean(value), 2)) + " s")


	def print_average_energy_consumption(cls):		
		for key, value in cls._energy_consumption_dict.items():
			print("After " + str(key) + " executions, average is " + str(round(np.mean(value), 2)) + " J")


	def print_average_rewards(cls):
		for key, value in cls._rewards_dict.items():
			print("After " + str(key) + " executions, average is " + str(round(np.mean(value), 2)))


	def print_offloading_distribution(cls):
		print(cls._offloading_distribution_dict)


	def print_offloading_failure_frequency(cls):
		print(cls._off_fail_freq_per_off_site_dict)


	def add_time_comp(cls, time_completion):
		cls._time_completion += (time_completion,)


	def add_energy_eff(cls, energy_consumption):
		cls._energy_consumption += (energy_consumption,)


	def add_failure_rate(cls, failure_rates):
		cls._failure_rates += (failure_rates,)


	def add_reward(cls, rewards):
		cls._rewards += (rewards,)


	def add_time_comp_single_app_exe(cls, single_app_exe_time_comp):
		cls._single_app_time_comp.append(single_app_exe_time_comp)


	def add_energy_consum_single_app_exe(cls, single_app_energy_consum):
		cls._single_app_energy_consum.append(single_app_energy_consum)


	def add_offload(cls, offloading_site_name):
		if offloading_site_name in cls._offloading_distribution_dict.keys():
			cls._offloading_distribution_dict[offloading_site_name] = cls._offloading_distribution_dict[offloading_site_name] + 1
			return

		raise ValueError("Offloading site " + offloading_site_name + " does not exists in dictionary in Statistics object!")


	def add_offload_fail(cls, offloading_site_name_fail):
		if offloading_site_name_fail in cls._off_fail_freq_per_off_site_dict.keys():
			cls._off_fail_freq_per_off_site_dict[offloading_site_name_fail] = cls._off_fail_freq_per_off_site_dict[offloading_site_name_fail] + 1
			return

		raise ValueError("Offloading site " + offloading_site_name_fail + " does not exists in dictionary in Statistics object!")


	def get_time_completion_mean(cls):
		return round(np.mean(cls._time_completion), 3)


	def get_energy_consumption_mean(cls):
		return round(np.mean(cls._energy_consumption), 3)


	def get_failure_rates_mean(cls):
		return round(np.mean(cls._failure_rates), 3)


	def get_rewards_mean(cls):
		return np.mean(cls._rewards)


	def get_time_completion_var(cls):
		return round(np.var(cls._time_completion), 3)


	def get_energy_consumption_var(cls):
		return round(np.var(cls._energy_consumption), 3)


	def get_failure_rates_var(cls):
		return round(np.var(cls._failure_rates), 3)


	def get_rewards_var(cls):
		return np.var(cls._rewards)


	def get_offloading_distribution(cls):
		return cls._offloading_distribution_dict


	def get_offloading_failure_frequencies(cls):
		return cls._off_fail_freq_per_off_site_dict


	def get_offloading_distribution_relative(cls):
		sum_ = sum(cls._offloading_distribution_dict.values())
		rel_dict = dict()

		for key, value in cls._offloading_distribution_dict.items():
			if sum_ != 0:
				rel_dict[key] = round((value / sum_) * 100, 2)
			else:
				rel_dict[key] = 0

		return rel_dict


	def get_offloading_failure_relative(cls):
		sum_ = sum(cls._off_fail_freq_per_off_site_dict.values())
		rel_dict = dict()

		for key, value in cls._off_fail_freq_per_off_site_dict.items():
			if sum_ != 0:
				rel_dict[key] = round((value / sum_) * 100, 2)
			else:
				rel_dict[key] = 0

		return rel_dict


	def get_num_of_offloadings(cls):
		return sum(cls._offloading_distribution_dict.values())


	def get_num_of_offloading_failures(cls):
		return sum(cls._off_fail_freq_per_off_site_dict.values())


	def get_single_app_time_comp_mean(cls):
		return np.mean(cls._single_app_time_comp)


	def get_single_app_app_energy_consum_mean(cls):
		return np.mean(cls._single_app_energy_consum)


	def get_single_app_time_comp_std(cls):
		return np.std(cls._single_app_time_comp)


	def get_single_app_app_energy_consum_std(cls):
		return np.std(cls._single_app_energy_consum)
