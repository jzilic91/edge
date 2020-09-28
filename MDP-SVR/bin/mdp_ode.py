import random, math, mdptoolbox, mdptoolbox.example, numpy as np
from inspect import currentframe, getframeinfo

from ode import OffloadingDecisionEngine
from offloading_site import OffloadingSite
from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions
from task import Task
from svr_logger import SvrLogger
from mdp_logger import MdpLogger


class MdpOde(OffloadingDecisionEngine):

	# initializes parameters that are neccessary for decision engines deployment
	def initialize_params(cls):
		cls.__init_MDP_settings()


	# offloading function
	def offload(cls, tasks):
		if not tasks:
			raise ValueError("Tasks should not be empty in ODE class!")

		for task in tasks:
			if not isinstance(task, Task):
				raise ValueError("Tasks should be Task object instance in ODE class!")

		# update previous node for offloading decisions and MDP state transitions
		cls._previous_node = cls._current_node
		task_completion_time_array = tuple()
		task_energy_consumption_array = tuple()
		task_overall_reward_array = tuple()

		# validity deployment vector is used to denote offloading sites as available or not available due to offloading failures or resource limitations
		validity_vector = [True for i in range(len(cls._offloading_sites))]

		non_offloadable_flag = False 
		
		for task in tasks:
			# check is at least one task offloadable
			# if yes, then increment epoch counter and load new test failure sample
			# otherwise, no need to increment epoch counters and load new test failure sample
			# since reliability estimation from SVR or EFPO is not relevant because task will be executed on 
			# mobile device and not on offloading site
			if task.is_offloadable() and non_offloadable_flag == False:
				non_offloadable_flag = True
				cls._OffloadingDecisionEngine__increment_discrete_epoch_counters()

			task_completion_time = 0
			task_energy_consumption = 0
			task_overall_reward = 0
			task_failure_time_cost = 0
			task_failure_energy_cost = 0
			task_failures = 0
			candidate_node = None
			
			while True:
				# if task is not offloadable, then mobile device is considered as offloading site for task execution
				candidate_node, validity_vector = cls.__offloading_decision(task, validity_vector)
				
				# random offloading site checks validity of such task deployment regards to it's own resource capacity			
				if not candidate_node.check_validity_of_deployment(task):
					# in current simulator version all offloading sites should have sufficient resource requirements for task execution 
					raise ValueError(candidate_node.get_name() + " does not have validity for task deployment!")

				# Logger.write_log(cls._previous_node.get_name() + " -> " + candidate_node.get_name())

				# compute task execution cost in terms of mobile device energy consumption and application time completion
				(uplink_time, execution_time, downlink_time, task_completion_time_tmp) = cls._OffloadingDecisionEngine__compute_complete_task_time_completion(task, candidate_node, cls._previous_node)
				# Logger.write_log("Uplink time: " + str(uplink_time) + "s")
				# Logger.write_log("Execution time: " + str(execution_time) + "s")
				# Logger.write_log("Downlink time: " + str(downlink_time) + "s")
				# Logger.write_log("Task completion time: " + str(task_completion_time_tmp) + "s\n")

				(uplink_energy, execution_energy, downlink_energy, task_energy_consumption_tmp) = \
					cls._OffloadingDecisionEngine__compute_complete_energy_consumption(uplink_time, execution_time, downlink_time, candidate_node, cls._previous_node)
				# Logger.write_log("Uplink energy: " + str(uplink_energy) + "J")
				# Logger.write_log("Execution/Idle energy: " + str(execution_energy) + "J")
				# Logger.write_log("Downlink energy: " + str(downlink_energy) + "J")
				# Logger.write_log("Task energy: " + str(task_energy_consumption_tmp) + "J")
				
				# if task deployment on offloading site is valid, then task is going to be executed
				if not candidate_node.execute(task):
					validity_vector[candidate_node.get_offloading_action_index()] = False
					cls._statistics.add_offload_fail(candidate_node.get_name())
					task_failures += 1

					(task_completion_time_tmp, task_energy_consumption_tmp, task_overall_reward_tmp) = \
						cls._OffloadingDecisionEngine__compute_failure_cost(candidate_node, cls._previous_node)

					task_completion_time = task_completion_time + task_completion_time_tmp
					task_failure_time_cost += task_completion_time_tmp

					task_energy_consumption = task_energy_consumption + task_energy_consumption_tmp
					task_failure_energy_cost += task_energy_consumption_tmp
					
					task_overall_reward = task_overall_reward - task_overall_reward_tmp

					if any(validity_vector):
						continue
					else:
						raise ValueError("None of the offloading sites can execute task " + task.get_name() + " due to resource limitations or offloading failures!")

				task_completion_time = round(task_completion_time + task_completion_time_tmp, 3)
				task_completion_time_array += (task_completion_time,)
				task_energy_consumption = round(task_energy_consumption + task_energy_consumption_tmp, 3)
				task_energy_consumption_array += (task_energy_consumption,)
				
				# MdpLogger.write_log('\nFilename: ' + getframeinfo(currentframe()).filename + ', Line = ' + str(getframeinfo(currentframe()).lineno))
				# MdpLogger.write_log("Complete task completion time: " + str(task_completion_time) + " s")
				# MdpLogger.write_log("Complete task energy: " + str(task_energy_consumption) + " J")

				# compute task time completion reward
				task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(task_completion_time)

				# compute task energy reward
				task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(task_energy_consumption)

				# compute task overall reward
				task_overall_reward_tmp = round(cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward), 3)
				# MdpLogger.write_log("Reward: " + str(task_overall_reward_tmp) + '\n')
				
				task_overall_reward = task_overall_reward + task_overall_reward_tmp
				task_overall_reward_array += (task_overall_reward),
				# MdpLogger.write_log("Complete task reward: " + str(task_overall_reward) + "\n")

				break

			cls._current_node = candidate_node
			cls._statistics.add_offload(cls._current_node.get_name())			

			# this is only for printing information
			task.save_offloading_site(cls._current_node.get_name())
			task.save_offloading_policy(cls._policy)

			# flush the current consumption from current node since task is executed
			cls._current_node.flush_executed_task(task)

		max_task_completion_time = 0
		for task_completion_time in task_completion_time_array:
			if max_task_completion_time < task_completion_time:
				max_task_completion_time = task_completion_time

		acc_task_energy_consumption = 0
		for task_energy_consumption in task_energy_consumption_array:
			acc_task_energy_consumption += task_energy_consumption

		acc_task_overall_rewards = 0
		for task_overall_reward in task_overall_reward_array:
			acc_task_overall_rewards += task_overall_reward

		# return both objectives and rewards
		return (max_task_completion_time, acc_task_energy_consumption, acc_task_overall_rewards, task_failure_time_cost, task_failure_energy_cost, task_failures)



	def __init_MDP_settings(cls):
		# P matrix represents transition probabilities along entire state space and actions of MDP state machine
		# P matrix consists of two arrays, where first represents array of actions, and second represents transition probabilities
		# rows and columns of both arrays represent each state in the state space in order (E1, E2, E3, MD) where Ex are Edge servers and MD is an mobile device
		# actions are 0 (locally) and 1 (remotely) which indicates local or remotely execution
		# transition probabilities are within number range [0,1]
		cls._P = np.array([[[0.0 for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] for i in range(len(cls._offloading_sites))] \
			for i in range(len(cls._offloading_sites))])

		# R matrix indicates reward for each state transition in MDP state machine (values can be negative and positive, integer and double)
		cls._R = np.array([[[0.0 for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] for i in range(len(cls._offloading_sites))] \
			for i in range(len(cls._offloading_sites))])

		cls._response_time_matrix = np.array([[[0.0 for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS)] for i in range(len(cls._offloading_sites))] \
			for i in range(len(cls._offloading_sites))])

		# print("P = " + str(cls._P))
		# print("R = " + str(cls._R))
		# print("Offloading sites: " + str(cls._offloading_sites))

		# check if dimensions (columns and rows) of P and R matrix corresponds to number of offloading sites
		if (cls._P.size / cls._P[0].size) != OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS:
			raise ValueError("Size of P matrix is not correct! It should contain " + str(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS) + \
				" action submatrices but it has " + str(cls._P.size / cls._P[0].size) + ".")

		for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS):
			if math.ceil(cls._P[i].size / cls._P[i][0].size) != len(cls._offloading_sites):
				raise ValueError("Number of rows of each action submatrix should be equal to number of offloading sites! Offloading sites = " + \
					str(len(cls._offloading_sites)) + ", matrix rows = " + str(math.ceil(cls._P[i].size / cls._P[i][0].size)) + " for " + \
					str(i + 1) + ".action submatrix. P[" + str(i) + "] = " + str(cls._P[i]))

			for j in range(len(cls._offloading_sites)):
				if cls._P[i][j].size != len(cls._offloading_sites):
					raise ValueError("Size of " + str(i + 1) + ".action submatrix row should be equal to number of offloading sites " + str(len(cls._offloading_sites)) + \
						" but it is " + str(cls._P[i][j].size))

		# dicsount factor is within the number range [0,1] which indicates the importance of future state values
		cls._discount_factor = 0.96

		# initialize tuple that stores optimal offloading decision policy
		cls._policy = ()

		# print('Init P matrix = ' + str(cls._P))
		# print('Init R matrix = ' + str(cls._R))


	def __offloading_decision(cls, task, validity_vector):
		while True:
			if not task.is_offloadable():
				for i in range(len(validity_vector)):
					if cls._offloading_sites[i].get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
						validity_vector[i] = False

				return (cls._mobile_device, validity_vector)

			# continue application execution from the previous offloading site where the last task execution was completed
			offloading_site_index = cls._current_node.get_offloading_action_index()
			
			# run MDP algorithm and obtain optimal offloading decision policy
			cls._policy = cls.__MDP_run(task, validity_vector)
			# print("Current node: " + cls._current_node.get_name())
			# print("Current offloading policy: " + str(cls._policy))

			# according to the optimal offloading decision policy, the task will be executed locally on the mobile device
			if cls._policy[offloading_site_index] == OffloadingActions.MOBILE_DEVICE:
			 	return (cls._offloading_sites[cls._mobile_device.get_offloading_action_index()], validity_vector)

			# according to the optimal offloading decision policy, the task will be executed remotely on one of remote offloading sites (Edge servers or Cloud DC)
			# extract transition probabilities from P matrix via index access
			trans_prob = ()
			action_index = cls._policy[offloading_site_index]
			source_node_index = cls._current_node.get_offloading_action_index()
			P_matrix_columns = len(cls._P[action_index][source_node_index])
			# print("P matrix columns [action = " + str(action_index) + "][source_node = " + str(source_node_index) + "] = " + str(cls._P[action_index][source_node_index]))

			for i in range(P_matrix_columns):
				if cls._P[action_index][source_node_index][i] != 0.0 and i != cls._mobile_device.get_offloading_action_index():
					trans_prob = trans_prob + (1.0,)
				else:
					trans_prob = trans_prob + (0.0,)
				
				# trans_prob = trans_prob + (cls._P[action_index][source_node_index][i],)

			# print("Transition probabilities for REMOTELY offloading action: " + str(trans_prob))
			offloading_site_index = np.random.choice(P_matrix_columns, 1, p = trans_prob)[0]

			if cls._offloading_sites[offloading_site_index].get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
				validity_vector[action_index] = False

				if any(validity_vector):
					continue
				else:
					offloading_site_index = cls._mobile_device.get_offloading_action_index()
					break

			break

		return (cls._offloading_sites[offloading_site_index], validity_vector)


	# run MDP algorithm to obtain optimal offloading policy
	def __MDP_run(cls, task, validity_vector):
		cls.update_P_matrix()
		cls.update_R_matrix(task, validity_vector)

		# Logger.write_log("P = " + str(cls._P))
		# Logger.write_log("R = " + str(cls._R))

		VIA = mdptoolbox.mdp.PolicyIteration(cls._P, cls._R, cls._discount_factor)
		VIA.verbose = False
		VIA.run()

		return VIA.policy