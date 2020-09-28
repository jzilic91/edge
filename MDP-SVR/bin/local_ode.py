from utilities import OffloadingSiteCode
from task import Task
from ode import OffloadingDecisionEngine
from svr_logger import SvrLogger

class LocalOde(OffloadingDecisionEngine):

	# initializes parameters that are neccessary for decision engines deployment
	def initialize_params(cls):
		pass

	# offloading function
	def offload(cls, tasks):
		if not tasks:
			raise ValueError("Tasks should not be empty in ODE class!")

		for task in tasks:
			if not isinstance(task, Task):
				raise ValueError("Tasks should be Task object instance in ODE class!")

		cls._OffloadingDecisionEngine__increment_discrete_epoch_counters()

		# update previous node for offloading decisions and MDP state transitions
		cls._previous_node = cls._current_node
		task_completion_time = 0
		task_energy_consumption = 0
		task_overall_reward = 0
		candidate_node = None

		# validity deployment vector is used to denote offloading sites as available or not available due to offloading failures or resource limitations
		validity_vector = [True for i in range(len(cls._offloading_sites))]

		for task in tasks:
			
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
				# Logger.write_log("Execution energy: " + str(execution_energy) + "J")
				# Logger.write_log("Downlink energy: " + str(downlink_energy) + "J")
				# Logger.write_log("Task energy: " + str(task_energy_consumption_tmp) + "J")
				
				# if task deployment on offloading site is valid, then task is going to be executed
				if not candidate_node.execute(task):
					validity_vector[candidate_node.get_offloading_action_index()] = False
					cls._statistics.add_offload_fail(candidate_node.get_name())

					(task_completion_time_tmp, task_energy_consumption_tmp, task_overall_reward_tmp) = cls._OffloadingDecisionEngine__compute_failure_cost(uplink_time, execution_time, downlink_time, \
						uplink_energy, execution_energy, downlink_energy, candidate_node, cls._previous_node)

					task_completion_time = task_completion_time + task_completion_time_tmp
					task_energy_consumption = task_energy_consumption + task_energy_consumption_tmp
					task_overall_reward = task_overall_reward - task_overall_reward_tmp

					if any(validity_vector):
						continue
					else:
						raise ValueError("None of the offloading sites can execute task " + task.get_name() + " due to resource limitations or offloading failures!")

				task_completion_time = task_completion_time + task_completion_time_tmp
				task_energy_consumption = task_energy_consumption + task_energy_consumption_tmp
				
				# Logger.write_log("Complete task completion time is " + str(task_completion_time) + "s")
				# Logger.write_log("Complete task energy is " + str(task_energy_consumption) + "J")

				# compute task time completion reward
				task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(task_completion_time)

				# compute task energy reward
				task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(task_energy_consumption)

				# compute task overall reward
				task_overall_reward_tmp = cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward)
				# Logger.write_log("Reward is " + str(task_overall_reward_tmp))

				task_overall_reward = task_overall_reward + task_overall_reward_tmp
				# Logger.write_log("Complete task reward is " + str(task_overall_reward) + "\n")

				break

			cls._current_node = candidate_node			
			cls._statistics.add_offload(cls._current_node.get_name())	

			# this is only for printing information
			task.save_offloading_site(cls._current_node.get_name())

			# flush the current consumption from current node since task is executed
			cls._current_node.flush_executed_task(task)

		# return both objectives and rewards
		return (task_completion_time, task_energy_consumption, task_overall_reward)

	def __offloading_decision(cls, task, validity_vector):
		for i in range(len(validity_vector)):
			if cls._offloading_sites[i].get_offloading_site_code() != OffloadingSiteCode.MOBILE_DEVICE:
				validity_vector[i] = False

		return (cls._mobile_device, validity_vector)