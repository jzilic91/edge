import numpy.random as num
import numpy as np
import re
import matplotlib.pyplot as plt
import datetime
import matplotlib.pyplot as plt

from task import Task
from offloading_site import OffloadingSite
from mobile_app import MobileApplication
from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions, Util
from efpo_ode import EfpoOde
from energy_efficient_ode import EnergyEfficientOde
from mobile_cloud_ode import MobileCloudOde
from local_ode import LocalOde
from logger import Logger

# constants
GIGABYTES = 1000000
PROGRESS_REPORT_INTERVAL = 1

FACEBOOK = "FACEBOOK"
FACERECOGNIZER = "FACERECOGNIZER"
CHESS = "CHESS"

LOCAL_ODE_NAME = "LOCAL"
MC_ODE_NAME = "MC"
EE_ODE_NAME = "EE"
EFPO_ODE_NAME = "EFPO"

class MobileDevice:

	def __init__(self, edge_servers, cloud_dc):
		self.__evaluate_params(edge_servers, cloud_dc)

		self._mips = 1000
		self._memory = 8
		self._data_storage = 16
		
		self._edge_servers = edge_servers
		self._cloud_dc = cloud_dc
		self._mobile_app = None
		self._network = None
		self._ode = None
		self._memory_consumption = 0
		self._data_storage_consumption = 0
		self._name = "MOBILE_DEVICE"
		self._offloading_site_code = OffloadingSiteCode.MOBILE_DEVICE
		self._offloading_action_index = OffloadingActions.MOBILE_DEVICE
		self._discrete_epoch_counter = 0
		self._stats_log = tuple()
		self._sensitivity_analysis = False

	def run(cls, samplings, executions, sensitivity_analysis):
		if cls._mobile_app and cls._ode:

			cls._sensitivity_analysis = sensitivity_analysis
			previous_progress = 0
			current_progress = 0

			print("**************** PROGRESS with " + cls._ode.get_name() + " and " + cls._mobile_app.get_name() + " ****************")
			# Logger.write_log("######################### " + cls._ode.get_name() + " application trace logs #########################")
			print(str(previous_progress) + "% - " + str(datetime.datetime.utcnow()))

			if cls._sensitivity_analysis:
				sensitivity_params = []
				for i in range(0, 11):
					sensitivity_params.append((round(i / 10, 1), round(1 - i / 10, 1)))
			else:
				sensitivity_params =[(0.5, 0.5)]

			print("Sensitivity parameters: " + str(sensitivity_params))

			for sens_params in sensitivity_params:
				cls._ode.save_app_name(cls._mobile_app.get_name())
				cls._ode.set_sensitivity_params(sens_params[0], sens_params[1])

				print("Currently used sensitivity params: " + str(sens_params))

				for i in range(samplings):
					application_time_completion = 0 	# measure total application completion time during execution
					application_energy_consumption = 0  # measure total application energy consumption during execution
					application_overall_rewards = 0 	# measure total application overall rewards during execution

					diff_time = []
					diff_energy = []
					
					for j in range(executions):
						previous_progress = current_progress
						current_progress = round((j + (i * executions)) / (samplings * executions) * 100)

						if current_progress != previous_progress and (current_progress % PROGRESS_REPORT_INTERVAL == 0):
							print(str(current_progress) + "% - " + str(datetime.datetime.utcnow()))

						cls._mobile_app.run()

						ready_tasks = cls._mobile_app.get_ready_tasks()

						single_app_exe_task_comp = 0
						single_app_exe_energy_consum = 0

						while ready_tasks:
							cls._discrete_epoch_counter = cls._discrete_epoch_counter + 1
							# Logger.write_log("********************* " + str(cls._discrete_epoch_counter) + ". DISCRETE EPOCH *********************")

							(task_completion_time, task_energy_consumption, task_overall_reward) = cls._ode.offload(ready_tasks)
							ready_tasks = cls._mobile_app.get_ready_tasks()

							application_time_completion = application_time_completion + task_completion_time
							single_app_exe_task_comp = single_app_exe_task_comp + task_completion_time
							# Logger.write_log("Current application runtime: " + str(application_time_completion) + "s")

							application_energy_consumption = application_energy_consumption + task_energy_consumption
							single_app_exe_energy_consum = single_app_exe_energy_consum + task_energy_consumption
							# Logger.write_log("Current application energy consumption: " + str(application_energy_consumption) + "J")

							application_overall_rewards = application_overall_rewards + task_overall_reward
							# Logger.write_log("Current application overall rewards: " + str(application_overall_rewards))

							cls._mobile_app.print_task_exe_status()

						# deploy facebook mobile applicaiton for further execution
						cls.__reset_application()

						cls._ode.get_statistics().add_time_comp(application_time_completion, j + 1)
						cls._ode.get_statistics().add_energy_eff(application_energy_consumption, j + 1)
						cls._ode.get_statistics().add_reward(application_overall_rewards, j + 1)

						cls._ode.get_statistics().add_time_comp_single_app_exe(single_app_exe_task_comp)
						cls._ode.get_statistics().add_energy_consum_single_app_exe(single_app_exe_energy_consum)

						if len(diff_time) != 0:
							diff_time.append(application_time_completion - np.sum(diff_time))
							diff_energy.append(application_energy_consumption - np.sum(diff_energy))
						else:
							diff_time.append(application_time_completion)
							diff_energy.append(application_energy_consumption)

					cls.__reset_offloading_site_discrete_epoch_counters()

				cls._stats_log = cls._stats_log + (cls._ode, )
				for stats in cls._stats_log:
					print("ODE name: " + stats.get_name())

				print("Time mean: " + str(np.mean(diff_time)))
				print("Time variance: " + str(np.var(diff_time)))

				print("Energy mean: " + str(np.mean(diff_energy)))
				print("Energy variance: " + str(np.var(diff_energy)))

				print("Offloading distribution: " + str(cls._ode.get_statistics().get_offloading_distribution()))
				print("Offloading failure distribution: " + str(cls._ode.get_statistics().get_offloading_failure_frequencies()))

				print("Offloading distribution relative: " + str(cls._ode.get_statistics().get_offloading_distribution_relative()))
				print("Offloading failure frequency relative: " + str(cls._ode.get_statistics().get_offloading_failure_relative()))

				if isinstance(cls._ode, LocalOde):
					cls.deploy_local_ode()
				elif isinstance(cls._ode, EfpoOde):
					cls.deploy_efpo_ode()
				elif isinstance(cls._ode, MobileCloudOde):
					cls.deploy_mobile_cloud_ode()
				elif isinstance(cls._ode, EnergyEfficientOde):
					cls.deploy_energy_efficient_ode()

		else:
			Logger.write_log("You need to DEPLOY mobile application AND offloading decision engine on mobile device before you execute it!")
			Logger.write_log()

	def execute(cls, task):
		print_text = "Task "

		if not isinstance(task, Task):
			Logger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK

		if not task.execute():
			return ExecutionErrorCode.EXE_NOK

		print_text = print_text + task.get_name()
		task_data_storage_consumption = task.get_data_in() + task.get_data_out()
		task_memory_consumption = task.get_memory()

		cls._data_storage_consumption = cls._data_storage_consumption + (task_data_storage_consumption / GIGABYTES)
		cls._memory_consumption = cls._memory_consumption + task_memory_consumption

		# Logger.write_log(print_text + " (off = " + str(task.is_offloadable()) + ") is executed on MOBILE_DEVICE!")
		
		return ExecutionErrorCode.EXE_OK

	def print_system_config(cls):
		Logger.write_log("################### MOBILE DEVICE SYSTEM CONFIGURATION ###################")
		Logger.write_log("CPU: " + str(cls._mips) + " M cycles")
		Logger.write_log("Memory: " + str(cls._memory) + " Gb")
		Logger.write_log("Data Storage: " + str(cls._data_storage) + " Gb")
		Logger.write_log()

	def print_app_config(cls):
		cls._mobile_app.print_entire_config()

	def print_connection_config(cls):
		Logger.write_log("################### MOBILE DEVICE CONNECTION CONFIGURATION ###################")

		for edge_server in cls._edge_servers:
			edge_server.print_system_config()

		cls._cloud_dc.print_system_config()

	def print_ode(cls):
		Logger.write_log("################### OFFLOADING DECISION ENGINE ###################")
		Logger.write_log("Name: " + cls._ode.get_name())
		Logger.write_log()

	def print_network_connections(cls):
		Logger.write_log("################### NETWORK CONNECTIONS ###################")
		for key, values in cls._network.items():
			for value in values:
				Logger.write_log("Source node is (" + key + ") : Destination nodes: (" + str(value[0]) + "), Latency = " + \
				str(value[1]) + "ms, Bandwidth = " + str(value[2]) + "kb/s")

	def print_entire_config(cls):
		cls.print_system_config()
		cls.print_app_config()
		cls.print_connection_config()
		cls.print_ode()
		cls.print_network_connections()

	def plot_statistics(cls):
		for app_name in [FACEBOOK, FACERECOGNIZER, CHESS]:
			for stats in cls._stats_log:
				if stats.get_app_name() == app_name:
					# cls.__plot_time_completion_stats(app_name)
					# cls.__plot_energy_consumption_stats(app_name)
					# cls.__plot_rewards_stats(app_name)
					# cls.__plot_offloading_distribution_stats(app_name)
					# cls.__plot_offloading_failure_frequency_stats(app_name)
					break

		cls.__plot_bar_chart_time_completion()
		cls.__plot_bar_chart_energy_consumption()

		cls._stats_log = tuple()

	def deploy_facebook_application(cls):
		# parameters are (name, millions of instructions, memory (Gb), input data (kb), output data (kb), offloadability)
		facebook_gui = Task("FACEBOOK_GUI", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		get_token = Task("GET_TOKEN", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), True)
		post_request = Task("POST_REQUEST", Util.generate_random_cpu_cycles(), 2, Util.generate_random_input_data(), Util.generate_random_output_data(), True)
		process_response = Task("PROCES_RESPONSE", Util.generate_random_cpu_cycles(), 2, Util.generate_random_input_data(), Util.generate_random_output_data(), True)
		file_upload = Task("FILE_UPLOAD", Util.generate_di_cpu_cycles(), 2, Util.generate_di_input_data(), Util.generate_di_output_data(), False)
		apply_filter = Task("APPLY_FILTER", Util.generate_di_cpu_cycles(), 2, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		facebook_post = Task("FACEBOOK_POST", Util.generate_di_cpu_cycles(), 2, Util.generate_di_input_data(), Util.generate_di_output_data(), False)
		output = Task("OUTPUT", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		# Logger.write_log("############################# APPLICATION DEPLOYMENT #########################")
		# facebook_gui = Task("FACEBOOK_GUI", num.exponential(400), 1, 5, 1, False)
		# get_token = Task("GET_TOKEN", num.exponential(400), 1, 1, 1, True)
		# post_request = Task("POST_REQUEST", num.exponential(550), 2, 1, 5, True)
		# process_response = Task("PROCES_RESPONSE", num.exponential(550), 2, 1, 1, True)
		# file_upload = Task("FILE_UPLOAD", num.exponential(550), 2, num.exponential(500), num.exponential(500), False)
		# apply_filter = Task("APPLY_FILTER", num.exponential(800), 2, num.exponential(500), num.exponential(500), True)
		# facebook_post = Task("FACEBOOK_POST", num.exponential(600), 2, num.exponential(500), 5, False)
		# output = Task("OUTPUT", num.exponential(600), 1, 5, 5, False)

		facebook_delay_dict = {
			facebook_gui: [(get_token, num.randint(2, 10)), (post_request, num.randint(2, 10))],
			get_token: [(post_request, num.randint(2, 10))],
			post_request: [(process_response, num.randint(2, 10))],
			process_response: [(file_upload, num.randint(2, 10))],
			file_upload: [(apply_filter, num.randint(2, 10))],
			apply_filter: [(facebook_post, num.randint(2, 10))],
			facebook_post: [(output, num.randint(2, 10))],
			output: []
		}

		cls._mobile_app = MobileApplication(FACEBOOK, facebook_delay_dict)

	def deploy_chess_application(cls):
		gui = Task("GUI", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		update_chess = Task("UPDATE_CHESS", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), True)
		compute_move = Task("COMPUTE_MOVE", Util.generate_ci_cpu_cycles(), 2, Util.generate_ci_input_data(), Util.generate_ci_output_data(), True)
		output = Task("OUTPUT", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)

		chess_delay_dict = {
			gui: [(update_chess, num.randint(2, 10))],
			update_chess: [(compute_move, num.randint(2, 10))],
			compute_move: [(output, num.randint(2, 10))],
			output: []
		}

		cls._mobile_app = MobileApplication(CHESS, chess_delay_dict)

	def deploy_facerecognizer_application(cls):
		gui = Task("GUI", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), False)
		find_match = Task("FIND_MATCH", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		init = Task("INIT", Util.generate_di_cpu_cycles(), 2, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		detect_face = Task("DETECT_FACE", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		output = Task("OUTPUT", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), False)

		facerecognizer_delay_dict = {
			gui: [(find_match, num.randint(2, 10))],
			find_match: [(init, num.randint(2, 10)), (detect_face, num.randint(2, 10))],
			init: [(detect_face, num.randint(2, 10))],
			detect_face: [(output, num.randint(2, 10))],
			output: []
		}

		cls._mobile_app = MobileApplication(FACERECOGNIZER, facerecognizer_delay_dict)

	def deploy_network_model(cls):
		cloud_dc = cls.__get_cloud_dc_server()
		edge_db_server = cls.__get_edge_database_server('A')
		edge_comp_server = cls.__get_edge_computational_server('A')
		edge_reg_server = cls.__get_edge_regular_server('A')
		mobile_device = cls

		# network bandwidth is hardcoded but network latency contains randomness feature in the distribuiton for every method invocation
		# thus network latency method will be invoked only once for bidirectional connections to gain symmetric latency distribuiton 

		# Cloud DC <-> Edge database server
		cloud_dc__edge_db_server__net_lat = Util.get_network_latency(cloud_dc, edge_db_server)

		# Cloud DC <-> Edge computational intensive server
		cloud_dc__edge_comp_server__net_lat = Util.get_network_latency(cloud_dc, edge_comp_server)

		# Cloud DC <-> Edge regular server
		cloud_dc__edge_reg_server__net_lat = Util.get_network_latency(cloud_dc, edge_reg_server)

		# Cloud DC <-> mobile device
		cloud_dc__mobile_device__net_lat = Util.get_network_latency(cloud_dc, mobile_device)

		# Edge database server <-> Edge computational intensive server
		edge_db_server__edge_comp_server__net_lat = Util.get_network_latency(edge_db_server, edge_comp_server)

		# Edge database server <-> Edge regular server
		edge_db_server__edge_reg_server__net_lat = Util.get_network_latency(edge_db_server, edge_reg_server)

		# Edge database server <-> mobile device
		edge_db_server__mobile_device__net_lat = Util.get_network_latency(edge_db_server, mobile_device)

		# Edge computational intensive server <-> Edge regular server
		edge_comp_server__edge_reg_server__net_lat = Util.get_network_latency(edge_comp_server, edge_reg_server)

		# Edge computational intensive server <-> mobile device
		edge_comp_server__mobile_device__net_lat = Util.get_network_latency(edge_comp_server, mobile_device)

		# Edge regular server <-> mobile device
		edge_reg_server__mobild_device__net_lat = Util.get_network_latency(edge_reg_server, mobile_device)


		cls._network = {
			cloud_dc.get_name(): [(edge_db_server.get_name(), cloud_dc__edge_db_server__net_lat, Util.get_network_bandwidth(cloud_dc, edge_db_server)),
				(edge_comp_server.get_name(), cloud_dc__edge_comp_server__net_lat, Util.get_network_bandwidth(cloud_dc, edge_comp_server)),
				(edge_reg_server.get_name(), cloud_dc__edge_reg_server__net_lat, Util.get_network_bandwidth(cloud_dc, edge_reg_server)),
				(mobile_device.get_name(), cloud_dc__mobile_device__net_lat, Util.get_network_bandwidth(cloud_dc, mobile_device))],
			edge_db_server.get_name(): [(cloud_dc.get_name(), cloud_dc__edge_db_server__net_lat, Util.get_network_bandwidth(edge_db_server, cloud_dc)),
				(edge_comp_server.get_name(), edge_db_server__edge_comp_server__net_lat, Util.get_network_bandwidth(edge_db_server, edge_comp_server)),
				(edge_reg_server.get_name(), edge_db_server__edge_reg_server__net_lat, Util.get_network_bandwidth(edge_db_server, edge_reg_server)),
				(mobile_device.get_name(), edge_db_server__mobile_device__net_lat, Util.get_network_bandwidth(edge_db_server, mobile_device))],
			edge_comp_server.get_name(): [(cloud_dc.get_name(), cloud_dc__edge_comp_server__net_lat, Util.get_network_bandwidth(edge_comp_server, cloud_dc)),
				(edge_db_server.get_name(), edge_db_server__edge_comp_server__net_lat, Util.get_network_bandwidth(edge_comp_server, edge_db_server)),
				(edge_reg_server.get_name(), edge_comp_server__edge_reg_server__net_lat, Util.get_network_bandwidth(edge_comp_server, edge_reg_server)),
				(mobile_device.get_name(), edge_comp_server__mobile_device__net_lat, Util.get_network_bandwidth(edge_comp_server, mobile_device))],
			edge_reg_server.get_name(): [(cloud_dc.get_name(), cloud_dc__edge_reg_server__net_lat, Util.get_network_bandwidth(edge_reg_server, cloud_dc)),
				(edge_db_server.get_name(), edge_db_server__edge_reg_server__net_lat, Util.get_network_bandwidth(edge_reg_server, edge_db_server)),
				(edge_comp_server.get_name(), edge_comp_server__edge_reg_server__net_lat, Util.get_network_bandwidth(edge_reg_server, edge_comp_server)),
				(mobile_device.get_name(), edge_reg_server__mobild_device__net_lat, Util.get_network_bandwidth(edge_reg_server, mobile_device))],
			mobile_device.get_name(): [(cloud_dc.get_name(), cloud_dc__mobile_device__net_lat, Util.get_network_bandwidth(mobile_device, cloud_dc)),
				(edge_db_server.get_name(), edge_db_server__mobile_device__net_lat, Util.get_network_bandwidth(mobile_device, edge_db_server)),
				(edge_comp_server.get_name(), edge_comp_server__mobile_device__net_lat, Util.get_network_bandwidth(mobile_device, edge_comp_server)),
				(edge_reg_server.get_name(), edge_reg_server__mobild_device__net_lat, Util.get_network_bandwidth(mobile_device, edge_reg_server))]
		}

	def deploy_efpo_ode(cls):
		cls._ode = EfpoOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, EFPO_ODE_NAME)

	def deploy_energy_efficient_ode(cls):
		cls._ode = EnergyEfficientOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, EE_ODE_NAME)

	def deploy_local_ode(cls):
		cls._ode = LocalOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, LOCAL_ODE_NAME)

	def deploy_mobile_cloud_ode(cls):
		cls._ode = MobileCloudOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, MC_ODE_NAME)

	# get name
	def get_name(cls):
		return cls._name

	# get CPU processing power expressed in millions of instructions per second
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

	# get state transition cost
	def get_transition_cost(cls):
		return cls._transition_cost

	def get_failure_transition_probability(cls):
		return 0.0

	def get_offloading_action_index(cls):
		return cls._offloading_action_index

	def get_offloading_site_code(cls):
		return cls._offloading_site_code

	def get_server_failure_probability(cls):
		return 0.0

	def get_network_failure_probability(cls):
		return 0.0

	# set index that is used for accessing elements of P and R matrix that corresponds to offloading site
	def set_index(cls, index):
		cls._index = int(index)

	# memory and data storage consumption are updated after task execution is done
	def flush_executed_task(cls, task):
		if not isinstance(task, Task):
			Logger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK
			
		cls._memory_consumption = cls._memory_consumption - task.get_memory()
		cls._data_storage_consumption = cls._data_storage_consumption - ((task.get_data_in() + task.get_data_out()) / GIGABYTES)

		if cls._memory_consumption < 0 or cls._data_storage_consumption < 0:
			raise ValueError("Memory consumption: " + str(cls._memory_consumption) + "Gb, data storage consumption: " + str(cls._data_storage_consumption) + \
				"Gb, both should be positive! Node: " + cls._name + ", task: " + task.get_name())

	# check the validity of task deployment on mobile device regarding to resource capacity (memory and data storage)
	def check_validity_of_deployment(cls, task):
		if not isinstance(task, Task):
			Logger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK

		# check that task resouce requirements fits mobile device's resource capacity
		if cls._data_storage > (cls._data_storage_consumption + ((task.get_data_in() + task.get_data_out())) / GIGABYTES) and \
			cls._memory > (cls._memory_consumption + task.get_memory()):
			return ExecutionErrorCode.EXE_OK
		
		return ExecutionErrorCode.EXE_NOK

	def __reset_application(cls):
		if cls._mobile_app.get_name() == FACEBOOK:
			cls.deploy_facebook_application()
		elif cls._mobile_app.get_name() == CHESS:
			cls.deploy_chess_application()
		elif cls._mobile_app.get_name() == FACERECOGNIZER:
			cls.deploy_facerecognizer_application()

	def __plot_time_completion_stats(cls, app_name):
		for stats in cls._stats_log:
			if stats.get_app_name() == app_name:
				plt.plot(stats.get_statistics().get_time_completion_mean().keys(), stats.get_statistics().get_time_completion_mean().values(), label = stats.get_name())

		plt.title("Time Completion Graph with mobile app " + app_name)
		plt.xlabel("Application executions")
		plt.ylabel("Time completion")
		plt.legend()
		plt.show()
		
	def __plot_energy_consumption_stats(cls, app_name):
		for stats in cls._stats_log:
			if stats.get_app_name() == app_name:
				plt.plot(stats.get_statistics().get_energy_consumption_mean().keys(), stats.get_statistics().get_energy_consumption_mean().values(), label = stats.get_name())

		plt.title("Energy Consumption Graph with mobile app " + app_name)
		plt.xlabel("Application executions")
		plt.ylabel("Energy Consumption")
		plt.legend()
		plt.show()
	
	def __plot_rewards_stats(cls, app_name):
		for stats in cls._stats_log:
			if stats.get_app_name() == app_name:
				plt.plot(stats.get_statistics().get_rewards_mean().keys(), stats.get_statistics().get_rewards_mean().values(), label = stats.get_name())

		plt.title("Rewards Graph regarding with mobile app " + app_name)
		plt.xlabel("Application executions")
		plt.ylabel("Rewards")
		plt.legend()
		plt.show()

	def __plot_offloading_distribution_stats(cls, app_name):
		hist_data = ()
		labels = []
		for stats in cls._stats_log:
			if stats.get_app_name() == app_name:
				offload_dist_dict = stats.get_statistics().get_offloading_distribution()
				bin_data = []

				for key, value in offload_dist_dict.items():
					tmp_list = value * [key]
					bin_data += tmp_list

				labels.append(stats.get_name())
				hist_data = hist_data + (bin_data,)

		plt.hist(hist_data, len(cls._edge_servers) + 2, histtype = 'bar', stacked = False, fill = True, label = labels, alpha = 0.8, edgecolor = "k")

		plt.title('Offloading distribution with mobile app ' + app_name)
		plt.xlabel('Offloading sites')
		plt.ylabel('Frequency')
		plt.legend();
		plt.show()

	def __plot_offloading_failure_frequency_stats(cls, app_name):
		hist_data = ()
		labels = []
		for stats in cls._stats_log:
			if stats.get_app_name() == app_name:
				offload_fail_freq_dict = stats.get_statistics().get_offloading_failure_frequencies()
				bin_data = []

				for key, value in offload_fail_freq_dict.items():
					tmp_list = value * [key]
					bin_data += tmp_list

				labels.append(stats.get_name())
				hist_data = hist_data + (bin_data,)

		plt.hist(hist_data, len(cls._edge_servers) + 2, histtype = 'bar', stacked = False, fill = True, label = labels, alpha = 0.8, edgecolor = "k")

		plt.title('Offloading failure distribution with mobile app ' + app_name)
		plt.xlabel('Offloading sites')
		plt.ylabel('Frequency')
		plt.legend()
		plt.show()

	def __plot_bar_chart_time_completion(cls):
		applications = list()

		for stats in cls._stats_log:
			if not (stats.get_app_name() in applications):
				applications.append(stats.get_app_name())

		local_x_mean = list()
		local_x_std = list()

		mc_x_mean = list()
		mc_x_std = list()

		ee_x_mean = list()
		ee_x_std = list()

		efpo_x_mean = list()
		efpo_x_std = list()

		for stats in cls._stats_log:
			for app in applications:
				if stats.get_app_name() == app and stats.get_name() == LOCAL_ODE_NAME:
					local_x_mean.append(stats.get_statistics().get_single_app_time_comp_mean())
					local_x_std.append(stats.get_statistics().get_single_app_time_comp_std())

				elif stats.get_app_name() == app and stats.get_name() == MC_ODE_NAME:
					mc_x_mean.append(stats.get_statistics().get_single_app_time_comp_mean())
					mc_x_std.append(stats.get_statistics().get_single_app_time_comp_std())

				elif stats.get_app_name() == app and stats.get_name() == EE_ODE_NAME:
					ee_x_mean.append(stats.get_statistics().get_single_app_time_comp_mean())
					ee_x_std.append(stats.get_statistics().get_single_app_time_comp_std())

				elif stats.get_app_name() == app and stats.get_name() == EFPO_ODE_NAME:
					efpo_x_mean.append(stats.get_statistics().get_single_app_time_comp_mean())
					efpo_x_std.append(stats.get_statistics().get_single_app_time_comp_std())

		x = np.arange(len(applications))

		ax = plt.subplot(111)
		ax.bar(x - 0.2, local_x_mean, yerr = local_x_std, width = 0.1, color = 'b', align = 'center', label = 'Local')
		ax.bar(x - 0.1, mc_x_mean, yerr = mc_x_std , width = 0.1, color = 'g', align = 'center', label = 'Mobile Cloud')
		ax.bar(x, ee_x_mean, yerr = ee_x_std, width = 0.1, color = 'r', align = 'center', label = 'Energy Efficient')
		ax.bar(x + 0.1, efpo_x_mean, yerr = efpo_x_std, width = 0.1, color = 'm', align = 'center', label = 'EFPO')

		plt.xlabel('Mobile applications')
		plt.ylabel('Time completion (seconds)')
		plt.title('Average time completion of single mobile execution')
		plt.xticks(x, applications, fontsize = 10)
		plt.legend()
		plt.show()

	def __plot_bar_chart_energy_consumption(cls):
		applications = list()

		for stats in cls._stats_log:
			if not (stats.get_app_name() in applications):
				applications.append(stats.get_app_name())

		local_x_mean = list()
		local_x_std = list()

		mc_x_mean = list()
		mc_x_std = list()

		ee_x_mean = list()
		ee_x_std = list()

		efpo_x_mean = list()
		efpo_x_std = list()

		for stats in cls._stats_log:
			for app in applications:
				if stats.get_app_name() == app and stats.get_name() == LOCAL_ODE_NAME:
					local_x_mean.append(stats.get_statistics().get_single_app_app_energy_consum_mean())
					local_x_std.append(stats.get_statistics().get_single_app_app_energy_consum_std())

				elif stats.get_app_name() == app and stats.get_name() == MC_ODE_NAME:
					mc_x_mean.append(stats.get_statistics().get_single_app_app_energy_consum_mean())
					mc_x_std.append(stats.get_statistics().get_single_app_app_energy_consum_std())

				elif stats.get_app_name() == app and stats.get_name() == EE_ODE_NAME:
					ee_x_mean.append(stats.get_statistics().get_single_app_app_energy_consum_mean())
					ee_x_std.append(stats.get_statistics().get_single_app_app_energy_consum_std())

				elif stats.get_app_name() == app and stats.get_name() == EFPO_ODE_NAME:
					efpo_x_mean.append(stats.get_statistics().get_single_app_app_energy_consum_mean())
					efpo_x_std.append(stats.get_statistics().get_single_app_app_energy_consum_std())

		x = np.arange(len(applications))

		ax = plt.subplot(111)
		ax.bar(x - 0.2, local_x_mean, yerr = local_x_std, width = 0.1, color = 'b', align = 'center', label = 'Local')
		ax.bar(x - 0.1, mc_x_mean, yerr = mc_x_std, width = 0.1, color = 'g', align = 'center', label = 'Mobile Cloud')
		ax.bar(x, ee_x_mean, yerr = ee_x_std, width = 0.1, color = 'r', align = 'center', label = 'Energy Efficient')
		ax.bar(x + 0.1, efpo_x_mean, yerr = efpo_x_std, width = 0.1, color = 'm', align = 'center', label = 'EFPO')

		plt.xlabel('Mobile applications')
		plt.ylabel('Energy consumption (joules)')
		plt.title('Average energy consumption of single mobile execution')
		plt.xticks(x, applications, fontsize = 10)
		plt.legend()
		plt.show()

	def __reset_offloading_site_discrete_epoch_counters(cls):
		for edge_server in cls._edge_servers:
			edge_server.reset_discrete_epoch_counter()

		cls._cloud_dc.reset_discrete_epoch_counter()

		cls.__reset_discrete_epoch_counters()

	def __reset_discrete_epoch_counters(cls):
		cls._discrete_epoch_counter = 0

	def __get_edge_database_server(cls, name):
		for edge_server in cls._edge_servers:
			if re.match(r'EDGE_DATABASE_SERVER_' + re.escape(name), edge_server.get_name()):
				return edge_server

		raise ValueError("Edge database server with name " + name + " is not found!")

	def __get_edge_computational_server(cls, name):
		for edge_server in cls._edge_servers:
			if re.match(r'EDGE_COMPUTATIONAL_SERVER_' + re.escape(name), edge_server.get_name()):
				return edge_server

		raise ValueError("Edge computational server with name " + name + " is not found!")

	def __get_edge_regular_server(cls, name):
		for edge_server in cls._edge_servers:
			if re.match(r'EDGE_REGULAR_SERVER_' + re.escape(name), edge_server.get_name()):
				return edge_server

		raise ValueError("Edge regular server with name " + name + " is not found!")

	def __get_cloud_dc_server(cls):
		return cls._cloud_dc

	def __evaluate_params(cls, edge_servers, cloud_dc):
		if type(edge_servers) is not tuple:
			raise TypeError("Edge servers should be a tuple!")
		if not edge_servers:
			raise ValueError("Edge servers should not be an empty tuple!")

		for edge in edge_servers:
			if not isinstance(edge, OffloadingSite):
				raise TypeError("Edge server should be an OffloadingSite class instance!")
			if not edge.get_offloading_site_code() in [OffloadingSiteCode.EDGE_DATABASE_SERVER, OffloadingSiteCode.EDGE_COMPUTATIONAL_INTENSIVE_SERVER, \
				OffloadingSiteCode.EDGE_REGULAR_SERVER] :
				raise ValueError("Edge server is not configured as edge server according to offloading site code!")

		if not isinstance(cloud_dc, OffloadingSite):
			raise TypeError("Edge server should be an OffloadingSite class instance!")
		if cloud_dc.get_offloading_site_code() != OffloadingSiteCode.CLOUD_DATA_CENTER:
			raise ValueError("Cloud data center is not configured as cloud data center according to offloading site code!")

		# evaluate edge servers naming, every edge server should have distinct unique name
		for i in range(0, len(edge_servers)):
			for j in range(0, len(edge_servers)):
				if i == j:
					continue

				if edge_servers[i].get_name() == edge_servers[j].get_name():
					for edge in edge_servers:
						Logger.write_log(edge.get_name())
					raise ValueError("Edge servers should have distinct unique names!")