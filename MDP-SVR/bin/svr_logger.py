class SvrLogger(object):

	_file_handler = open("svr_log.txt", 'w')


	@staticmethod
	def write_log(text):
		SvrLogger._file_handler.write(str(text) + "\n")