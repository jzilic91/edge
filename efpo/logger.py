class Logger(object):

	file_handler = open("simulation_log.txt", 'w')

	@staticmethod
	def write_log(text):
		if True:
			Logger.file_handler.write(text + "\n")