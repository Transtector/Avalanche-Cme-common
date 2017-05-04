import logging, logging.handlers

''' 
config: {
	REMOVE_PREVIOUS: False,
	PATH: '/data/log/cme-boot.log',
	SIZE: 10240,
	COUNT: 1,
	FORMAT: '%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
	LEVEL: 'DEBUG',
	DATE: '%Y-%m-%d %H:%M:%S',
	CONSOLE: False
}
'''
def GetLogger(name, config):

	# delete previous if configured and exists
	if config['REMOVE_PREVIOUS']:
		try:
			os.remove(config['PATH'])
		except:
			pass

	# create a logger by name
	logger = logging.getLogger(name)

	# set the logging level
	level = logging.getLevelName(config['LEVEL'])
	
	# set the logger level to lowest level (DEBUG)
	# and use the handler levels to set the desired
	# level from the config see: http://stackoverflow.com/a/11111212
	logger.setLevel(logging.DEBUG)

	# a nice format for log entries
	formatter = logging.Formatter(config['FORMAT'], datefmt=config['DATE'])

	# use rotating file handler
	fh = logging.handlers.RotatingFileHandler(config['PATH'], maxBytes=config['SIZE'], backupCount=config['COUNT'])

	fh.setFormatter(formatter)
	fh.setLevel(level)
	logger.addHandler(fh)

	if config['CONSOLE']:
		sh = logging.StreamHandler(sys.stdout)
		sh.setFormatter(formatter)
		sh.setLevel(level)
		logger.addHandler(sh)
	
	return logger
