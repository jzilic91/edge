import numpy as np

APP_EXE_INTERVAL = 50

class Statistics:

	def __init__(self, offloading_sites):
		self._time_completion_dict = dict()
		self._energy_consumption_dict = dict()
		self._rewards_dict = dict()
		self._offloading_distribution_dict = dict()
		self._off_fail_freq_per_off_site_dict = dict()
		self._single_app_time_comp = list()
		self._single_app_energy_consum = list()

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

	def add_time_comp(cls, time_completion, app_execution):
		if (app_execution % APP_EXE_INTERVAL) == 0:
			if app_execution in cls._time_completion_dict.keys():
				cls._time_completion_dict[app_execution].append(time_completion)
			else:
				cls._time_completion_dict[app_execution] = [time_completion]

	def add_energy_eff(cls, energy_consumption, app_execution):
		if (app_execution % APP_EXE_INTERVAL) == 0:
			if app_execution in cls._energy_consumption_dict.keys():
				cls._energy_consumption_dict[app_execution].append(energy_consumption)
			else:
				cls._energy_consumption_dict[app_execution] = [energy_consumption]

	def add_reward(cls, rewards, app_execution):
		if (app_execution % APP_EXE_INTERVAL) == 0:
			if app_execution in cls._rewards_dict.keys():
				cls._rewards_dict[app_execution].append(rewards)
			else:
				cls._rewards_dict[app_execution] = [rewards]

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
		time_completion_dict = dict()

		for key, value in cls._time_completion_dict.items():
			time_completion_dict[key] = np.mean(value)

		print("Time completion dict: " + str(time_completion_dict))
		return time_completion_dict

	def get_energy_consumption_mean(cls):
		energy_consumption_dict = dict()

		for key, value in cls._energy_consumption_dict.items():
			energy_consumption_dict[key] = np.mean(value)

		print("Energy consumption dict: " + str(energy_consumption_dict))
		return energy_consumption_dict

	def get_rewards_mean(cls):
		rewards_dict = dict()

		for key, value in cls._rewards_dict.items():
			rewards_dict[key] = np.mean(value)

		return rewards_dict

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
		rel_dict = dict()
		for key, value in cls._off_fail_freq_per_off_site_dict.items():
			if cls._offloading_distribution_dict[key] != 0:
				rel_dict[key] = round((value / cls._offloading_distribution_dict[key]) * 100, 2)
			else:
				rel_dict[key] = 0

		return rel_dict

	def get_single_app_time_comp_mean(cls):
		return np.mean(cls._single_app_time_comp)

	def get_single_app_app_energy_consum_mean(cls):
		return np.mean(cls._single_app_energy_consum)

	def get_single_app_time_comp_std(cls):
		return np.std(cls._single_app_time_comp)

	def get_single_app_app_energy_consum_std(cls):
		return np.std(cls._single_app_energy_consum)