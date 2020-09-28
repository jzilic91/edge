
#############################
####### STD LIBRARIES #######
#############################

import numpy as np
import matplotlib.pyplot as plt
import time
import os
import math

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from statistics import mean, stdev


#############################
##### CUSTOM LIBRARIES ######
#############################

from utilities import PredictionMode, ExecutionMode, SlidingWindowSize, DataType, DatasetType, WorkingCondition, NodeCategory, OdeType
from metrics import Metrics
from svr_logger import SvrLogger
from mdp_logger import MdpLogger


class SupportVectorRegression:

	def __init__(self, dataset, dataset_type, regressor_type, offloading_site_name, node_candidate, degree = 0):
		self._dataset = dataset
		self._dataset_type = dataset_type
		self._offloading_site_name = offloading_site_name

		if regressor_type == 'linear':
			self._svr = SVR(regressor_type)

		elif regressor_type == 'poly':
			self._svr = SVR(regressor_type, degree)

		elif regressor_type == 'rbf':
			self._svr = SVR(regressor_type)

		else:
			exit('Unidentified regressor type ' + regressor_type)

		self._regressor_type = regressor_type
		self._degree = degree
		self._epsilon = 0
		self._C = 0

		self._train_nrmse = tuple()
		self._train_rmse = tuple()
		self._train_mae = tuple()
		self._train_r2 = tuple()
		self._train_emp_risk = tuple()

		self._test_nrmse = tuple()
		self._test_rmse = tuple()
		self._test_mae = tuple()
		self._test_r2 = tuple()
		self._test_emp_risk = tuple()

		self._test_window_size = SlidingWindowSize.SIZE_10

		self._random_state = 0
		self._x_train = 0
		self._x_test = 0
		self._y_train = 0
		self._y_test = 0

		self._predicted = None
		self._node_candidate = node_candidate
		

	def train(cls):
		# folder_path = cls._dataset.get_folder_path() + 'results/' + cls._regressor_type
		# if cls._regressor_type == 'linear':
		# 	cls.__remove_files_from_folder(folder_path)

		# elif cls._regressor_type == 'poly':
		# 	folder_path = folder_path + '_' + str(cls._degree)
		# 	cls.__remove_files_from_folder(folder_path)

		# elif cls._regressor_type == 'rbf':
		# 	cls.__remove_files_from_folder(folder_path)

		cls._train_nrmse = tuple()
		cls._train_rmse = tuple()
		cls._train_mae = tuple()
		cls._train_r2 = tuple()
		cls._train_emp_risk = tuple()

		node_category = cls._dataset.get_node_category()
		cls.__separate_dataset()

		consum_time = cls.__compute_fitting_time(cls._x_train, cls._y_train)
		predicted = cls._svr.predict(cls._x_train)

		cls._C = cls.__compute_C(cls._y_train)
		res_error = np.subtract(cls._y_train, predicted)
		cls._epsilon = cls.__compute_epsilon(res_error)
		cls._svr = SVR(kernel = cls._regressor_type, degree = cls._degree, C = cls._C, epsilon = cls._epsilon)

		consum_time = cls.__compute_fitting_time(cls._x_train, cls._y_train)
		SvrLogger.write_log('Node candidate: ' + str(cls._node_candidate))
		SvrLogger.write_log('Training CPU time (' + node_category + '): ' + str(consum_time) + 's')
		SvrLogger.write_log('Training sample size: ' + str(len(cls._x_train)))
		
		predicted = cls._svr.predict(cls._x_train)
						
		cls.__log_regression_results(cls._y_train, predicted, cls._dataset, PredictionMode.TRAINING_PREDICTION_MODE)

		# SvrLogger.write_log('################################################################')
		# SvrLogger.write_log('################### SVR RELIABILITY ESTIMATION #################')
		# SvrLogger.write_log('################################################################\n')

		# SvrLogger.write_log('******************** TRAINING SUMMARY **************************')
		# SvrLogger.write_log('Train NRMSE: ' + str(round(sum(cls._train_nrmse) / len(cls._train_nrmse), 3)))
		# SvrLogger.write_log('Train RMSE: ' + str(round(sum(cls._train_rmse) / len(cls._train_rmse), 3)))
		# SvrLogger.write_log('Train MAE: ' + str(round(sum(cls._train_mae) / len(cls._train_mae), 3)))
		# SvrLogger.write_log('Train R2: ' + str(round(sum(cls._train_r2) / len(cls._train_r2), 3)))
		# SvrLogger.write_log('Train empirical risk: ' + str(np.round(sum(cls._train_emp_risk) / len(cls._train_emp_risk), 3)) + '\n')

		cls.__predict()


	def get_test_data(cls):
		data = np.array(cls._y_test).reshape(1, -1)[0]

		for i in range(len(data)):
			data[i] = '{:.2f}'.format(data[i])

		#MdpLogger.write_log('TESTING DATA: ' + str(data))

		return data


	def get_predicted_data(cls):
		data = np.array(cls._predicted).reshape(1, -1)[0]
		
		for i in range(len(data)):
			data[i] = '{:.2f}'.format(data[i])

		#MdpLogger.write_log('PREDICTED DATA: ' + str(data))

		return data


	def get_node_candidate(cls):
		return cls._node_candidate


	def get_new_test_predicted_data(cls, ode_type):
		# MdpLogger.write_log('Node candidate: ' + str(cls._node_candidate))
		
		if ode_type == OdeType.MDP_SVR:
			cls.train()
		
		else:
			cls.__separate_dataset()

		return (cls.get_test_data(), cls.get_predicted_data())


	def __predict(cls):
		cls._test_nrmse = tuple()
		cls._test_rmse = tuple()
		cls._test_mae = tuple()
		cls._test_r2 = tuple()
		cls._test_emp_risk = tuple()

		node_category = cls._dataset.get_node_category()
		
		start_time = time.time()
		cls._predicted = cls._svr.predict(cls._x_test)
		# SvrLogger.write_log('Prediction CPU time (' + node_category + '): ' + str(time.time() - start_time) + ' s')
		# SvrLogger.write_log('Test sample size: ' + str(len(cls._x_test)) + '\n')
						
		cls.__log_regression_results(cls._y_test, cls._predicted, cls._dataset, PredictionMode.TEST_PREDICTION_MODE)

		# MdpLogger.write_log('Test NRMSE: ' + str(round(sum(cls._test_nrmse) / len(cls._test_nrmse), 3)))
		# MdpLogger.write_log('Test RMSE: ' + str(round(sum(cls._test_rmse) / len(cls._test_rmse), 3)))
		# MdpLogger.write_log('Test MAE: ' + str(round(sum(cls._test_mae) / len(cls._test_mae), 3)))
		# MdpLogger.write_log('Test R2: ' + str(round(sum(cls._test_r2) / len(cls._test_r2), 3)))
		# MdpLogger.write_log('Test empirical risk: ' + str(np.round(sum(cls._test_emp_risk) / len(cls._test_emp_risk), 3)) + \
		# 	'\n\n')

		# MdpLogger.write_log('Offloading site name: ' + cls._offloading_site_name)
		# MdpLogger.write_log('Node system id / node number: ' + str((cls._node_candidate)))
		# MdpLogger.write_log('\n')


	def __separate_dataset(cls):
		cls._random_state = 5725
		data = cls._dataset.get_node_candidate_avail(cls._node_candidate[0], cls._node_candidate[1])		
		cls._x_train, cls._x_test, cls._y_train, cls._y_test = \
			train_test_split(range(len(data)), data, train_size = 0.8, random_state = cls._random_state)
		cls._x_train = np.array(cls._x_train).reshape(-1, 1)
		cls._y_train = np.array(cls._y_train).reshape(-1, 1)
		cls._x_test = np.array(cls._x_test).reshape(-1, 1)
		cls._y_test = np.array(cls._y_test).reshape(-1, 1)


	def __print_regression_results(cls, actual, predicted, node_category):
		print('###### REGRESSION RESULTS for ' + node_category + '  ######')
		print('NRMSE: ' + str(Metrics.nrmse(actual, predicted)))
		print('RMSE: ' + str(Metrics.rmse(actual, predicted)))
		print('MAE: ' + str(Metrics.mean_absolute_error(actual, predicted)))
		print('R2: ' + str(Metrics.r2_score(actual, predicted)))
		print('Empirical risk: ' + str(Metrics.empirical_risk(actual, predicted, cls._epsilon)))
		Metrics.residual_plot(actual, predicted)


	def __plot_regression_results(cls, x_data, y_data, node_category, prediction_mode_str, data_type):
		plt.close()
		fig, ax = plt.subplots(constrained_layout = True)

		if prediction_mode_str == PredictionMode.TRAINING_PREDICTION_MODE:
			print('TRAINING')
			consum_time = cls.__compute_fitting_time(x_data, y_data)
			cls._C = cls.__compute_C(y_data)
			print('PREDICTING DATA!!!!')
			predicted = cls._svr.predict(x_data)
			res_error = np.subtract(y_data, predicted)
			cls._epsilon = cls.__compute_epsilon(res_error)
			print('C = ' + str(cls._C))
			print('epsilon = ' + str(cls._epsilon))
			cls._svr = SVR(kernel = cls._regressor_type, degree = cls._degree, C = cls._C, epsilon = cls._epsilon)
			print('SVR params:' + str(cls._svr.get_params()))

			consum_time = cls.__compute_fitting_time(x_data, y_data)
			print('CPU time (' + node_category + '): ' + str(consum_time) + 's')

		elif prediction_mode_str == PredictionMode.TEST_PREDICTION_MODE:
			print('TEST!!!!!!')
			print('PREDICTING DATA!!!!')
			print('SVR params:' + str(cls._svr.get_params()))
			predicted = cls._svr.predict(x_data)

		ax.scatter(x_data, y_data, color = 'magenta')
		ax.scatter(x_data, predicted, color = 'green')
		fig.suptitle('Sample size = ' + str(len(y_data)) + ', NMRSE = ' + \
			str(round(Metrics.nrmse(y_data, predicted), 4)) + ', R2 = ' + str(round(Metrics.r2_score(y_data, predicted), 4)))

		if data_type == DataType.TIME_BETWEEN_FAILURE:
			ax.set_title('TBF prediction (' + prediction_mode_str +  ') for ' + node_category + \
				' (' + cls._data_storage.get_dataset_type() + ' dataset)')
			ax.set_xlabel('Failure index')
			ax.set_ylabel('TBF (days)')

		elif data_type == DataType.FAILURE_RATE:
			ax.set_title('Failure rate prediction (' + prediction_mode_str +  ') for ' + node_category + \
				' (' + cls._data_storage.get_dataset_type() + ' dataset)')
			ax.set_xlabel('Datetime')
			ax.set_ylabel('Failure rate')

		elif data_type == DataType.AVAILABILITY:
			ax.set_title('Availability prediction (' + prediction_mode_str +  ') for ' + node_category + \
				' (' + cls._data_storage.get_dataset_type() + ' dataset)')
			ax.set_xlabel('Day')
			ax.set_ylabel('Availability (per day)')
		
		plt.show()

		return predicted


	def __compute_fitting_time(cls, x_data, y_data):
		start = time.time()
		cls._svr.fit(x_data, y_data)
		
		return round(time.time() - start, 4)


	def __log_regression_results(cls, actual, predicted, dataset, prediction_mode):
		SvrLogger.write_log('Prediction mode: ' + prediction_mode)

		if type(actual) is float or type(actual) is np.float64 or type(actual) is int:
			SvrLogger.write_log('Sample size: 1')
		else:
			SvrLogger.write_log('Sample size: ' + str(len(actual)))

		if prediction_mode == PredictionMode.TRAINING_PREDICTION_MODE:
			cls._train_nrmse += (Metrics.nrmse(actual, predicted),)
			cls._train_rmse += (Metrics.rmse(actual, predicted),)
			cls._train_mae += (Metrics.mean_absolute_error(actual, predicted),)
			cls._train_r2 += (Metrics.r2_score(actual, predicted),)
			cls._train_emp_risk += (Metrics.empirical_risk(actual, predicted, cls._epsilon),)

		elif prediction_mode == PredictionMode.TEST_PREDICTION_MODE:
			cls._test_nrmse += (Metrics.nrmse(actual, predicted),)
			cls._test_rmse += (Metrics.rmse(actual, predicted),)
			cls._test_mae += (Metrics.mean_absolute_error(actual, predicted),)
			cls._test_r2 += (Metrics.r2_score(actual, predicted),)
			cls._test_emp_risk += (Metrics.empirical_risk(actual, predicted, cls._epsilon),)

		SvrLogger.write_log('NRMSE: ' + str(Metrics.nrmse(actual, predicted)))
		SvrLogger.write_log('RMSE: ' + str(Metrics.rmse(actual, predicted)))
		SvrLogger.write_log('MAE: ' + str(Metrics.mean_absolute_error(actual, predicted)))
		SvrLogger.write_log('R2: ' + str(Metrics.r2_score(actual, predicted)))
		SvrLogger.write_log('Empirical risk: ' + str(Metrics.empirical_risk(actual, predicted, cls._epsilon)))
		SvrLogger.write_log('')


	def __write_setup_stats_log(cls, dataset):
		SvrLogger.open_file_log(dataset.get_folder_path() + 'setup/setup_stats.txt')
		SvrLogger.write_log(dataset.get_node_category())
		SvrLogger.write_log('Node ID: ' + str(dataset.get_node_candidate_id()))
		SvrLogger.write_log('Processors: ' + str(dataset.get_node_candidate_num_procs()))
		SvrLogger.write_log('Memory size: ' + str(dataset.get_node_candidate_mem_size()))
		SvrLogger.write_log('Failure: ' + str(dataset.get_node_candidate_num_failures()))
		SvrLogger.write_log('TIMESTAMPS')

		index = 1
		for timestamp in dataset.get_node_candidate_failure_timestamps():
			SvrLogger.write_log(str(index) + '. ' + timestamp)
			index += 1


	def __remove_files_from_folder(cls, folder):
		for filename in os.listdir(folder):
		    file_path = os.path.join(folder, filename)
		    try:
		        if os.path.isfile(file_path) or os.path.islink(file_path):
		            os.unlink(file_path)
		        elif os.path.isdir(file_path):
		            shutil.rmtree(file_path)
		    except Exception as e:
		        print('Failed to delete %s. Reason: %s' % (file_path, e))


	def __convert_str_to_datetime(cls, data_frames):
		conv_data = tuple()

		for data in data_frames:
			conv_data += (datetime.strptime(data['Date'], '%m/%d/%Y %H:%M'),)

		return conv_data


	def __compute_C(cls, data):
		mean_ = np.mean(data)
		std_ = np.std(data)

		if mean_ == 0 or std_ == 0:
			return 1

		return max(abs(mean_ + 3 * std_), abs(mean_ - 3 * std_))
		#return 1


	def __compute_epsilon(cls, data):
		std = np.std(data)
		n = len(data)

		if std == 0 or n == 0:
			return 0.1

		return 0.001
		#return 3 * std * math.sqrt(np.log(n) / n)