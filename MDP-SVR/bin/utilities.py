import random
import numpy

class NodeCategory:
	ER_DATA, EC_DATA, ED_DATA, CD_DATA, NET_DATA = ("EDGE_REG_DATA", "EDGE_COMP_DATA", "EDGE_DATA_DATA", \
		"CLOUD_DATA", "NETWORK_DATA")


class TrainingDataSize:
	SIZE_526 = 526


class DatasetType:
	LANL_DATASET, PNNL_DATASET, LDNS_DATASET = ("LANL", "PNNL", "LDNS")


class PredictionMode:
	TEST_PREDICTION_MODE, TRAINING_PREDICTION_MODE = ("test", "training")


class SlidingWindowSize:
	SIZE_1, SIZE_2, SIZE_5, SIZE_10, SIZE_15, SIZE_20, SIZE_30, SIZE_40, SIZE_50, SIZE_70, SIZE_100 = (1, 2, 5, 10, 15, 20, 30, 40, 50, 70, 100)


class ExecutionMode:
	NORMAL_MODE, EXHAUSTIVE_MODE = (1, 2)


class DataType:
	TIME_BETWEEN_FAILURE, FAILURE_RATE, AVAILABILITY = ('TBF', 'FR', 'AVAIL')


class Uptime:
	DAY_IN_MINUTES = 1440


class WorkingCondition:
	SLIDING_WINDOW, TRAINING_TEST_SEPARATION = ('SLIDING_WINDOW', 'TRAINING_TEST_SEPARATION')


class PredictionSample:
	MTBF, SVR = ('MTBF', 'SVR')


class ExecutionErrorCode:
	EXE_NOK, EXE_OK = range(2)


class OffloadingSiteCode:
	MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER = range(5)


class OffloadingActions:
	NUMBER_OF_OFFLOADING_ACTIONS = 5
	MOBILE_DEVICE, EDGE_DATABASE_SERVER, EDGE_COMPUTATIONAL_INTENSIVE_SERVER, EDGE_REGULAR_SERVER, CLOUD_DATA_CENTER = \
		range(NUMBER_OF_OFFLOADING_ACTIONS)


class FailureEventMode:
	POISSON_FAILURE, TEST_DATASET_FAILURE = range(2)


class OdeType:
	LOCAL, MOBILE_CLOUD, ENERGY_EFFICIENT, EFPO, MDP_SVR = ('LOCAL', 'MOBILE_CLOUD', 'ENERGY_EFFICIENT',\
		'EFPO', 'MDP_SVR')


class Util(object):

	#######################################################################
	###################### TASK SIMULATION PARAMETERS #####################
	#######################################################################

	########################### CPU (M cycles) ############################

	@classmethod
	def generate_di_cpu_cycles(cls):
		return random.randint(100, 200)

	@classmethod
	def generate_ci_cpu_cycles(cls):
		return random.randint(550, 650)

	@classmethod
	def generate_random_cpu_cycles(cls):
		return random.randint(100, 200)

	########################## Input data (kb) ############################

	@classmethod
	def generate_di_input_data(cls):
		return random.randint(4 * 25, 4 * 30)

	@classmethod
	def generate_random_input_data(cls):
		return random.randint(4, 8)

	@classmethod
	def generate_ci_input_data(cls):
		return random.randint(4, 8)

	########################## Output data (kb) ############################

	@classmethod
	def generate_di_output_data(cls):
		return random.randint(4 * 15, 4 * 20)

	@classmethod
	def generate_random_output_data(cls):
		return random.randint(4, 8)

	@classmethod
	def generate_ci_output_data(cls):
		return random.randint(4, 8)

	#######################################################################
	############# COMPUTATIONAL NODES SIMULATION PARAMETERS ###############
	#######################################################################

	############################## CPU (GHz) ##############################

	@classmethod
	def get_mobile_device_cpu(cls):
		return 0.5

	@classmethod
	def get_edge_database_server_cpu(cls):
		return 2

	@classmethod
	def get_edge_regular_server_cpu(cls):
		return 2

	@classmethod
	def get_edge_computational_intensive_cpu(cls):
		return 3

	@classmethod
	def get_cloud_dc_cpu(cls):
		return 5

	########################## RAM memory (Gb) ############################

	@classmethod
	def get_mobile_device_ram_memory(cls):
		return 4

	@classmethod
	def get_edge_database_server_ram_memory(cls):
		return 8

	@classmethod
	def get_edge_regular_server_ram_memory(cls):
		return 8

	@classmethod
	def get_edge_computational_intensive_ram_memory(cls):
		return 8

	@classmethod
	def get_cloud_dc_ram_memory(cls):
		return 128

	######################## Data storage (Gb) ##########################

	@classmethod
	def get_mobile_device_data_storage(cls):
		return 16

	@classmethod
	def get_edge_database_server_data_storage(cls):
		return 500

	@classmethod
	def get_edge_regular_server_data_storage(cls):
		return 250

	@classmethod
	def get_edge_computational_intensive_data_storage(cls):
		return 250

	@classmethod
	def get_cloud_dc_data_storage(cls):
		return 1000

	#######################################################################
	############ NETWORK INFRASTRUCTURE SIMULATION PARAMETERS #############
	#######################################################################
	
	@classmethod
	def get_network_latency(cls, src_node, dst_node):
		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return round((15 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return round((15 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return round((15 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return round((54 + numpy.random.normal(200, 33.5)), 2)




		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return round((15 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 10

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 10

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 15




		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return round((15 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 10 

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 10 

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 15




		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return round((15 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 10

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 10

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 15




		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return round((54 + numpy.random.normal(200, 33.5)), 2)

		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 15

		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 15

		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 15

	@classmethod
	def get_network_bandwidth(cls, src_node, dst_node):
		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 123000

		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 12500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 12500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 2500




		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return 123000

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 123000

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 123000

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 2500




		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return 12500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 123000 

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 12500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 687.5




		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return 12500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 123000

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 12500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE:
			return 687.5



		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.CLOUD_DATA_CENTER:
			return 2500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_DATABASE_SERVER:
			return 2500

		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER:
			return 687.5

		if src_node.get_offloading_site_code() == OffloadingSiteCode.MOBILE_DEVICE and \
			dst_node.get_offloading_site_code() == OffloadingSiteCode.EDGE_REGULAR_SERVER:
			return 687.5