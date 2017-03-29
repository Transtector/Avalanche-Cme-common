import os, subprocess, time, logging

from .ClockUtils import ntp_servers
from .IpUtils import set_dhcp, write_network_addresses

from . import is_a_cme, is_a_docker, docker_run

def restart(delay=5, recovery_mode=False, factory_reset=False, settings_file=None, recovery_file=None, logger=None):
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
	if factory_reset and settings_file:
		try:
			os.remove(setings_file)
			if logger:
				logger.info("CME user settings file removed")
		except:
			pass

		if is_a_cme():
			set_dhcp(False)
			if logger:
				logger.info("CME DHCP turned OFF - static addressing will be used")

			write_network_addresses({ 
				'address': '192.168.1.30', 
				'netmask': '255.255.255.0', 
				'gateway': '192.168.1.1',
				'primary': '8.8.4.4',
				'secondary': '8.8.8.8' 
			})
			if logger:
				logger.info("CME network settings reset to factory defaults")

			ntp_servers(['time.nist.gov'])
			if logger:
				logger.info("CME NTP servers set to factory defaults")

			ntp_enable = ['systemctl', 'enable', 'ntp']

			if is_a_docker():
				docker_run(ntp_enable)
			else:
				subprocess.call(ntp_enable)

			if logger:
				logger.info("CME NTP system enabled")
		
	if recovery_mode and not os.path.isfile(recovery_file):
		open(recovery_file, 'w').close()
		if logger:
			logger.info("CME set to boot into recovery mode")
	
	elif os.path.isfile(recovery_file):
		os.remove(recovery_file)

	_reboot(delay, logger)


def _reboot(delay=5, logger=None):
	# trigger a reboot
	if logger:
		logger.info("CME rebooting in {0} seconds.".format(delay))	
	
	time.sleep(delay)

	# reboot system
	if is_a_cme():

		if is_a_docker():
			docker_run(['shutdown', '-r', 'now'])
		else:
			subprocess.call(['shutdown', '-r', 'now'])

