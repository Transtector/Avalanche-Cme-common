import os, subprocess, time, logging

from .ClockUtils import ntp_servers
from .IpUtils import set_dhcp, write_network_addresses

from . import is_a_cme, is_a_docker, docker_run, Config

def restart(recovery_mode=False, factory_reset=False, logger=None):
	''' Performs a reboot with optional configuration (including network and clock) reset.

		factory_reset simply removes the current user settings (typically found in /data/settings.json,
		but look at app.config['SETTINGS'] key to see where it might be).

		Network reset:
			1) Turn off DHCP network config
			1) Write default static addresses
			-- Network will reset to defaults after reboot

		NTP reset:
			1) Write default NTP servers
			2) Enable the ntp service
			-- NTP will reset to defaults after reboot

		recovery_mode prevents docker modules (Cme, Cme-hw) from starting and just launches the
		base API (cme) under the base OS.
	'''
	settings_file = Config.PATHS.SETTINGS
	recovery_file = Config.PATHS.RECOVERY_FILE

	delay = Config.RECOVERY.RESET_REBOOT_DELAY_SECONDS

	if factory_reset and settings_file and os.path.isfile(settings_file):
		try:
			print("[DEBUG] Reboot.py, 34: Remove settings file: {0}".format(settings_file))
			#os.remove(settings_file)
			if logger:
				logger.info("CME user settings file removed")
		except Exception as e:
			if logger:
				logger.error("CME failed to remove user settings file, {}".format(e))

		if is_a_cme():
			print("[DEBUG] Reboot.py, 43: Set DHCP False")
			#set_dhcp(False)
			if logger:
				logger.info("CME DHCP turned OFF - static addressing will be used")

			print("[DEBUG] Reboot.py, 48: Write default net addresses")
			#write_network_addresses({ 
			#	'address': '192.168.1.30', 
			#	'netmask': '255.255.255.0', 
			#	'gateway': '192.168.1.1',
			#	'primary': '8.8.4.4',
			#	'secondary': '8.8.8.8' 
			#})
			if logger:
				logger.info("CME network settings reset to factory defaults")

			print("[DEBUG] Reboot.py, 59: Set default NTP servers")
			#ntp_servers(['time.nist.gov'])
			if logger:
				logger.info("CME NTP servers set to factory defaults")

			ntp_enable = ['systemctl', 'enable', 'ntp']

			if is_a_docker():
				print("[DEBUG] Reboot.py, 67: Enable NTP")
				#docker_run(ntp_enable)
			else:
				print("[DEBUG] Reboot.py, 70: Enable NTP")
				#subprocess.call(ntp_enable)

			if logger:
				logger.info("CME NTP system enabled")
		
	if recovery_mode and not os.path.isfile(recovery_file):
		print("[DEBUG] Reboot.py, 77: Touching recovery file: {0}".format(recovery_file))
		#open(recovery_file, 'w').close()
		if logger:
			logger.info("CME set to boot into recovery mode")
	
	elif os.path.isfile(recovery_file):
		print("[DEBUG] Reboot.py, 83: Removing existing recovery file: {0}".format(recovery_file))
		#os.remove(recovery_file)

	_reboot(delay, logger)


def _reboot(delay=5, logger=None):
	# trigger a reboot
	if logger:
		logger.info("CME rebooting in {0} seconds.".format(delay))	
	
	time.sleep(delay)

	# reboot system
	if is_a_cme():

		if is_a_docker():
			print("[DEBUG] Reboot.py, 100: Rebooting now")
			#docker_run(['shutdown', '-r', 'now']) 
		else:
			print("[DEBUG] Reboot.py, 103: Rebooting now")
			#subprocess.call(['shutdown', '-r', 'now'])

