import math
import random, math, mdptoolbox, mdptoolbox.example, numpy as np
from inspect import currentframe, getframeinfo
from abc import ABC, abstractmethod

from utilities import OffloadingSiteCode, OffloadingActions
from offloading_site import OffloadingSite
from mdp_logger import MdpLogger
from efpo_statistics import Statistics

# constants for time (ms -> s) and data conversion (kb for data size and mbps for bandwdith)
KILOBYTE = 1000 					# bytes
KILOBYTE_PER_SECOND = 1000 			# 1Mbps -> 0.125 Mb/s
THOUSAND_MS = 1000 					# 1000ms -> 1s used for network latency unit conversion
GIGABYTES = 1000000

# constans for power consumption (Watts)
POWER_CONSUM_UPLINK = 1.3
POWER_CONSUM_DOWNLINK = 1.0
POWER_CONSUM_LOCAL = 0.9
POWER_CONSUM_IDLE = 0.3

OFFLOADING_FAILURE_DETECTION_TIME = 1.5 # seconds

class OffloadingDecisionEngine(ABC):

	# initial
	def __init__(self, mobile_device, edge_servers, cloud_dc, network, name):
		if not self.__evaluate_params(mobile_device, edge_servers, cloud_dc, network):
			raise ValueError("Wrong parameters passed to DummyOde object!")
		
		self._name = name
		self._mobile_device = mobile_device
		self._edge_servers = edge_servers
		self._cloud_dc = cloud_dc
		self._network = network
		self._offloading_sites = [None for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] 
		self._app_name = ""
		self._w_f_time_completion = 0.5
		self._w_f_energy_consumption = 0.5

		# initialize offloading sites (mutable in case in the future user mobility will be considered)
		for edge_server in self._edge_servers:
			self._offloading_sites[edge_server.get_offloading_action_index()] = edge_server

		# set indexes for mobile device and Cloud DC for accessing to P and R matrix elements
		self._offloading_sites[self._mobile_device.get_offloading_action_index()] = self._mobile_device
		self._offloading_sites[self._cloud_dc.get_offloading_action_index()] = self._cloud_dc

		# current node where task is executed, also corresponds to current state in MDP state space
		self._previous_node = self._mobile_device
		self._current_node = self._mobile_device

		# maintain statistics (time completion, energy efficiency, offloading distribution, offloading failure frequencies, etc.)
		self._statistics = Statistics(self._offloading_sites)

		self.initialize_params()
		super().__init__()


	def print_statistics(cls):
		print("************* " + cls._name + " *************")
		cls._statistics.print_average_time_completion()
		cls._statistics.print_average_energy_consumption()
		cls._statistics.print_average_rewards()
		cls._statistics.print_offloading_distribution()
		cls._statistics.print_offloading_failure_frequency()


	def get_time_completion_mean(cls):
		return cls._statistics.get_time_completion_mean()


	def get_energy_consumption_mean(cls):
		return cls._statistics.get_energy_consumption_mean()


	def get_rewards_mean(cls):
		return cls._statistics.get_rewards_mean()

		
	def get_offloading_distribution_mean(cls):
		return cls._statistics.get_offloading_distribution()

		
	def get_offloading_failure_frequency_mean(cls):
		return cls._statistics.get_offloading_failure_frequencies()


	# get name of offloading decision engine
	def get_name(cls):
		return cls._name #+ "_t_" + str(cls._w_f_time_completion) + "_e_" + str(cls._w_f_energy_consumption)


	def get_statistics(cls):
		return cls._statistics


	def get_app_name(cls):
		return cls._app_name


	def get_w_f_time_completion_param(cls):
		return cls._w_f_time_completion


	def get_w_f_energy_consumption_param(cls):
		return cls._w_f_energy_consumption


	def save_app_name(cls, app_name):
		cls._app_name = app_name


	def set_sensitivity_params(cls, w_f_time_completion, w_f_energy_consumption):
		cls._w_f_time_completion = w_f_time_completion
		cls._w_f_energy_consumption = w_f_energy_consumption


	@abstractmethod
	def initialize_params(cls):
		pass


	@abstractmethod
	def offload(cls, tasks):
		pass

	def __evaluate_params(cls, mobile_device, edge_servers, cloud_dc, network):
		# if not isinstance(mobile_device, MobileDevice):
		# 	return False
		if not isinstance(cloud_dc, OffloadingSite):
			MdpLogger.write_log("Cloud data center should be OffloadingSite object instance in ODE class!")
			return False

		if not edge_servers:
			MdpLogger.write_log("Edge servers should not be empty in ODE class!")
			return False

		for edge in edge_servers:
			if not isinstance(edge, OffloadingSite):
				MdpLogger.write_log("Edge servers should be OffloadingSite object instance in ODE class!")
				return False

		if not (cloud_dc.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER):
			MdpLogger.write_log("Cloud data center should be configured as cloud data center in ODE class!")
			return False

		for edge in edge_servers:
			if not (edge.get_offloading_site_code() in [OffloadingSiteCode.EDGE_DATABASE_SERVER, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, \
				OffloadingSiteCode.EDGE_REGULAR_SERVER]):
				MdpLogger.write_log("Edge server should be configured as edge server in ODE class!")
				return False

		return True


	def __increment_discrete_epoch_counters(cls):
		# MdpLogger.write_log('\nFilename: ' + getframeinfo(currentframe()).filename + ', Line = ' + str(getframeinfo(currentframe()).lineno))
		# MdpLogger.write_log('########################################################################')
		# MdpLogger.write_log('######################## FAILURE PROBABILITIES #########################')
		# MdpLogger.write_log('########################################################################')
		
		for offloading_site in cls._offloading_sites:
			if offloading_site.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
				offloading_site.evaluate_failure_event()


	# compute complete application time completion
	def __compute_complete_task_time_completion(cls, task, current_node, previous_node):
		# if bandwidth is 0 then task is executed on mobile device since there is no task transmission via wireless link
		if current_node.get_name() == previous_node.get_name():
			execution_time = cls.__compute_execution_time(task, current_node)
			# Logger.write_log("Computed execution time is " + str(execution_time))

			# return tuple as (uplink_time, execution_time, downlink_time, complete_time)
			# in this case complete_time = execution_time since there were no uplink and downlink transmissions
			# between mobile device and Cloud DC or Edge server nodes
			return (0, execution_time, 0, execution_time)			

		uplink_time = cls.__compute_uplink_time(task, current_node, previous_node)
		execution_time = cls.__compute_execution_time(task, current_node)
		
		if not task.get_out_edges():
			downlink_time = cls.__compute_downlink_time(task, cls._mobile_device, current_node)
		else:
			downlink_time = 0

		return (uplink_time, execution_time, downlink_time, uplink_time + execution_time + downlink_time)


	# compute transmission time through uplink from mobile device to Cloud DC or Edge server
	def __compute_uplink_time(cls, task, current_node, previous_node):
		return ((task.get_data_in() * KILOBYTE) / (cls.__get_network_bandwidth(current_node.get_name(), previous_node.get_name()) * KILOBYTE_PER_SECOND)) + \
			(cls.__get_network_latency(current_node.get_name(), previous_node.get_name()) / THOUSAND_MS)


	# compute transmission time through downlink from Cloud DC or Edge server to mobile device
	def __compute_downlink_time(cls, task, current_node, previous_node):
		if current_node.get_name() == previous_node.get_name():
			return 0.0

		return ((task.get_data_out() * KILOBYTE) / (cls.__get_network_bandwidth(current_node.get_name(), previous_node.get_name()) * KILOBYTE_PER_SECOND)) + \
			(cls.__get_network_latency(current_node.get_name(), previous_node.get_name()) / THOUSAND_MS)


	# compute execution time of the task on the node (mobile device, Cloud DC, Edge server)
	def __compute_execution_time(cls, task, current_node):
		# Logger.write_log("Task millions of instructions: " + str(task.get_millions_of_instructions()))
		# Logger.write_log("Current node MIPS: " + str(current_node.get_millions_of_instructions_per_second()))
		return task.get_millions_of_instructions() / current_node.get_millions_of_instructions_per_second()


	# compute complete task energy consumption from mobile device perspective
	def __compute_complete_energy_consumption(cls, uplink_time, execution_time, downlink_time, current_node, previous_node):
		uplink_time_power = 0.0
		execution_time_power = 0.0
		downlink_time_power = 0.0
		task_energy_consumption = 0.0

		#MdpLogger.write_log('Energy failure cost computation for ' + str(previous_node.get_offloading_site_code()) + ' -> ' + \
		#	str(current_node.get_offloading_site_code()) + '!')
		
		# use case: mobile device -> mobile device
		if current_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and\
			previous_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			#MdpLogger.write_log("Energy execution consumption!!!! Execution time: " + str(execution_time))
			
			execution_time_power = cls.__compute_execution_energy_consumption(execution_time)
			task_energy_consumption = uplink_time_power + execution_time_power + downlink_time_power

		# use case: mobile device -> Edge/Cloud servers
		elif current_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
			previous_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			#MdpLogger.write_log("Energy uplink consumption!!!! Uplink time: " + str(uplink_time) + ", idle time: " + str(execution_time) + ", downlink time: " + str(downlink_time))
			
			uplink_time_power = cls.__compute_uplink_energy_consumption(uplink_time)
			execution_time_power = cls.__compute_idle_energy_consumption(execution_time)
			downlink_time_power = cls.__compute_downlink_energy_consumption(downlink_time)
			task_energy_consumption = cls.__compute_offloading_energy_consumption_uplink_direction(uplink_time, execution_time, downlink_time)

		# use case: Cloud/Edge -> Cloud/Edge (successive tasks executed on the same node)
		elif current_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
			previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
			current_node.get_name() == previous_node.get_name():
			#MdpLogger.write_log("Energy consumption during remote execution!!!! Execution time: " + str(execution_time) + ", downlink time: " + str(downlink_time))
			
			execution_time_power = cls.__compute_idle_energy_consumption(execution_time)
			downlink_time_power = cls.__compute_downlink_energy_consumption(downlink_time)
			task_energy_consumption = cls.__compute_energy_consumption_during_remote_execution(execution_time, downlink_time)

		# use case: Cloud/Edge -> Cloud/Edge (successive tasks executed on the different nodes)	
		elif current_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
			previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and\
			current_node.get_name() != previous_node.get_name():
			#MdpLogger.write_log("Energy consumption during remote execution!!!! Uplink + Execution time: " + str(uplink_time + execution_time) + ", downlink time: " + str(downlink_time))
			
			execution_time_power = cls.__compute_idle_energy_consumption(uplink_time + execution_time)
			downlink_time_power = cls.__compute_downlink_energy_consumption(downlink_time)
			task_energy_consumption = cls.__compute_energy_consumption_during_remote_execution(uplink_time + execution_time, downlink_time)

		# use case: Cloud/Edge -> mobile device
		elif current_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and\
			previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
			#MdpLogger.write_log("Energy downlink consumption!!!! Downlink time: " + str(uplink_time) + ", execution time: " + str(execution_time))
			
			execution_time_power = cls.__compute_execution_energy_consumption(execution_time)
			downlink_time_power = cls.__compute_downlink_energy_consumption(uplink_time)
			task_energy_consumption = cls.__compute_offloading_energy_consumption_downlink_direction(uplink_time, execution_time)

		return (uplink_time_power, execution_time_power, downlink_time_power, task_energy_consumption)


	def __compute_failure_cost(cls, candidate_node, previous_node):
		time_cost = OFFLOADING_FAILURE_DETECTION_TIME

		# MdpLogger.write_log('Failure cost computation for '+ str(previous_node.get_offloading_site_code()) + \
		# 		' -> ' + str(candidate_node.get_offloading_site_code()))

		if candidate_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and \
			previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
	
			(_, _, _, energy_cost) = cls.__compute_complete_energy_consumption(0.0, time_cost, 0.0, candidate_node, previous_node)
			task_time_reward = cls.__compute_task_time_completion_reward(time_cost)
			task_energy_reward = cls.__compute_task_energy_consumption_reward(energy_cost)
			task_overall_reward = cls.__compute_overall_task_reward(task_time_reward, task_energy_reward)

			# MdpLogger.write_log("Failure cost only for remote idle execution!")
			# MdpLogger.write_log("Uplink time: " + str(0.0) + "s")
			# MdpLogger.write_log("Execution time: " + str(time_cost) + "s")
			# MdpLogger.write_log("Downlink time: " + str(0.0) + "s")
			# MdpLogger.write_log("Task completion cost: " + str(time_cost) + "s\n")

			# MdpLogger.write_log("Uplink energy: " + str(0.0) + "J")
			# MdpLogger.write_log("Execution energy: " + str(energy_cost) + "J")
			# MdpLogger.write_log("Downlink energy: " + str(0.0) + "J")
			# MdpLogger.write_log("Task energy: " + str(energy_cost) + "J\n")
			# MdpLogger.write_log("Total reward: -" + str(task_overall_reward))

		elif candidate_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			previous_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:

			(_, _, _, energy_cost) = cls.__compute_complete_energy_consumption(0.0, 0.0, time_cost, candidate_node, previous_node)
			task_time_reward = cls.__compute_task_time_completion_reward(time_cost)
			task_energy_reward = cls.__compute_task_energy_consumption_reward(energy_cost)
			task_overall_reward = cls.__compute_overall_task_reward(task_time_reward, task_energy_reward)

			# MdpLogger.write_log("Failure cost only for downlink failure !")
			# MdpLogger.write_log("Uplink time: " + str(0.0) + "s")
			# MdpLogger.write_log("Execution time: " + str(0.0) + "s")
			# MdpLogger.write_log("Downlink time: " + str(time_cost) + "s")
			# MdpLogger.write_log("Task completion cost: " + str(time_cost) + "s\n")

			# MdpLogger.write_log("Uplink energy: " + str(0.0) + "J")
			# MdpLogger.write_log("Execution energy: " + str(0.0) + "J")
			# MdpLogger.write_log("Downlink energy: " + str(energy_cost) + "J")
			# MdpLogger.write_log("Task energy: " + str(energy_cost) + "J\n")
			# MdpLogger.write_log("Total reward: -" + str(task_overall_reward))

		elif candidate_node.get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE and \
			previous_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			(_, _, _, energy_cost) = cls.__compute_complete_energy_consumption(time_cost, 0.0, 0.0, candidate_node, previous_node)
			task_time_reward = cls.__compute_task_time_completion_reward(time_cost)
			task_energy_reward = cls.__compute_task_energy_consumption_reward(energy_cost)
			task_overall_reward = cls.__compute_overall_task_reward(task_time_reward, task_energy_reward)

			# MdpLogger.write_log("Failure cost only for uplink failure !")
			# MdpLogger.write_log("Uplink time: " + str(time_cost) + "s")
			# MdpLogger.write_log("Execution time: " + str(0.0) + "s")
			# MdpLogger.write_log("Downlink time: " + str(0.0) + "s")
			# MdpLogger.write_log("Task completion cost: " + str(time_cost) + "s\n")

			# MdpLogger.write_log("Uplink energy: " + str(energy_cost) + "J")
			# MdpLogger.write_log("Execution energy: " + str(0.0) + "J")
			# MdpLogger.write_log("Downlink energy: " + str(0.0) + "J")
			# MdpLogger.write_log("Task energy: " + str(energy_cost) + "J\n")
			# MdpLogger.write_log("Total reward: -" + str(task_overall_reward))

		return (time_cost, energy_cost, task_overall_reward)
	
	# def __compute_failure_cost(cls, uplink_time, execution_time, downlink_time, uplink_energy, execution_energy, downlink_energy, candidate_node, previous_node):
	# 	# use case 1: local server failure 
	# 	if uplink_time == 0.0 and downlink_time == 0.0:
	# 		# compute task time completion reward
	# 		task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(execution_time)

	# 		# compute task energy reward
	# 		task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(execution_energy)

	# 		# compute task overall reward
	# 		task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward)

	# 		MdpLogger.write_log("Failure cost only for local server execution!")
	# 		MdpLogger.write_log("Uplink time: " + str(uplink_time) + "s")
	# 		MdpLogger.write_log("Execution time: " + str(execution_time) + "s")
	# 		MdpLogger.write_log("Downlink time: " + str(downlink_time) + "s")
	# 		MdpLogger.write_log("Task completion cost: " + str(execution_time) + "s\n")

	# 		MdpLogger.write_log("Uplink energy: " + str(uplink_energy) + "J")
	# 		MdpLogger.write_log("Execution energy: " + str(execution_energy) + "J")
	# 		MdpLogger.write_log("Downlink energy: " + str(downlink_energy) + "J")
	# 		MdpLogger.write_log("Task energy: " + str(execution_energy) + "J\n")
	# 		MdpLogger.write_log("Total reward: -" + str(task_overall_reward))
			
	# 		return (execution_time, execution_energy, task_overall_reward)

	# 	# determine which kind of failure happend (0 - server failure, 1 - network failure)
	# 	choice = np.random.choice(2, 1, p = (candidate_node.get_server_failure_probability(), \
	# 		candidate_node.get_network_failure_probability()))[0]

	# 	# in case of network failure we need to consider uplink and downlink
	# 	if choice:
	# 		# if downlink is present
	# 		if downlink_time != 0.0:
	# 			# determine on which link failure happend (0 - uplink, 1 - downlink)
	# 			choice = np.random.choice(2, 1, p = (0.5, 0.5))[0]

	# 			# use case 2: downlink link failure
	# 			if choice:
	# 				task_time = uplink_time + execution_time + downlink_time
	# 				task_energy = uplink_energy + execution_energy + downlink_energy

	# 				# compute task time completion reward
	# 				task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(task_time)

	# 				# compute task energy reward
	# 				task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(task_energy)

	# 				# compute task overall reward
	# 				task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward)

	# 				MdpLogger.write_log("Failure cost only for downlink failure!")
	# 				MdpLogger.write_log("Uplink time: " + str(uplink_time) + "s")
	# 				MdpLogger.write_log("Execution time: " + str(execution_time) + "s")
	# 				MdpLogger.write_log("Downlink time: " + str(downlink_time) + "s")
	# 				MdpLogger.write_log("Task completion cost: " + str(task_time) + "s\n")

	# 				MdpLogger.write_log("Uplink energy: " + str(uplink_energy) + "J")
	# 				MdpLogger.write_log("Execution energy: " + str(execution_energy) + "J")
	# 				MdpLogger.write_log("Downlink energy: " + str(downlink_energy) + "J")
	# 				MdpLogger.write_log("Task energy: " + str(task_energy) + "J\n")
	# 				MdpLogger.write_log("Total reward: -" + str(task_overall_reward))
					
	# 				return (task_time, task_energy, task_overall_reward)
			
	# 		# use case 3: uplink link failure
	# 		# compute task time completion reward
	# 		task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(uplink_time)

	# 		# compute task energy reward
	# 		task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(uplink_energy)

	# 		# compute task overall reward
	# 		task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward)

	# 		MdpLogger.write_log("Failure cost only for uplink failure!")
	# 		MdpLogger.write_log("Uplink time: " + str(uplink_time) + "s")
	# 		MdpLogger.write_log("Execution time: " + str(execution_time) + "s")
	# 		MdpLogger.write_log("Downlink time: " + str(downlink_time) + "s")
	# 		MdpLogger.write_log("Task completion cost: " + str(uplink_time) + "s\n")

	# 		MdpLogger.write_log("Uplink energy: " + str(uplink_energy) + "J")
	# 		MdpLogger.write_log("Execution energy: " + str(execution_energy) + "J")
	# 		MdpLogger.write_log("Downlink energy: " + str(downlink_energy) + "J")
	# 		MdpLogger.write_log("Task energy: " + str(uplink_energy) + "J\n")
	# 		MdpLogger.write_log("Total reward: -" + str(task_overall_reward))
					
	# 		return (uplink_time, uplink_energy, task_overall_reward)

	# 	# use case 4: offloading server failure
	# 	else:
	# 		task_time = uplink_time + execution_time
	# 		task_energy = uplink_energy + execution_energy
			
	# 		# compute task time completion reward
	# 		task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(task_time)

	# 		# compute task energy reward
	# 		task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(task_energy)

	# 		# compute task overall reward
	# 		task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward)

	# 		MdpLogger.write_log("Failure cost only for offloading server failure!")
	# 		MdpLogger.write_log("Uplink time: " + str(uplink_time) + "s")
	# 		MdpLogger.write_log("Execution time: " + str(execution_time) + "s")
	# 		MdpLogger.write_log("Downlink time: " + str(downlink_time) + "s")
	# 		MdpLogger.write_log("Task completion cost: " + str(task_time) + "s\n")

	# 		MdpLogger.write_log("Uplink energy: " + str(uplink_energy) + "J")
	# 		MdpLogger.write_log("Execution energy: " + str(execution_energy) + "J")
	# 		MdpLogger.write_log("Downlink energy: " + str(downlink_energy) + "J")
	# 		MdpLogger.write_log("Task energy: " + str(task_energy) + "J\n")
	# 		MdpLogger.write_log("Total reward: -" + str(task_overall_reward))
					
	# 		return (task_time, task_energy, task_overall_reward)

	# compute mobile device energy consumption when task is offloaded remotely on Cloud DC or Edge server
	# execution time is here used as idle time since execution time refers to task execution remotely on Cloud DC or Edge server but not an mobile device
	def __compute_offloading_energy_consumption_downlink_direction(cls, downlink_time, execution_time):
		return cls.__compute_downlink_energy_consumption(downlink_time) + cls.__compute_execution_energy_consumption(execution_time)

	def __compute_offloading_energy_consumption_uplink_direction(cls, uplink_time, idle_time, downlink_time):
		return cls.__compute_uplink_energy_consumption(uplink_time) + cls.__compute_idle_energy_consumption(idle_time) \
			+ cls.__compute_downlink_energy_consumption(downlink_time)
	
	def __compute_energy_consumption_during_remote_execution(cls, remote_execution_time, downlink_time):
		return cls.__compute_idle_energy_consumption(remote_execution_time) + cls.__compute_downlink_energy_consumption(downlink_time)

	# compute energy consumption for uplink from mobile device to Cloud DC or Edge server
	def __compute_uplink_energy_consumption(cls, uplink_time):
		return uplink_time * POWER_CONSUM_UPLINK

	# compute energy consumption for downlink from Cloud DC or Edge server
	def __compute_downlink_energy_consumption(cls, downlink_time):
		return downlink_time * POWER_CONSUM_DOWNLINK

	# compute energy consumption for task execution on the node (mobile device, Cloud DC, Edge server)
	def __compute_execution_energy_consumption(cls, execution_time):
		return execution_time * POWER_CONSUM_LOCAL

	# compute energy consumption of mobile device when task is executed on Cloud DC or Edge server (idle mode)
	def __compute_idle_energy_consumption(cls, idle_time):
		return idle_time * POWER_CONSUM_IDLE

	# compute task completion reward
	def __compute_task_time_completion_reward(cls, task_completion_time):
		if task_completion_time == 0.0:
			return 0.0

		return 1 / (1 + math.exp(task_completion_time))

	# compute task energy consumption reward
	def __compute_task_energy_consumption_reward(cls, task_energy_consumption):
		if task_energy_consumption == 0.0:
			return 0.0

		return 1 / (1 + math.exp(task_energy_consumption))

	# compute overall task reward based on weight factors applied on both task completion time reward and task energy consumption reward
	def __compute_overall_task_reward(cls, task_completion_time_reward, task_energy_consumption_reward):
		# MdpLogger.write_log("Time Reward: " + str(cls._w_f_time_completion * task_completion_time_reward) + ", Energy Reward: " + str(cls._w_f_energy_consumption * task_energy_consumption_reward))
		return (cls._w_f_time_completion * task_completion_time_reward) + (cls._w_f_energy_consumption * task_energy_consumption_reward)
	
	# get network latency between previous node (where previous task is executed) and current node (where current task will be executed)
	def __get_network_latency(cls, current_node_name, previous_node_name):
		if current_node_name == previous_node_name:
			return 0.0

		for value in cls._network[previous_node_name]:
			if value[0] == current_node_name:
				return value[1]

		raise ValueError("Cannot find network latency between " + current_node_name + " and " + previous_node_name)

	# get network bandwidth between previous node (where previous task is executed) and current node (where current task will be executed)
	def __get_network_bandwidth(cls, current_node_name, previous_node_name):
		if current_node_name == previous_node_name:
			return 0.0

		for value in cls._network[previous_node_name]:
			if value[0] == current_node_name:
				return value[2]

		raise ValueError("Cannot find network bandwidth between " + current_node_name + " and " + previous_node_name)