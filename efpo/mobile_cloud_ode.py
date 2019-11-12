import math

from utilities import OffloadingActions
from mdp_ode import MdpOde
from ode import OffloadingDecisionEngine
from logger import Logger

class MobileCloudOde(MdpOde):

	def update_P_matrix(cls):
		for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS): 			 # iterate through action submatrices
			for j in range(math.ceil(cls._P[i].size / cls._P[i][0].size)): 			 # iterate through rows of current action submatrix
				for k in range(math.ceil(cls._P[i][j].size / cls._P[i][j][0].size)): # iterate through columns of current action submatrix
					# # offload to k offloading site
					# if cls._offloading_sites[k].get_offloading_action_index() == i:
					# 	cls._P[i][j][k] = 1 - cls._offloading_sites[k].get_failure_transition_probability()

					# # offload to mobile device (in case of offloading failure) 
					# elif cls._mobile_device.get_offloading_action_index() == k:
					# 	cls._P[i][j][k] = cls._offloading_sites[i].get_failure_transition_probability()

					# else:
					# 	cls._P[i][j][k] = 0.0
					if cls._offloading_sites[k].get_offloading_action_index() == i:
						cls._P[i][j][k] = 1.0

					else:
						cls._P[i][j][k] = 0.0

	def update_R_matrix(cls, task, validity_vector):
		for i in range(OffloadingActions.NUMBER_OF_OFFLOADING_ACTIONS): 			 # iterate through action submatrices
			for j in range(math.ceil(cls._R[i].size / cls._R[i][0].size)): 			 # iterate through rows of current action submatrix
				for k in range(math.ceil(cls._R[i][j].size / cls._R[i][j][0].size)): # iterate through columns of current action submatrix
					# if state transition in P matrix does not exists or offloading action performs on invalid offloading site then reward should be 0
					if cls._P[i][j][k] == 0.0 or not validity_vector[i] or (i != OffloadingActions.MOBILE_DEVICE and \
						i != OffloadingActions.CLOUD_DATA_CENTER):
						cls._R[i][j][k] = 0.0
						continue
					
					# compute task completion time
					Logger.write_log(cls._offloading_sites[j].get_name() + " -> " + cls._offloading_sites[k].get_name())
					(uplink_time, execution_time, downlink_time, task_completion_time) = cls._OffloadingDecisionEngine__compute_complete_task_time_completion(task, \
						cls._offloading_sites[k], cls._offloading_sites[j])
					# Logger.write_log("Uplink time: " + str(uplink_time))
					# Logger.write_log("Execution time: " + str(execution_time))
					# Logger.write_log("Downlink time: " + str(downlink_time))
					# Logger.write_log("Task completion time: " + str(task_completion_time) + "\n")

					# compute task energy consumption
					(uplink_energy, execution_energy, downlink_energy, task_energy_consumption) = \
						cls._OffloadingDecisionEngine__compute_complete_energy_consumption(uplink_time, execution_time, downlink_time, cls._offloading_sites[k], cls._offloading_sites[j])
					# Logger.write_log("Uplink energy: " + str(uplink_energy))
					# Logger.write_log("Execution energy: " + str(execution_energy))
					# Logger.write_log("Downlink energy: " + str(downlink_energy))
					# Logger.write_log("Task energy: " + str(task_energy_consumption)+ "\n")

					# compute task time completion reward
					task_time_completion_reward = cls._OffloadingDecisionEngine__compute_task_time_completion_reward(task_completion_time)
					# Logger.write_log("Task time completion reward: " + str(task_time_completion_reward))

					# compute task energy reward
					task_energy_consumption_reward = cls._OffloadingDecisionEngine__compute_task_energy_consumption_reward(task_energy_consumption)
					# Logger.write_log("Task energy reward: " + str(task_energy_consumption_reward))

					# compute task overall reward
					task_overall_reward = cls._OffloadingDecisionEngine__compute_overall_task_reward(task_time_completion_reward, task_energy_consumption_reward)
					# Logger.write_log("Task overall reward: " + str(task_overall_reward)+ "\n")

					if task_completion_time < 0 or downlink_time < 0 or execution_time < 0 or uplink_time < 0 or task_energy_consumption < 0 or \
						task_time_completion_reward < 0 or task_energy_consumption_reward < 0 or task_overall_reward < 0:
						raise ValueError("Some value is negative, leading to negative rewards!")

					cls._R[i][j][k] = task_overall_reward