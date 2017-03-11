''' General Cme system configuration file.

	This file is shared by all top-level Cme programs/projects
	from the Cme-common submodule.  Any changes here need to 
	be committed to Cme-common and then pulled into the projects
	desiring to see the changes.

	Sections within are namespaced by using classes.  To use these
	configuration values in the project, just do:

		from .common import Config
		myConfig_Value = Config.CLASS.MY_CONFIG_KEY

	Some of the settings are user-configurable.  They are NOT
	changed within this file (which always holds 'factory defaults'),
	but cached in the USERDATA folder in a file called 'settings.json'.
	Currently, only the Cme program is responsible for providing
	access to the user-configurable settings.
'''

import os, uuid, platform, json


# Temperature units enumeration
class TemperatureUnits:
	CELSIUS = 0
	FAHRENHEIT = 1


# Time display enumeration
class RelativeTo:
	UTC = 0 # display times relative to UTC (zone offset = 0)
	CmeLocal = 1 # display times relative to Cme's zone offset
	Local = 2 # display times relative to the client zone



class PATHS:
	''' Holds the file paths shared throughout the system.
	'''
	APPROOT = os.path.abspath(os.getcwd()) # /root/<package>, e.g., "/root/Cme/"
	USERDATA = os.path.abspath('/data') # User data is stored here

	# This is where the USER_SETTINGS are kept
	SETTINGS = os.path.join(USERDATA, 'settings.json')

	# uploads go to temp folder above app
	UPLOADS = os.path.abspath(os.path.join(USERDATA, 'tmp'))

	# updates are pending until restart, then removed if successful
	UPDATE = os.path.abspath(os.path.join(USERDATA, 'update'))

	# updates can be put on USB (removable) media
	USB = os.path.abspath('/media/usb')

	# where log files are kept
	LOGDIR = os.path.abspath(os.path.join(USERDATA, 'log'))

	# channel data and configuration are stored here
	CHDIR = os.path.abspath(os.path.join(USERDATA, 'channels')) # /data/channels

	VERSION_FILE = os.path.join(PATHS.APPROOT, 'VERSION')

	DEVICE_FILE = os.path.join(USERDATA, 'device.json')

	# This file created prior to rebooting to signal init process to boot to recovery mode
	# (i.e., don't launch module dockers).  Note that it is removed after detection by the
	# boot process.  Recovery mode is indicated if the cme package is NOT running inside a
	# docker container.
	RECOVERY_FILE = os.path.abspath(os.path.join(USERDATA, '.recovery'))

	# create USERDATA folders if they don't yet exist
	for p in [ UPLOADS, UPDATE, LOGDIR, CHDIR ]:
		if not os.path.exists(p):
			os.makedirs(p)



class INFO:
	''' Holds general system information and application package version.
	'''
	DEBUG = True
	HOSTNAME = platform.node()
	SYSTEM = platform.uname()

	# Each CME package uses a simple VERSION file
	# to hold its revision.  The file should be
	# found in the package root folder.
	VERSION = 'x.x.x'

	# It's a complete failure if VERSION cannot be read, this
	# will fail launching every package if it errors here.
	with open(PATHS.VERSION_FILE, "r") as f:
		VERSION = f.readline().strip()

	# CME Device info is 'hard-coded' into the device.json
	# read-only file in the USERDATA folder.  It may not exist
	# if the Cme device has not yet gone through production so
	# we don't want to fail here.
	DEVICE = {
		'host': {
			'modelNumber': '', 
			'serialNumber': '',
			'dateCode': ''
		},
		'cme': {
			'modelNumber': 'UNKNOWN', 
			'serialNumber': '00000000',
			'dateCode': '20170101',
			'unlocked': True
		}
	}

	try:
		with open(PATHS.DEVICE_FILE, "r") as f:
			DEVICE = json.load(f)
	except:
		pass

	# Set the Cme device version here whether we loaded it from device.json
	# or are just using defaults.
	DEVICE['cme'].setdefault('firmware', VERSION)



class UPDATES:
	''' Holds information about how software updates are located and verified.
	'''
	# These locations are checked for available updates (along with /media/usb)
	PUBLIC_UPDATES_URL = ['https://s3.amazonaws.com/transtectorpublicdownloads/']

	# Filnames much match this pattern to be seen in API
	UPDATE_GLOB = '15??-???-v*-SWARE-CME*.tgz'

	# TODO: figure out size/extension for actual firmware files
	ALLOWED_EXTENSIONS = ['tgz', 'tar.gz']
	MAX_CONTENT_LENGTH = 500 * 1024 * 1024 #  500 MB



class RECOVERY:
	''' The system normally runs the application packages (Cme, Cme-hw) under their own
		docker containers.  However, at a base-level, the Cme application package (which
		contains the API) will launch as "recovery mode".
	'''
	# recovery mode if we're not running inside a docker container
	from . import is_a_docker
	RECOVERY_MODE = not is_a_docker()

	# How long to hold reset button?
	RESET_REBOOT_SECONDS = 3 # <= this time: reboot; > this time: recovery or factory reset
	RESET_RECOVERY_SECONDS = 10 # <= this time: recovery mode; > this time: factory reset



class LOGGING:
	''' Controls how the application package loggers store their log files
	'''
	LOGBYTES = 1024 * 50
	LOGCOUNT = 1

	BOOTLOG = os.path.join(PATHS.LOGDIR, 'cme-boot.log')
	APILOG = os.path.join(PATHS.LOGDIR, 'cme.log')
	HWLOG = os.path.join(PATHS.LOGDIR, 'cme-hw.log')
	SERVERLOG = os.path.join(PATHS.LOGDIR, 'server.log')
	ACCESSLOG = os.path.join(PATHS.LOGDIR, 'access.log')



class RRD:
	''' Round-robin database settings
	'''
	# rrdcached is a cache service wrapping the rrd tool
	# See rrdtool.org for details.  Default address is
	# "localhost" and the default port is 42217.  You can
	# override this by passing a command line option as:
	#	$ python -m cme --rrdcached 'server'
	RRDCACHED = None #'localhost'



class HARDWARE:
	''' Cme-hw specific configuration
	'''
	LOOP_PERIOD_s = 1.0 # Cme-hw polling loop speed
	BUFFER_POINTS = 5 # each sensor keeps a rolling buffer of this many points
	MAX_ALARM_POINTS = 20 # max number of points recorded during alarm condition
	ALARM_LEAD_POINTS = 5 # number of pre- and post-alarm points saved in alarm traces



class API:
	''' These is API program layer specific configuration  
	'''
	SESSION_COOKIE_NAME = 'cmeSession'
	SESSION_EXPIRATION = 86400 # 24 hours
	SECRET_KEY = '99a83105bf3264465f2cd9c559d3c573' # md5('Kaelus0x0x0')

	SERVER_HOST = '0.0.0.0' # listen all interfaces
	SERVER_PORT = 80 # ports < 1024 require sudo to start

	USERNAME = 'admin'
	PASSHASH = 'b56e0b4ea4962283bee762525c2d490f' # md5('Welcome1')


from .DictPersistJSON import DictPersistJSON
from .ClockUtils import check_ntp, ntp_servers
from .IpUtils import mac, dhcp, address, netmask, gateway

''' User settings are cached in an external file 'settings.json'.  Import
	the Settings.py module and pass it through this class constructor to
	update the default values below.  Simply delete the settings.json file
	to return values to their factory defaults.

	Access USER_SETTINGS like this:

		from .common import Config
		user_setting = Config.USER_SETTINGS['user_setting_key']

	*Note: if you want to save a USER_SETTING that's part of
	a dict itself (e.g., GENERAL > NAME), then you have to 
	write the enire object.

	I.e., do this to make changes that get saved to disk:

		general = Config.USER_SETTINGS['GENERAL']
		general['NAME'] = 'My cool new name'
		Config.USER_SETTINGS['GENERAL'] = general


	*Note: Use an underscore character on items that you DON'T
	want to get serialized (e.g., to API respones).  For example
	the username and passhash are user settings, but we never
	want to serve them up as part of a response, so we prefix
	with underscores.
	'''
USER_SETTINGS = DictPersistJSON(PATHS.SETTINGS, {

	'__username': API.USERNAME,
	'__passhash': API.PASSHASH,
	'__device': INFO.DEVICE,

	'general': {
		'name': 'CME',
		'description': 'Core monitoring engine',
		'location': '',
		'sitecode': ''
	},

	'support': {
		'contact': '',
		'email': '',
		'phone': ''
	},

	'temperature': {
		'displayUnits': TemperatureUnits.CELSIUS,
		'warningTemp': 65, # ºC
		'alarmTemp': 80 # ºC
	},

	'clock': {
		'ntp': check_ntp(),
		'servers': ntp_servers(),
		'status': [],
		'zone': 0,
		'displayRelativeTo': RelativeTo.UTC,
		'display12Hour': False,
		'displayDateFormat': "YYYY-MM-DD",
		'displayTimeFormat24Hour': "HH:mm:ss",
		'displayTimeFormat12Hour': "h:mm:ss A"
	},

	'network': {
		'mac': mac(),
		'dhcp': dhcp(),
		'address': address(),
		'netmask': netmask(),
		'gateway': gateway(),
		'primary': '8.8.4.4',
		'secondary': '8.8.8.8'
	}
})




