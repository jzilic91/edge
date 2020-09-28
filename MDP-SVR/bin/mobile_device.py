import numpy.random as num
import numpy as np
import re
import matplotlib.pyplot as plt
import datetime
from inspect import currentframe, getframeinfo

from task import Task
from offloading_site import OffloadingSite
from mobile_app import MobileApplication
from utilities import OffloadingSiteCode, ExecutionErrorCode, OffloadingActions, Util, OdeType
from efpo_ode import EfpoOde
from mdp_svr_ode import MdpSvrOde
from energy_efficient_ode import EnergyEfficientOde
from mobile_cloud_ode import MobileCloudOde
from local_ode import LocalOde
from mdp_logger import MdpLogger

# constants
GIGABYTES = 1000000
PROGRESS_REPORT_INTERVAL = 1

FACEBOOK = "FACEBOOK"
FACERECOGNIZER = "FACERECOGNIZER"
CHESS = "CHESS"
ANTIVIRUS = "ANTIVIRUS"
GPS_NAVIGATOR = "GPS_NAVIGATOR"

LOCAL_ODE_NAME = "LOCAL"
MC_ODE_NAME = "MC"
EE_ODE_NAME = "EE"
EFPO_ODE_NAME = "EFPO"
MDP_SVR_ODE_NAME = "MDP_SVR"

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


	def run(cls, samplings, executions, mixed_mode, sensitivity_analysis):
		if cls._ode:

			cls._sensitivity_analysis = sensitivity_analysis
			previous_progress = 0
			current_progress = 0

			if cls._sensitivity_analysis:
				sensitivity_params = []
				for i in range(0, 11):
					sensitivity_params.append((round(i / 10, 1), round(1 - i / 10, 1)))
			else:
				sensitivity_params = [(0.5, 0.5)]

			print("Sensitivity parameters: " + str(sensitivity_params) + '\n')

			print("**************** PROGRESS with " + cls._ode.get_name() + "****************")
			# Logger.write_log("######################### " + cls._ode.get_name() + " application trace logs #########################")
			print(str(previous_progress) + "% - " + str(datetime.datetime.utcnow()))

			for sens_params in sensitivity_params:
				cls._ode.set_sensitivity_params(sens_params[0], sens_params[1])

				# diff_time = []
				# diff_energy = []
				# diff_fail_time = []
				# diff_fail_energy = []

				applications = ['ANTIVIRUS', 'GPS_NAVIGATOR', 'FACERECOGNIZER', 'FACEBOOK', 'CHESS']

				for i in range(samplings):
					# print("Currently used sensitivity params: " + str(sens_params))
					application_time_completion = 0 	# measure total application completion time during execution
					application_energy_consumption = 0  # measure total application energy consumption during execution
					application_overall_rewards = 0 	# measure total application overall rewards during execution
					application_fail_time_completion = 0
					application_fail_energy_consumption = 0
					application_failures = 0

					# reset test data after each simulation sampling to start from the beginning
					for edge in cls._edge_servers:
						edge.reset_test_data()

					cls._cloud_dc.reset_test_data()

					# simulate application executions					
					for j in range(executions):
						if mixed_mode:
							choice = np.random.choice(5, 1, p = [0.05, 0.3, 0.1, 0.45, 0.1])[0]

							if choice == 0:
								cls.deploy_antivirus_application()

							elif choice == 1:
								cls.deploy_gps_navigator_application()

							elif choice == 2:
								cls.deploy_facerecognizer_application()

							elif choice == 3:
								cls.deploy_facebook_application()

							elif choice == 4:
								cls.deploy_chess_application()

						cls._ode.save_app_name(cls._mobile_app.get_name())

						previous_progress = current_progress
						current_progress = round((j + (i * executions)) / (samplings * executions) * 100)

						if current_progress != previous_progress and (current_progress % PROGRESS_REPORT_INTERVAL == 0):
							print(str(current_progress) + "% - " + str(datetime.datetime.utcnow()))

						cls._mobile_app.run()

						ready_tasks = cls._mobile_app.get_ready_tasks()

						single_app_exe_task_comp = 0
						single_app_exe_energy_consum = 0

						while ready_tasks:
							# MdpLogger.write_log('##############################################################')
							# MdpLogger.write_log('##################### RESOURCE CONSUMPTION ###################')
							# MdpLogger.write_log('##############################################################\n')
							cls._discrete_epoch_counter = cls._discrete_epoch_counter + 1
							#MdpLogger.write_log("********************* " + str(cls._discrete_epoch_counter) + ". DISCRETE EPOCH *********************")

							(task_completion_time, task_energy_consumption, task_overall_reward, task_failure_time_cost,\
								task_failure_energy_cost, task_failures) = cls._ode.offload(ready_tasks)
							ready_tasks = cls._mobile_app.get_ready_tasks()

							application_time_completion = round(application_time_completion + task_completion_time, 3)
							application_fail_time_completion += round(task_failure_time_cost, 3)
							single_app_exe_task_comp = round(single_app_exe_task_comp + task_completion_time, 3)
							# MdpLogger.write_log('\nFilename: ' + getframeinfo(currentframe()).filename + ', Line = ' + str(getframeinfo(currentframe()).lineno))
							# MdpLogger.write_log("Current application runtime: " + str(application_time_completion) + " s")

							application_energy_consumption = round(application_energy_consumption + task_energy_consumption, 3)
							application_fail_energy_consumption = round(application_fail_energy_consumption + task_failure_energy_cost, 3)
							single_app_exe_energy_consum = round(single_app_exe_energy_consum + task_energy_consumption, 3)
							# MdpLogger.write_log("Current application energy consumption: " + str(application_energy_consumption) + " J")

							application_failures += task_failures

							application_overall_rewards = round(application_overall_rewards + task_overall_reward, 3)
							# MdpLogger.write_log("Current application overall rewards: " + str(application_overall_rewards) + '\n')

							# MdpLogger.write_log('Task application runtime: ' + str(task_completion_time) + 's')
							# MdpLogger.write_log('Task energy consumption: ' + str(task_energy_consumption) + 'J')
							# MdpLogger.write_log('Task rewards: ' + str(task_overall_reward))
							# MdpLogger.write_log('Task failure time cost:' + str(task_failure_time_cost) + 's')

							cls._mobile_app.print_task_exe_status()

						# deploy facebook mobile application for further execution
						cls.__reset_application()

						cls._ode.get_statistics().add_time_comp_single_app_exe(single_app_exe_task_comp)
						cls._ode.get_statistics().add_energy_consum_single_app_exe(single_app_exe_energy_consum)

						# if len(diff_time) != 0:
						# 	diff_time.append(application_time_completion - np.sum(diff_time))
						# 	diff_energy.append(application_energy_consumption - np.sum(diff_energy))
						# 	diff_fail_time.append(application_fail_time_completion - np.sum(diff_fail_time))
						# 	diff_fail_energy.append(application_fail_energy_consumption - np.sum(diff_fail_energy))
						# else:
						# 	diff_time.append(application_time_completion)
						# 	diff_energy.append(application_energy_consumption)
						# 	diff_fail_time.append(application_fail_time_completion)
						# 	diff_fail_energy.append(application_fail_energy_consumption)
					cls._ode.get_statistics().add_time_comp(application_time_completion)
					cls._ode.get_statistics().add_energy_eff(application_energy_consumption)
					cls._ode.get_statistics().add_reward(application_overall_rewards)
					cls._ode.get_statistics().add_failure_rate(application_failures)

					cls.__reset_offloading_site_discrete_epoch_counters()

				cls._stats_log = cls._stats_log + (cls._ode, )
				# for stats in cls._stats_log:
				# 	("ODE name: " + stats.get_name())
				if mixed_mode:
					app_name = 'MIXED MODE'

				else:
					app_name = cls._mobile_app.get_name()

				MdpLogger.write_log('\nFilename: ' + getframeinfo(currentframe()).filename + ', Line = ' + str(getframeinfo(currentframe()).lineno))
				MdpLogger.write_log('##############################################################')
				MdpLogger.write_log('################## ' + cls._ode.get_name() + ' OFFLOADING RESULT SUMMARY #################')
				MdpLogger.write_log('################## ' + app_name + ' ###########################################')
				MdpLogger.write_log('##############################################################\n')

				MdpLogger.write_log("Time mean: " + str(cls._ode.get_statistics().get_time_completion_mean()) + ' s')
				MdpLogger.write_log("Time variance: " + str(cls._ode.get_statistics().get_time_completion_var()) + ' s\n')

				# MdpLogger.write_log("Failure time cost mean: " + str(np.mean(diff_fail_time)) + ' s')
				# MdpLogger.write_log("Failure time cost variance: " + str(np.var(diff_fail_time)) + ' s\n')

				MdpLogger.write_log("Energy mean: " + str(cls._ode.get_statistics().get_energy_consumption_mean()) + ' J')
				MdpLogger.write_log("Energy variance: " + str(cls._ode.get_statistics().get_energy_consumption_var()) + ' J\n')

				MdpLogger.write_log("Offloading failure rate mean: " + str(cls._ode.get_statistics().get_failure_rates_mean()) + ' failures')
				MdpLogger.write_log("Offloading failure rate variance: " + str(cls._ode.get_statistics().get_failure_rates_var()) + ' failures\n')

				# MdpLogger.write_log("Failure energy cost mean: " + str(np.mean(diff_fail_energy)) + ' J')
				# MdpLogger.write_log("Failure energy cost variance: " + str(np.var(diff_fail_energy)) + ' J\n')

				# MdpLogger.write_log("Mobile application runtime: " + str(application_time_completion) + ' s')
				# MdpLogger.write_log("Mobile device energy consumption: " + str(application_energy_consumption) + ' J\n')

				MdpLogger.write_log("Offloading distribution: " + \
					str(cls._ode.get_statistics().get_offloading_distribution()))
				MdpLogger.write_log("Offloading distribution relative: " + \
					str(cls._ode.get_statistics().get_offloading_distribution_relative()))
				MdpLogger.write_log("Num of offloadings: " + \
					str(cls._ode.get_statistics().get_num_of_offloadings()) + '\n')

				text = ""
				all_failures = 0
				for edge in cls._edge_servers:
					all_failures += edge.get_failure_cnt()
					text += edge.get_name() + ': ' + str(edge.get_failure_cnt()) + ', '

				all_failures += cls._cloud_dc.get_failure_cnt()
				text += cls._cloud_dc.get_name() + ': ' + str(cls._cloud_dc.get_failure_cnt())
				MdpLogger.write_log("Failure frequency occurence: " + text)

				text = ""
				for edge in cls._edge_servers:
					text += edge.get_name() + ': ' + str(round(edge.get_failure_cnt() / all_failures * 100, 2)) + ', '

				text += cls._cloud_dc.get_name() + ': ' + str(round(cls._cloud_dc.get_failure_cnt() / all_failures * 100, 2))
				MdpLogger.write_log("Relative failure frequency occurence: " + text)
				MdpLogger.write_log("Num of failures: " + str(all_failures) + '\n')

				MdpLogger.write_log("Offloading failure distribution: " + \
					str(cls._ode.get_statistics().get_offloading_failure_frequencies()))
				MdpLogger.write_log("Offloading failure frequency relative: " + \
					str(cls._ode.get_statistics().get_offloading_failure_relative()))
				MdpLogger.write_log("Num of offloading failures: " + \
					str(cls._ode.get_statistics().get_num_of_offloading_failures()) + '\n')

				MdpLogger.write_log('Offloading site datasets:')
				for edge in cls._edge_servers:
					MdpLogger.write_log(edge.get_name() + ' ' + str(edge.get_node_candidate()))

				MdpLogger.write_log(cls._cloud_dc.get_name() + ' ' + str(cls._cloud_dc.get_node_candidate()))

				if isinstance(cls._ode, LocalOde):
					cls.deploy_local_ode()

				elif isinstance(cls._ode, EfpoOde):
					cls.deploy_efpo_ode()

				elif isinstance(cls._ode, EnhancedEfpoOde):
					cls.deploy_enhanced_efpo_ode()

				elif isinstance(cls._ode, MobileCloudOde):
					cls.deploy_mobile_cloud_ode()
					
				elif isinstance(cls._ode, EnergyEfficientOde):
					cls.deploy_energy_efficient_ode()

				for edge in cls._edge_servers:
					edge.reset_failure_cnt()

				cls._cloud_dc.reset_failure_cnt()

		else:
			MdpLogger.write_log("You need to DEPLOY mobile application AND offloading decision engine on mobile device before you execute it!")
			MdpLogger.write_log('\n')


	def execute(cls, task):
		print_text = "Task "

		if not isinstance(task, Task):
			MdpLogger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK

		if not task.execute():
			return ExecutionErrorCode.EXE_NOK

		print_text = print_text + task.get_name()
		task_data_storage_consumption = task.get_data_in() + task.get_data_out()
		task_memory_consumption = task.get_memory()

		cls._data_storage_consumption = cls._data_storage_consumption + (task_data_storage_consumption / GIGABYTES)
		cls._memory_consumption = cls._memory_consumption + task_memory_consumption

		#MdpLogger.write_log(print_text + " (off = " + str(task.is_offloadable()) + ") is executed on MOBILE_DEVICE!")
		
		return ExecutionErrorCode.EXE_OK


	def print_system_config(cls):
		print("################### MOBILE DEVICE SYSTEM CONFIGURATION ###################")
		print("CPU: " + str(cls._mips) + " M cycles")
		print("Memory: " + str(cls._memory) + " Gb")
		print("Data Storage: " + str(cls._data_storage) + " Gb")
		print('\n\n')


	def print_app_config(cls):
		cls._mobile_app.print_entire_config()


	def print_connection_config(cls):
		print("################### MOBILE DEVICE CONNECTION CONFIGURATION ###################")

		for edge_server in cls._edge_servers:
			edge_server.print_system_config()

		cls._cloud_dc.print_system_config()


	def print_ode(cls):
		print("################### OFFLOADING DECISION ENGINE ###################")
		print("Name: " + cls._ode.get_name())
		print('\n\n')


	def print_network_connections(cls):
		print("################### NETWORK CONNECTIONS ###################")
		for key, values in cls._network.items():
			for value in values:
				print("Source node is (" + key + ") : Destination nodes: (" + str(value[0]) + "), Latency = " + \
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


	def deploy_antivirus_application(cls):
		gui = Task("GUI", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		load_library = Task("LOAD_LIBRARY", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		scan_file = Task("SCAN_FILE", Util.generate_di_cpu_cycles(), 2, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		compare = Task("COMPARE", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		output = Task("OUTPUT", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)

		antivirus_delay_dict = {
			gui: [(load_library, num.randint(2, 10)), (scan_file, num.randint(2, 10))],
			load_library: [(compare, num.randint(2, 10))],
			scan_file: [(compare, num.randint(2, 10))],
			compare: [(output, num.randint(2, 10))],
			output: []
		}

		cls._mobile_app = MobileApplication(ANTIVIRUS, antivirus_delay_dict)


	def deploy_gps_navigator_application(cls):
		conf_panel = Task("CONF_PANEL", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		gps = Task("GPS", Util.generate_random_cpu_cycles(), 3, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		control = Task("CONTROL", Util.generate_ci_cpu_cycles(), 5, Util.generate_ci_input_data(), Util.generate_ci_output_data(), True)
		maps = Task("MAPS", Util.generate_di_cpu_cycles(), 5, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		path_calc = Task("PATH_CALC", Util.generate_di_cpu_cycles(), 2, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		traffic = Task("TRAFFIC", Util.generate_di_cpu_cycles(), 1, Util.generate_di_input_data(), Util.generate_di_output_data(), True)
		voice_synth = Task("VOICE_SYNTH", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		gui = Task("GUI", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)
		speed_trap = Task("SPEED_TRAP", Util.generate_random_cpu_cycles(), 1, Util.generate_random_input_data(), Util.generate_random_output_data(), False)

		gps_navigator_delay_dict = {
			conf_panel: [(control, num.randint(2, 10))],
			gps: [(control, num.randint(2, 10))],
			control: [(maps, num.randint(2, 10)), (path_calc, num.randint(2, 10)), (traffic, num.randint(2, 10))],
			maps: [(path_calc, num.randint(2, 10))],
			traffic: [(path_calc, num.randint(2, 10))],
			path_calc: [(voice_synth, num.randint(2, 10)), (gui, num.randint(2, 10)), (speed_trap, num.randint(2, 10))],
			voice_synth: [],
			gui: [],
			speed_trap: []
		}

		cls._mobile_app = MobileApplication(GPS_NAVIGATOR, gps_navigator_delay_dict)


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


	def deploy_enhanced_efpo_ode(cls):
		cls._ode = MdpSvrOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, MDP_SVR_ODE_NAME)
		cls.__update_off_site_ode_info()


	def deploy_efpo_ode(cls):
		cls._ode = EfpoOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, EFPO_ODE_NAME)
		cls.__update_off_site_ode_info()


	def deploy_energy_efficient_ode(cls):
		cls._ode = EnergyEfficientOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, EE_ODE_NAME)
		cls.__update_off_site_ode_info()


	def deploy_local_ode(cls):
		cls._ode = LocalOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, LOCAL_ODE_NAME)
		cls.__update_off_site_ode_info()


	def deploy_mobile_cloud_ode(cls):
		cls._ode = MobileCloudOde(cls, cls._edge_servers, cls._cloud_dc, cls._network, MC_ODE_NAME)
		cls.__update_off_site_ode_info()


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


	def get_failure_transition_probability(cls, this):
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
			MdpLogger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK
			
		cls._memory_consumption = cls._memory_consumption - task.get_memory()
		cls._data_storage_consumption = cls._data_storage_consumption - ((task.get_data_in() + task.get_data_out()) / GIGABYTES)

		if cls._memory_consumption < 0 or cls._data_storage_consumption < 0:
			raise ValueError("Memory consumption: " + str(cls._memory_consumption) + "Gb, data storage consumption: " + str(cls._data_storage_consumption) + \
				"Gb, both should be positive! Node: " + cls._name + ", task: " + task.get_name())


	# check the validity of task deployment on mobile device regarding to resource capacity (memory and data storage)
	def check_validity_of_deployment(cls, task):
		if not isinstance(task, Task):
			MdpLogger.write_log("Task for execution on offloading site should be Task class instance!")
			return ExecutionErrorCode.EXE_NOK

		# check that task resouce requirements fits mobile device's resource capacity
		if cls._data_storage > (cls._data_storage_consumption + ((task.get_data_in() + task.get_data_out())) / GIGABYTES) and \
			cls._memory > (cls._memory_consumption + task.get_memory()):
			return ExecutionErrorCode.EXE_OK
		
		return ExecutionErrorCode.EXE_NOK


	def __update_off_site_ode_info(cls):
		ode_type = None
		
		if isinstance(cls._ode, LocalOde):
			ode_type = OdeType.LOCAL

		elif isinstance(cls._ode, EfpoOde):
			ode_type = OdeType.EFPO

		elif isinstance(cls._ode, MdpSvrOde):
			ode_type = OdeType.MDP_SVR

		elif isinstance(cls._ode, MobileCloudOde):
			ode_type = OdeType.MOBILE_CLOUD
					
		elif isinstance(cls._ode, EnergyEfficientOde):
			ode_type = OdeType.ENERGY_EFFICIENT
		
		for edge in cls._edge_servers:
			edge.update_ode_info(ode_type)

		cls._cloud_dc.update_ode_info(ode_type)


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
						SvrLogger.write_log(edge.get_name())
					raise ValueError("Edge servers should have distinct unique names!")