import math
import numpy.random

from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions
from data_provider import DataProvider
from task import Task
from logger import Logger

# constants
GIGABYTES = 1000000

class OffloadingSite:

	def __init__(self, mips, memory, data_storage, offloading_site_code, failure_provider, name):
		self.__evaluate_params(mips, memory, data_storage, offloading_site_code)

		self._mips = mips
		self._memory = memory
		self._data_storage = data_storage
		self._offloading_site_code = offloading_site_code

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
		self._failure_provider = failure_provider
		self._failure_event = self._failure_provider.get_failure_event_poisson()
		self._discrete_epoch_counter = 0

		# print("Failure probabilities for " + self._name)
		# self._failure_provider.get_server_failure_probability()
		# self._failure_provider.get_network_failure_probability()

		# self._failure_event_pdf = self._failure_provider.get_failure_event_pdf()

		# Logger.write_log(self._name + " failure event via Poisson in " + str(self._failure_event) + " discrete epochs!")

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

	def get_failure_transition_probability(cls):
		return cls._failure_provider.get_failure_transition_probability(cls._discrete_epoch_counter)

	def get_offloading_action_index(cls):
		return cls._offloading_action_index

	def get_server_failure_probability(cls):
		return cls._failure_provider.get_server_failure_probability()

	def get_network_failure_probability(cls):
		return cls._failure_provider.get_network_failure_probability()

	def execute(cls, task):
		if not isinstance(task, Task):
			raise ValueError("Task for execution on offloading site should be Task class instance!")

		offloadable = task.is_offloadable()

		if not offloadable:
			Logger.write_log("Task is not offloadable! (off = " + str(offloadable) + ")")
			return ExecutionErrorCode.EXE_NOK

		if cls._failure_event <= cls._discrete_epoch_counter:
			Logger.write_log("Offloading failure occured on offloading site " + cls._name + "!")
			return ExecutionErrorCode.EXE_NOK
		
		if not task.execute():
			raise ValueError("Task execution operation is not executed properly! Please check the code of execute() method in Task class!")

		print_text = "Task " + task.get_name()
		task_data_storage_consumption = task.get_data_in() + task.get_data_out()
		task_memory_consumption = task.get_memory()

		cls._data_storage_consumption = cls._data_storage_consumption + (task_data_storage_consumption / GIGABYTES)
		cls._memory_consumption = cls._memory_consumption + task_memory_consumption

		# print(task.get_name() + " task current memory consumption: " + str(task_memory_consumption))
		# print(task.get_name() + " task current data storage consumption: " + str(task_data_storage_consumption / GIGABYTES))
		# print(cls._name + " current memory consumption: " + str(cls._memory_consumption) + "Gb (max = " + str(cls._memory) + "Gb)")
		# print(cls._name + " current data storage consumption: " + str(cls._data_storage_consumption) + "Gb (max = " + str(cls._data_storage) + "Gb)\n")
		# Logger.write_log(print_text + "(off = " + str(offloadable) + ") is executed on offloading site " + cls._name + "!")

		return ExecutionErrorCode.EXE_OK

	def print_system_config(cls):
		# Logger.write_log("################### " + ("EDGE SERVER" if cls._offloading_site_code in [OffloadingSiteCode.EDGE_DATABASE_SERVER, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, \
		# 		OffloadingSiteCode.EDGE_REGULAR_SERVER] else "CLOUD DATA CENTER") + " SYSTEM CONFIGURATION ###################")
		# Logger.write_log("Name: " + cls._name)
		# Logger.write_log("CPU: " + str(cls._mips) + " M cycles")
		# Logger.write_log("Memory: " + str(cls._memory) + " Gb")
		# Logger.write_log("Data Storage: " + str(cls._data_storage) + " Gb")
		pass

	# memory and data storage consumption are updated after task execution is done
	def flush_executed_task(cls, task):
		if not isinstance(task, Task):
			Logger.write_log("Task for execution on offloading site should be Task class instance!")
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
			Logger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK

		# check that task resouce requirements fits offloading sites's resource capacity
		if cls._data_storage > (cls._data_storage_consumption + ((task.get_data_in() + task.get_data_out()) / GIGABYTES)) and \
			cls._memory > (cls._memory_consumption + task.get_memory()):
			return ExecutionErrorCode.EXE_OK

		return ExecutionErrorCode.EXE_NOK

	def evaluate_failure_event(cls):
		cls._discrete_epoch_counter = cls._discrete_epoch_counter + 1

		if cls._failure_event < cls._discrete_epoch_counter:
			cls._failure_event = cls._failure_provider.get_failure_event_poisson() - 1
			cls._discrete_epoch_counter = 1

			if cls._failure_event < 0:
				cls._failure_event = 0

			# Logger.write_log(cls._name + " failure event via Poisson in " + str(cls._failure_event) + " discrete epochs!")
			return

		# Logger.write_log("Offloading site " + cls._name + ": " + str(cls._failure_event - cls._discrete_epoch_counter) + " discrete epoch until failure event!")

	def reset_discrete_epoch_counter(cls):
		cls._discrete_epoch_counter = 0

	def __evaluate_params(cls, cpu, memory, data_storage, offloading_site_code):
		if cpu <= 0 or type(cpu) is not int:
			raise ValueError("CPU should be positive integer!")
		if memory <= 0 or type(memory) is not int:
			raise ValueError("Memory should be positive integer!")
		if data_storage <= 0 or type(data_storage) is not int:
			raise ValueError("Input data should be positive integer!")
		if isinstance(offloading_site_code, OffloadingSiteCode):
			raise TypeError("Offloadable site code should be OffloadingSiteCode class object!")