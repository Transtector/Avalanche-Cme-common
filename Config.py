# Default CME device configuration.  This file should NOT be changed
# after release.  It's content is used to create a default running
# configuration - changes to which are persisted in a separate file,
# settings.json.  When settings.json is loaded during startup, the
# configuration values herein may be overridden.  To reset all config
# values to defaults, simply delete settings.json.
import os, uuid, platform, json

DEBUG = True

HOSTNAME = platform.node()
SYSTEM = platform.uname()

# Each CME package is stored at APPROOT.
# When this file (Config.py) is imported by each
# package, APPROOT will hold its folder.  So, here
# are the general results:
# Cme-init: /root/Cme-init
# Cme: /root/Cme
# Cme-hw: /root/Cme-hw
APPROOT = os.path.abspath(os.getcwd())

# Each CME package uses a simple VERSION file
# to hold its revision.  The file should be
# found in the package root folder.
VERSION_FILE = os.path.join(APPROOT, 'VERSION')
VERSION = 'x.x.x'

# It's a complete failure if VERSION cannot be read...
with open(VERSION_FILE, "r") as f:
	VERSION = f.readline().strip()


USERDATA = os.path.abspath('/data') # User data is stored here

# This file created prior to rebooting to signal init process
# to boot to recovery mode (don't launch module dockers).  Note that
# it is removed after detection by the boot process.  Recovery mode
# is indicated if the cme package is NOT running inside a docker.
# See RECOVERY key below.
RECOVERY_FILE = os.path.abspath(os.path.join(USERDATA, '.recovery')) # /data/.recovery

# How long to hold reset button?
RESET_REBOOT_SECONDS = 3 # <= this time: reboot; > this time: recovery or factory reset
RESET_RECOVERY_SECONDS = 10 # <= this time: recovery mode; > this time: factory reset


# uploads go to temp folder above app
# this name is used by Flask as well
UPLOAD_FOLDER = os.path.abspath(os.path.join(USERDATA, 'tmp')) # /data/tmp

# updates are pending until restart, then removed if successful
UPDATE = os.path.abspath(os.path.join(USERDATA, 'update')) # /data/update

# updates can be put on USB (removable) media
USB = os.path.abspath('/media/usb')

# globbing pattern for update image files
UPDATE_GLOB = '1500-???-v*-SWARE-CME*.tgz'
PUBLIC_UPDATES_URL = 'https://s3.amazonaws.com/transtectorpublicdownloads/'


# logging to files in parent folder
LOGDIR = os.path.abspath(os.path.join(USERDATA, 'log')) # /data/log
LOGBYTES = 1024 * 50
LOGCOUNT = 1

# channel data and configuration are stored here
CHDIR = os.path.abspath(os.path.join(USERDATA, 'channels')) # /data/channels

BOOTLOG = os.path.join(LOGDIR, 'cme-boot.log')
APILOG = os.path.join(LOGDIR, 'cme.log')
HWLOG = os.path.join(LOGDIR, 'cme-hw.log')
SERVERLOG = os.path.join(LOGDIR, 'server.log')
ACCESSLOG = os.path.join(LOGDIR, 'access.log')

# rrdcached is a cache service wrapping the rrd tool
# See rrdtool.org for details.  Default address is
# "localhost" and the default port is 42217.  You can
# override this by passing a command line option as:
#	$ python -m cme --rrdcached 'server'
RRDCACHED = None #'localhost'

# Cme-hw polling loop speed
LOOP_PERIOD_s = 1.0

# user-defined API layer settings are kept here
SETTINGS = os.path.join(USERDATA, 'settings.json')

# recovery mode if we're not running inside a docker container
from . import is_a_docker
RECOVERY = not is_a_docker()

# create USERDATA folders if they don't yet exist
for p in [ UPLOAD_FOLDER, UPDATE, LOGDIR, CHDIR ]:
	if not os.path.exists(p):
		os.makedirs(p)

# this for uploading files (ostensibly firmware files)
# TODO: figure out size/extension for actual firmware files
ALLOWED_EXTENSIONS = ['tgz', 'tar.gz']
MAX_CONTENT_LENGTH = 500 * 1024 * 1024 #  500 MB

SESSION_COOKIE_NAME = 'cmeSession'
SESSION_EXPIRATION = 86400 # 24 hours
SECRET_KEY = '99a83105bf3264465f2cd9c559d3c573' # md5('Kaelus0x0x0')

SERVER_HOST = '0.0.0.0' # listen all interfaces
SERVER_PORT = 80 # ports < 1024 require sudo to start

USERNAME = 'admin'
PASSHASH = 'b56e0b4ea4962283bee762525c2d490f' # md5('Welcome1')


# CME Device info is 'hard-coded' into the device.json
# read-only file in the USERDATA folder.
DEVICE_FILE = os.path.join(USERDATA, 'device.json')
try:
	with open(DEVICE_FILE, "r") as f:
		DEVICE_DATA = json.load(f)
except:
	# Default device data below.  We get here because no device.json file yet exists.
	# One will be created during CME production/calibration procedures.
	# The cme['unlocked'] will be removed when production creates the
	# 'device.json' file, and is used to prevent further updates to the 
	# CME device information after it passes through production.
	DEVICE_DATA = {
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

# Set the firmware version here whether we loaded it from device.json
# or are just using defaults.
DEVICE_DATA['cme'].setdefault('firmware', VERSION)

GENERAL_NAME = "CME"
GENERAL_DESCRIPTION = "Core monitoring engine"
GENERAL_LOCATION = ""

SUPPORT_CONTACT = ""
SUPPORT_EMAIL = ""
SUPPORT_PHONE = ""

# CME Temperature configuration
class TemperatureUnits:
	CELSIUS = 0
	FAHRENHEIT = 1

TEMPERATURE_DISPLAY_UNITS = TemperatureUnits.CELSIUS
TEMPERATURE_WARNING_TEMP = 65 # ºC
TEMPERATURE_ALARM_TEMP = 80 # ºC


''' CLOCK (ntp) CONFIGURATION

	These keys must be initialized before use.  After importing Config
	do a Config.initialize_Clock() to get these values loaded.  Note
	that if you're doing this from a dockerized Python app, then you'll
	need the cme-docker-fifo.sh system call handler running as well as
	extra volumes mapped.  Typically this is _only_ done for the CME
	API layer package (cme). '''
CLOCK_USE_NTP = None
CLOCK_NTP_SERVERS = None
def initialize_Clock():
	# These settings are read from the /etc/network configuration.  On factory
	# resets, the network can (optionally) be reset as well.
	# (see Cme/ref/interfaces_static; deploys to /etc/network/interfaces_static)
	from .ClockUtils import check_ntp, ntp_servers

	global CLOCK_USE_NTP
	global CLOCK_NTP_SERVERS

	# default NTP settings are obtained from /etc/ntp.conf
	CLOCK_USE_NTP = check_ntp()
	CLOCK_NTP_SERVERS = ntp_servers()

# lookup for clock display reference zone
# this is manually duplicated in client code,
# so be careful when making changes
class RelativeTo:
	UTC = 0 # display times relative to UTC (zone offset = 0)
	CmeLocal = 1 # display times relative to Cme's zone offset
	Local = 2 # display times relative to the client zone


# clock display settings
# see momentjs.org for valid display formats
CLOCK_ZONE_OFFSET = 0
CLOCK_DISPLAY_RELATIVE_TO = RelativeTo.UTC
CLOCK_DISPLAY_12HOUR = False
CLOCK_DISPLAY_DATE_FORMAT = "YYYY-MM-DD" 
CLOCK_DISPLAY_24HOUR_FORMAT = "HH:mm:ss"
CLOCK_DISPLAY_12HOUR_FORMAT = "h:mm:ss A"


''' NETWORK (ntp) CONFIGURATION

	These keys must be initialized before use.  After importing Config
	do a Config.initialize_Network() to get these values loaded.  Note
	that if you're doing this from a dockerized Python app, then you'll
	need the cme-docker-fifo.sh system call handler running as well as
	extra volumes mapped.  Typically this is _only_ done for the CME
	API layer package (cme). '''
MAC = ''
DHCP = False
ADDRESS = '0.0.0.0'
NETMASK = '0.0.0.0'
GATEWAY = '0.0.0.0'
PRIMARY = '8.8.4.4'
SECONDARY = '8.8.8.8'
def initialize_Network():
	# These settings are read from the /etc/network configuration.  On factory
	# resets, the network can (optionally) be reset as well.
	# (see Cme/ref/interfaces_static; deploys to /etc/network/interfaces_static)
	from .IpUtils import mac, dhcp, address, netmask, gateway

	global MAC
	global DHCP
	global ADDRESS
	global NETMASK
	global GATEWAY

	MAC = mac() # just read the MAC address from network interface
	DHCP = dhcp() # False
	ADDRESS = address() # 192.168.1.30
	NETMASK = netmask() # 255.255.255.0
	GATEWAY = gateway() # 192.168.1.1
