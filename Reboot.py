import os, subprocess, time, logging

from .ClockUtils import ntp_servers
from .IpUtils import set_dhcp, write_network_addresses

from . import is_a_cme, is_a_docker, docker_run, Config

def restart(power_off=False, recovery_mode=False, factory_reset=False, logger=None):
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
	poweroff_file = Config.PATHS.POWEROFF_FILE

	delay = Config.RECOVERY.RESET_REBOOT_DELAY_SECONDS

	if factory_reset and settings_file and os.path.isfile(settings_file):
		try:
			print("[DEBUG] Reboot.py, 35: Remove settings file: {0}".format(settings_file))
			#os.remove(settings_file)
			if logger:
				logger.info("CME user settings file removed")
		except Exception as e:
			if logger:
				logger.error("CME failed to remove user settings file, {}".format(e))

		if is_a_cme():
			print("[DEBUG] Reboot.py, 44: Set DHCP False")
			#set_dhcp(False)
			if logger:
				logger.info("CME DHCP turned OFF - static addressing will be used")

			print("[DEBUG] Reboot.py, 49: Write default net addresses")
			#write_network_addresses({ 
			#	'address': '192.168.1.30', 
			#	'netmask': '255.255.255.0', 
			#	'gateway': '192.168.1.1',
			#	'primary': '8.8.4.4',
			#	'secondary': '8.8.8.8' 
			#})
			if logger:
				logger.info("CME network settings reset to factory defaults")

			print("[DEBUG] Reboot.py, 60: Set default NTP servers")
			#ntp_servers(['time.nist.gov'])
			if logger:
				logger.info("CME NTP servers set to factory defaults")

			ntp_enable = ['systemctl', 'enable', 'ntp']

			if is_a_docker():
				print("[DEBUG] Reboot.py, 68: Enable NTP")
				#docker_run(ntp_enable)
			else:
				print("[DEBUG] Reboot.py, 71: Enable NTP")
				#subprocess.call(ntp_enable)

			if logger:
				logger.info("CME NTP system enabled")
		
	if recovery_mode and not os.path.isfile(recovery_file):
		print("[DEBUG] Reboot.py, 78: Touching recovery file: {0}".format(recovery_file))
		open(recovery_file, 'w').close()
		if logger:
			logger.info("CME set to boot into recovery mode")
	
	elif os.path.isfile(recovery_file):
		print("[DEBUG] Reboot.py, 84: Removing existing recovery file: {0}".format(recovery_file))
		os.remove(recovery_file)

	if power_off:
		print("[DEBUG] Reboot.py, 88: Touching poweroff_file: {0}".format(poweroff_file))
		open(poweroff_file, 'w').close()

	_reboot(delay, logger)


def _reboot(delay=1, logger=None):

	# These commands will cause SIGTERM to be sent to all running processes.
	# The cleanup() function in Cme-init/__main__.py is a callback listening
	# for the SIGTERM signal and will clean up GPIO and optionally have the
	# power control MCU remove primary power.
	command = ['shutdown', '-r', 'now'] if not power_off else ['shutdown', '-h', 'now']
	message = 'rebooting' if not power_off else 'powering down'

	# log the message
	if logger:
		logger.info("CME {0} in {1} seconds.".format(message, delay))	

	# delay - mostly for GPIO cleanup
	time.sleep(delay)

	# reboot system
	if is_a_cme():

		if is_a_docker():
			docker_run(command) 
		else:
			print("[DEBUG] Reboot.py, 116: reboot/halt now")
			subprocess.call(command)

