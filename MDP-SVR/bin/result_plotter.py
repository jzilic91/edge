import re
import math
import matplotlib.pyplot as plt
import numpy as np

MDP_SVR_STR = 'MDP-SVR'
EFPO_STR = 'EFPO'
EE_STR = 'EE'


def print_time_confidence_intervals(resp_time_var_dict):
	for i in range(5):
		print(str(i + 1) + '. dataset configuration (response time):')
		print('MDP-SVR: +/- ' + str(compute_yerr(resp_time_var_dict[MDP_SVR_STR][i])))
		print('EFPO: +/- ' + str(compute_yerr(resp_time_var_dict[EFPO_STR][i])))
		print('EE: +/- ' + str(compute_yerr(resp_time_var_dict[EE_STR][i])))
		print('')


def print_energy_confidence_intervals(energy_consum_var_dict):
	for i in range(5):
		print(str(i + 1) + '. dataset configuration (energy consumption):')
		print('MDP-SVR: +/- ' + str(compute_yerr(energy_consum_var_dict[MDP_SVR_STR][i])))
		print('EFPO: +/- ' + str(compute_yerr(energy_consum_var_dict[EFPO_STR][i])))
		print('EE: +/- ' + str(compute_yerr(energy_consum_var_dict[EE_STR][i])))
		print('')

def print_failure_rate_intervals(failure_rates_var_dict):
	for i in range(5):
		print(str(i + 1) + '. dataset configuration (failure rates):')
		print('MDP-SVR: +/- ' + str(compute_yerr(failure_rates_var_dict[MDP_SVR_STR][i])))
		print('EFPO: +/- ' + str(compute_yerr(failure_rates_var_dict[EFPO_STR][i])))
		print('EE: +/- ' + str(compute_yerr(failure_rates_var_dict[EE_STR][i])))
		print('')


def compute_yerr(data_var):
	return 1.96 * (math.sqrt(data_var)) / math.sqrt(10000)


def plot_response_time_graph(data_mean, i):
	x = np.arange(i)

	ax = plt.subplot(111)
	ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'g', align = 'center', label = 'MDP-SVR')
	ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'r', align = 'center', label = 'EFPO')
	ax.bar(x + 0.2, data_mean[EE_STR], width = 0.2, color = 'm', align = 'center', label = 'EE')

	plt.xlabel('Dataset configurations')
	plt.ylabel('Response time (seconds)')
	plt.title('Average response time after 40 application executions')
	plt.xticks(x, [1, 2, 3, 4, 5], fontsize = 10)
	plt.legend()
	plt.show()


def plot_energy_consumption_graph(data_mean, i):
	x = np.arange(i)

	ax = plt.subplot(111)
	ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'g', align = 'center', label = 'MDP-SVR')
	ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'r', align = 'center', label = 'EFPO')
	ax.bar(x + 0.2, data_mean[EE_STR], width = 0.2, color = 'm', align = 'center', label = 'EE')

	plt.xlabel('Dataset configurations')
	plt.ylabel('Energy consumption (jouls)')
	plt.title('Average energy consumption after 40 application executions')
	plt.xticks(x, [1, 2, 3, 4, 5], fontsize = 10)
	plt.legend()
	plt.show()


def plot_failure_rates(data_mean, i):
	x = np.arange(i)

	ax = plt.subplot(111)
	ax.bar(x - 0.2, data_mean[MDP_SVR_STR], width = 0.2, color = 'g', align = 'center', label = 'MDP-SVR')
	ax.bar(x, data_mean[EFPO_STR], width = 0.2, color = 'r', align = 'center', label = 'EFPO')
	ax.bar(x + 0.2, data_mean[EE_STR], width = 0.2, color = 'm', align = 'center', label = 'EE')

	plt.xlabel('Dataset configurations')
	plt.ylabel('Offloading failure rates (%)')
	plt.title('Offloading failure rates over all application executions')
	plt.xticks(x, [1, 2, 3, 4, 5], fontsize = 10)
	plt.legend()
	plt.show()


def main():
	file_reader = open('simulation_log.txt', 'r')
	mdp_svr_flag = False
	efpo_flag = False
	ee_flag = False
	flags = [False, False, False]
	i = 0

	resp_time_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	energy_consum_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	resp_time_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	energy_consum_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	off_rel_dict = {MDP_SVR_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)], \
		EFPO_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)], \
		EE_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)]}
	num_of_off_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	fail_freq_rel = {MDP_SVR_STR: [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)], \
		EFPO_STR: [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)], \
		EE_STR: [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)]}
	num_of_fail = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	off_fail_freq_rel = {MDP_SVR_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)], \
		EFPO_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)], \
		EE_STR: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)]}
	num_of_off_fail = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	failure_rate_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}
	failure_rate_var_dict = {MDP_SVR_STR: [0, 0, 0, 0, 0], EFPO_STR: [0, 0, 0, 0, 0], EE_STR: [0, 0, 0, 0, 0]}

	for line in file_reader:
		#print(line)
		matched = re.search("(#+) (ENHANCED EFPO OFFLOADING RESULT SUMMARY) (#+)", line)
		if matched:
			mdp_svr_flag = True
			efpo_flag = False
			ee_flag = False
			flags[0] = True
			continue

		matched = re.search("(#+) (EFPO OFFLOADING RESULT SUMMARY) (#+)", line)
		if matched:
			mdp_svr_flag = False
			efpo_flag = True
			ee_flag = False
			flags[1] = True
			continue

		matched = re.search("(#+) (EE OFFLOADING RESULT SUMMARY) (#+)", line)
		if matched:
			mdp_svr_flag = False
			efpo_flag = False
			ee_flag = True
			flags[2] = True
			continue

		matched = re.search("Time mean: (\d+\.\d+) s", line)
		if matched:
			if mdp_svr_flag:
				resp_time_dict[MDP_SVR_STR][i] = float(matched.group(1))

			elif efpo_flag:
				resp_time_dict[EFPO_STR][i] = float(matched.group(1))

			elif ee_flag:
				resp_time_dict[EE_STR][i] = float(matched.group(1))


		matched = re.search("Time variance: (\d+\.\d+) s", line)
		if matched:
			if mdp_svr_flag:
				resp_time_var_dict[MDP_SVR_STR][i] = float(matched.group(1))

			elif efpo_flag:
				resp_time_var_dict[EFPO_STR][i] = float(matched.group(1))

			elif ee_flag:
				resp_time_var_dict[EE_STR][i] = float(matched.group(1))

		matched = re.search("Energy mean: (\d+\.\d+) J", line)
		if matched:
			if mdp_svr_flag:
				energy_consum_dict[MDP_SVR_STR][i] = float(matched.group(1))

			elif efpo_flag:
				energy_consum_dict[EFPO_STR][i] = float(matched.group(1))

			elif ee_flag:
				energy_consum_dict[EE_STR][i] = float(matched.group(1))

		matched = re.search("Energy variance: (\d+\.\d+) J", line)
		if matched:
			if mdp_svr_flag:
				energy_consum_var_dict[MDP_SVR_STR][i] = float(matched.group(1))

			elif efpo_flag:
				energy_consum_var_dict[EFPO_STR][i] = float(matched.group(1))

			elif ee_flag:
				energy_consum_var_dict[EE_STR][i] = float(matched.group(1))

		matched = re.search("Offloading distribution relative: {'MOBILE_DEVICE': (\d+\.\d+), 'EDGE_DATABASE_SERVER_A': (\d+\.\d+), 'EDGE_COMPUTATIONAL_SERVER_A': (\d+\.\d+), 'EDGE_REGULAR_SERVER_A': (\d+\.\d+), 'CLOUD_DATA_CENTER_1': (\d+\.\d+)}", line)
		if matched:
			if mdp_svr_flag:
				off_rel_dict[MDP_SVR_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

			elif efpo_flag:
				off_rel_dict[EFPO_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

			elif ee_flag:
				off_rel_dict[EE_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

		matched = re.search("Num of offloadings: (\d+)", line)
		if matched:
			if mdp_svr_flag:
				num_of_off_dict[MDP_SVR_STR][i] = int(matched.group(1))

			elif efpo_flag:
				num_of_off_dict[EFPO_STR][i] = int(matched.group(1))

			elif ee_flag:
				num_of_off_dict[EE_STR][i] = int(matched.group(1))

		matched = re.search("Relative failure frequency occurence: EDGE_DATABASE_SERVER_A: (\d+\.\d+), EDGE_COMPUTATIONAL_SERVER_A: (\d+\.\d+), EDGE_REGULAR_SERVER_A: (\d+\.\d+), CLOUD_DATA_CENTER_1: (\d+\.\d+)", line)
		if matched:
			if mdp_svr_flag:
				fail_freq_rel[MDP_SVR_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)))

			elif efpo_flag:
				fail_freq_rel[EFPO_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)))

			elif ee_flag:
				fail_freq_rel[EE_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)))

		matched = re.search("Num of failures: (\d+)", line)
		if matched:
			if mdp_svr_flag:
				num_of_fail[MDP_SVR_STR][i] = int(matched.group(1))

			elif efpo_flag:
				num_of_fail[EFPO_STR][i] = int(matched.group(1))

			elif ee_flag:
				num_of_fail[EE_STR][i] = int(matched.group(1))

		matched = re.search("Offloading failure frequency relative: {'MOBILE_DEVICE': (\d+\.\d+), 'EDGE_DATABASE_SERVER_A': (\d+\.\d+), 'EDGE_COMPUTATIONAL_SERVER_A': (\d+\.\d+), 'EDGE_REGULAR_SERVER_A': (\d+\.\d+), 'CLOUD_DATA_CENTER_1': (\d+\.\d+)}", line)
		if matched:
			if mdp_svr_flag:
				off_fail_freq_rel[MDP_SVR_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

			elif efpo_flag:
				off_fail_freq_rel[EFPO_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

			elif ee_flag:
				off_fail_freq_rel[EE_STR][i] = (float(matched.group(1)), float(matched.group(2)), float(matched.group(3)), float(matched.group(4)), float(matched.group(5)))

		matched = re.search("Num of offloading failures: (\d+)", line)
		if matched:
			if mdp_svr_flag:
				num_of_off_fail[MDP_SVR_STR][i] = int(matched.group(1))

			elif efpo_flag:
				num_of_off_fail[EFPO_STR][i] = int(matched.group(1))

			elif ee_flag:
				num_of_off_fail[EE_STR][i] = int(matched.group(1))

			if flags[0] and flags[1] and flags[2]:
				flags[0] = False
				flags[1] = False
				flags[2] = False
				i += 1

		matched = re.search("Offloading failure rate mean: (\d+\.\d+) failures", line)
		if matched:
			if mdp_svr_flag:
				failure_rate_dict[MDP_SVR_STR][i] = float(matched.group(1)) / 40 * 100

			elif efpo_flag:
				failure_rate_dict[EFPO_STR][i] = float(matched.group(1)) / 40 * 100

			elif ee_flag:
				failure_rate_dict[EE_STR][i] = float(matched.group(1)) / 40 * 100


		matched = re.search("Offloading failure rate variance: (\d+\.\d+) failures", line)
		if matched:
			if mdp_svr_flag:
				failure_rate_var_dict[MDP_SVR_STR][i] = float(matched.group(1)) / 40 * 100

			elif efpo_flag:
				failure_rate_var_dict[EFPO_STR][i] = float(matched.group(1)) / 40 * 100

			elif ee_flag:
				failure_rate_var_dict[EE_STR][i] = float(matched.group(1)) / 40 * 100

	
	plot_response_time_graph(resp_time_dict, i)
	plot_energy_consumption_graph(energy_consum_dict, i)
	plot_failure_rates(failure_rate_dict, i)

	print_time_confidence_intervals(resp_time_var_dict)
	print_energy_confidence_intervals(energy_consum_var_dict)
	print_failure_rate_intervals(failure_rate_var_dict)

	file_reader = open('svr_log.txt', 'r')
	node_candidate_svr_time_dict = {}
	node_candidate_train_sample_size = {}
	current_key = None

	for line in file_reader:
		matched = re.search("Node candidate: (\(\d+\, \d+\))", line)
		if matched:
			current_key = matched.group(1)
			if not (matched.group(1) in node_candidate_svr_time_dict):
				node_candidate_svr_time_dict[matched.group(1)] = list()

		matched = re.search("Training CPU time \(.+\): (\d+\.\d+)s", line)
		if matched:
			node_candidate_svr_time_dict[current_key].append(float(matched.group(1)))

		matched = re.search("Training sample size: (\d+)", line)
		if matched:
			node_candidate_train_sample_size[current_key] = int(matched.group(1))

	for key, value in node_candidate_svr_time_dict.items():
		print('Min time for ' + key + ' is ' + str(min(value)) + ' s')
		print('Max time for ' + key + ' is ' + str(max(value)) + ' s')
		print('Mean time for ' + key + ' is ' + str(round(sum(value) / len(value), 4)) + ' s')
		print('Training sample size: ' + str(node_candidate_train_sample_size[key]))
		print('\n')


if __name__ == "__main__":
	main()