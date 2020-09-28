class MdpLogger(object):

	file_handler = open("simulation_log.txt", 'w')

	@staticmethod
	def write_log(text):
		if True:
			MdpLogger.file_handler.write(text + "\n")