import math
import numpy.random
import numpy as np
from inspect import currentframe, getframeinfo

from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions, DatasetType, FailureEventMode, OdeType
from data_provider import DataProvider
from failure_provider import FailureProvider
from task import Task
from mdp_logger import MdpLogger
from dataset_statistics import DatasetStatistics
from support_vector_regression import SupportVectorRegression

# constants
GIGABYTES = 1000000

class OffloadingSite:

	def __init__(self, mips, memory, data_storage, offloading_site_code, failure_placeholder, name, node_candidate):
		self.__evaluate_params(mips, memory, data_storage, offloading_site_code)

		self._mips = mips
		self._memory = memory
		self._data_storage = data_storage
		self._offloading_site_code = offloading_site_code
		self._node_candidate = node_candidate

		# prefix name is added according to offloading site type
		if self._offloading_site_code in [OffloadingSiteCode.EDGE_DATABASE_SERVER, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, \
			OffloadingSiteCode.EDGE_REGULAR_SERVER]:

			if self._offloading_site_code == OffloadingSiteCode.EDGE_DATABASE_SERVER:
				self._name = 'EDGE_DATABASE_SERVER_' + str(name)
				self._offloading_action_index = OffloadingActions.EDGE_DATABASE_SERVER

			elif self._offloading_site_code == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
				self._name = 'EDGE_COMPUTATIONAL_SERVER_' + str(name)
				self._offloading_action_index = OffloadingActions.EDGE_COMPUTATIONAL_INTENSIVE_SERVER

			elif self._offloading_site_code == OffloadingSiteCode.EDGE_REGULAR_SERVER:
				self._name = 'EDGE_REGULAR_SERVER_' + str(name)
				self._offloading_action_index = OffloadingActions.EDGE_REGULAR_SERVER

		elif self._offloading_site_code == OffloadingSiteCode.CLOUD_DATA_CENTER:
			self._name = "CLOUD_DATA_CENTER_" + str(name)
			self._offloading_action_index = OffloadingActions.CLOUD_DATA_CENTER

		self._memory_consumption = 0
		self._data_storage_consumption = 0
		self._failure_provider = None
		self._dataset_stats = None
		self._svr = None
		self._discrete_epoch_counter = 0
		self._failure_event_mode = None
		self._failure_cnt = 0

		if type(failure_placeholder) == FailureProvider:
			self._failure_provider = failure_placeholder
			self._failure_event = self._failure_placeholder.get_failure_event_poisson()
			self._failure_event_mode = FailureEventMode.POISSON_FAILURE

		elif type(failure_placeholder) == DatasetStatistics:
			self._dataset_stats = failure_placeholder
			self._failure_event = None
			self._avail_probability_set = None
			self._avail_probability = 0
			self._failure_event_mode = FailureEventMode.TEST_DATASET_FAILURE
			self._failure_event_flag = False

			# self._dataset_stats.compute_mtbf_mttr()
			# this is a hack
			self.deploy_svr()


	def get_offloading_site_code(cls):
		return cls._offloading_site_code


	def get_name(cls):
		return cls._name


	# get CPU processing speed expressed in millions of instructions per second
	def get_millions_of_instructions_per_second(cls):
		return cls._mips


	# get memory (Gb)
	def get_memory(cls):
		return cls._memory


	# get memory consumption
	def get_memory_consumption(cls):
		return cls._memory_consumption


	# get data storage
	def get_data_storage(cls):
		return cls._data_storage


	def get_offloading_action_index(cls):
		return cls._offloading_action_index


	def get_avail_prob_test_size(cls):
		return len(cls._avail_probability_set)


	def get_failure_transition_probability(cls, indicator):
		if cls._failure_event_mode == FailureEventMode.POISSON_FAILURE:
			return cls._failure_provider.get_failure_transition_probability(cls._discrete_epoch_counter)	
		
		elif cls._failure_event_mode == FailureEventMode.TEST_DATASET_FAILURE:
			# print('Len: ' + str(len(cls._avail_probability_set)))
			# print('Name: ' + cls._name)

			if indicator == OdeType.MDP_SVR:
				if len(cls._avail_probability_set) == 0:
					cls.__evaluate_failure_test()

				if cls._avail_probability >= 0.95 and cls._offloading_site_code != OffloadingSiteCode.CLOUD_DATA_CENTER:
					return 0
				else:
					return (1 - cls._avail_probability)


			elif indicator == OdeType.EFPO:
				return cls._dataset_stats.get_failure_transition_probability(cls._discrete_epoch_counter)


	def get_server_failure_probability(cls):
		if cls._failure_event_mode == FailureEventMode.POISSON_FAILURE:
			return cls._failure_provider.get_server_failure_probability()

		else:
			return 0.9


	def get_network_failure_probability(cls):
		if cls._failure_event_mode == FailureEventMode.POISSON_FAILURE:
			return cls._failure_provider.get_network_failure_probability()

		else:
			return 0.1


	def get_failure_cnt(cls):
		return cls._failure_cnt


	def reset_failure_cnt(cls):
		cls._failure_cnt = 0


	def get_node_candidate(cls):
		return cls._node_candidate


	def deploy_svr(cls):
		cls._svr = SupportVectorRegression(cls._dataset_stats, DatasetType.LANL_DATASET, 'rbf', cls._name, cls._node_candidate)
		cls._svr.train()
		cls._failure_event = cls._svr.get_test_data()
		cls._avail_probability_set = cls._svr.get_predicted_data()


	def reset_test_data(cls):
		# MdpLogger.write_log('\n\nRESETTING TRAIN DATA for ' + cls._name)
		cls._failure_event = cls._svr.get_test_data()
		cls._avail_probability_set = cls._svr.get_predicted_data()


	def execute(cls, task):
		if not isinstance(task, Task):
			raise ValueError("Task for execution on offloading site should be Task class instance!")

		offloadable = task.is_offloadable()

		if not offloadable:
			# MdpLogger.write_log("Task is not offloadable! (off = " + str(offloadable) + ")")
			return ExecutionErrorCode.EXE_NOK

		if cls._failure_event_mode == FailureEventMode.POISSON_FAILURE:
			if cls._failure_event <= cls._discrete_epoch_counter:
				#print("Offloading failure occured on offloading site " + cls._name + "!")
				# MdpLogger.write_log("Offloading failure occured on offloading site " + cls._name + "!")
				return ExecutionErrorCode.EXE_NOK

		elif cls._failure_event_mode == FailureEventMode.TEST_DATASET_FAILURE:
			if cls._failure_event_flag:
				#print("Offloading failure occured on offloading site " + cls._name + "!")
				# MdpLogger.write_log("Offloading failure occured on offloading site " + cls._name + "!")
				return ExecutionErrorCode.EXE_NOK
		
		if not task.execute():
			raise ValueError("Task execution operation is not executed properly! Please check the code of execute() method in Task class!")

		print_text = "Task " + task.get_name()
		task_data_storage_consumption = task.get_data_in() + task.get_data_out()
		task_memory_consumption = task.get_memory()

		cls._data_storage_consumption = cls._data_storage_consumption + (task_data_storage_consumption / GIGABYTES)
		cls._memory_consumption = cls._memory_consumption + task_memory_consumption

		# MdpLogger.write_log('Filename:' + getframeinfo(currentframe()).filename + ', Line = ' + str(getframeinfo(currentframe()).lineno))
		# MdpLogger.write_log('#########################################################################################')
		# MdpLogger.write_log('######################## TASK AND OFFLOADING SITE RESOURCE CONSUMPTION ##################')
		# MdpLogger.write_log('#########################################################################################')

		# MdpLogger.write_log(task.get_name() + " task current memory consumption: " + \
		# 	str(task_memory_consumption) + ' Gb')
		# MdpLogger.write_log(task.get_name() + " task current data storage consumption: " + \
		# 	str(task_data_storage_consumption / GIGABYTES) + ' Gb')
		# MdpLogger.write_log(cls._name + " current memory consumption: " + \
		# 	str(cls._memory_consumption) + "Gb (max = " + str(cls._memory) + "Gb)")
		# MdpLogger.write_log(cls._name + " current data storage consumption: " + \
		# 	str(cls._data_storage_consumption) + "Gb (max = " + str(cls._data_storage) + "Gb)\n")
		# MdpLogger.write_log(print_text + "(off = " + str(offloadable) + ") is executed on offloading site " + \
		# 	cls._name + "!\n")
		
		return ExecutionErrorCode.EXE_OK


	def print_system_config(cls):
		MdpLogger.write_log("################### " + ("EDGE SERVER" if cls._offloading_site_code in [OffloadingSiteCode.EDGE_DATABASE_SERVER, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, \
				OffloadingSiteCode.EDGE_REGULAR_SERVER] else "CLOUD DATA CENTER") + " SYSTEM CONFIGURATION ###################")
		MdpLogger.write_log("Name: " + cls._name)
		MdpLogger.write_log("CPU: " + str(cls._mips) + " M cycles")
		MdpLogger.write_log("Memory: " + str(cls._memory) + " Gb")
		MdpLogger.write_log("Data Storage: " + str(cls._data_storage) + " Gb")
		# pass


	# memory and data storage consumption are updated after task execution is done
	def flush_executed_task(cls, task):
		if not isinstance(task, Task):
			# MdpLogger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK
		
		cls._memory_consumption = cls._memory_consumption - task.get_memory()
		cls._data_storage_consumption = cls._data_storage_consumption - ((task.get_data_in() + task.get_data_out()) / GIGABYTES)

		# print(task.get_name() + " task current memory consumption: " + str(task.get_memory()))
		# print(task.get_name() + " task current data storage consumption: " + str((task.get_data_in() + task.get_data_out()) / GIGABYTES))
		# print(cls._name + " current memory consumption: " + str(cls._memory_consumption) + "Gb (max = " + str(cls._memory) + "Gb)")
		# print(cls._name + " current data storage consumption: " + str(cls._data_storage_consumption) + "Gb (max = " + str(cls._data_storage) + "Gb)\n")

		if cls._memory_consumption < 0 or cls._data_storage_consumption < 0:
			raise ValueError("Memory consumption: " + str(cls._memory_consumption) + "Gb, data storage consumption: " + str(cls._data_storage_consumption) + \
				"Gb, both should be positive! Node: " + cls._name + ", task: " + task.get_name())


	# check the validity of task deployment on offloading site (Cloud DC or Edge server) regarding to resource capacity (memory and data storage)
	def check_validity_of_deployment(cls, task):
		if not isinstance(task, Task):
			MdpLogger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK

		# check that task resouce requirements fits offloading sites's resource capacity
		if cls._data_storage > (cls._data_storage_consumption + ((task.get_data_in() + task.get_data_out()) / GIGABYTES)) and \
			cls._memory > (cls._memory_consumption + task.get_memory()):
			return ExecutionErrorCode.EXE_OK

		return ExecutionErrorCode.EXE_NOK


	def evaluate_failure_event(cls):
		if cls._failure_event_mode == FailureEventMode.POISSON_FAILURE:
			cls.__evaluate_failure_poisson()

		elif cls._failure_event_mode == FailureEventMode.TEST_DATASET_FAILURE:
			cls.__evaluate_failure_test()

		
	def reset_discrete_epoch_counter(cls):
		cls._discrete_epoch_counter = 0


	def update_ode_info(cls, ode_type):
		cls._ode_type = ode_type


	def __evaluate_failure_poisson(cls):
		cls._discrete_epoch_counter = cls._discrete_epoch_counter + 1

		if cls._failure_event < cls._discrete_epoch_counter:
			cls._failure_event = cls._failure_provider.get_failure_event_poisson() - 1
			cls._discrete_epoch_counter = 1

			if cls._failure_event < 0:
				cls._failure_event = 0

			# Logger.write_log(cls._name + " failure event via Poisson in " + str(cls._failure_event) + " discrete epochs!")
			return

		# Logger.write_log("Offloading site " + cls._name + ": " + str(cls._failure_event - cls._discrete_epoch_counter) + " discrete epoch until failure event!")


	def __evaluate_failure_test(cls):
		#MdpLogger.write_log('Discrete epoch counter: ' + str(cls._discrete_epoch_counter))
					# did failure happen in previous epoch
		if cls._failure_event_flag:
			cls._discrete_epoch_counter = 1

		else:
			cls._discrete_epoch_counter += 1

		if len(cls._failure_event) > 0:

			# draw sample from probability distribution to determine will failure happen in this current epoch
			choice = np.random.choice(2, 1, p = (cls._failure_event[0], \
				1 - cls._failure_event[0]))[0]

			#MdpLogger.write_log('Failure probability: ' + str(round(1 - cls._failure_event[0], 3)))

			if choice:
				cls._failure_event_flag = True
				# MdpLogger.write_log('On ' + cls._name + ' failure WILL occur!')
				cls._failure_cnt += 1

			else:
				cls._failure_event_flag = False
				# MdpLogger.write_log('On ' + cls._name + ' failure WILL_NOT occur!')

			if len(cls._failure_event) > 1:
				cls._failure_event = cls._failure_event[1:]			

				if cls._ode_type == OdeType.MDP_SVR:
					cls._avail_probability_set = cls._avail_probability_set[1:]
					cls._avail_probability = cls._avail_probability_set[0]
					if cls._avail_probability > 1:
						cls._avail_probability = 1
			
			else:
				cls._failure_event = tuple()
				cls._avail_probability = 0
				cls._avail_probability_set = tuple()

			#MdpLogger.write_log('Predictive failure probability: ' + str(round(1 - cls._avail_probability, 3)) + '\n\n')

		elif len(cls._failure_event) == 0:
			# MdpLogger.write_log(cls._name + ' requires new dataset!\n')
			(cls._failure_event, cls._avail_probability_set) = cls._svr.get_new_test_predicted_data(cls._ode_type)
			cls._avail_probability = cls._avail_probability_set[0]


	def __evaluate_params(cls, cpu, memory, data_storage, offloading_site_code):
		if cpu <= 0 or type(cpu) is not int:
			raise ValueError("CPU should be positive integer!")

		if memory <= 0 or type(memory) is not int:
			raise ValueError("Memory should be positive integer!")

		if data_storage <= 0 or type(data_storage) is not int:
			raise ValueError("Input data should be positive integer!")

		if isinstance(offloading_site_code, OffloadingSiteCode):
			raise TypeError("Offloadable site code should be OffloadingSiteCode class object!")