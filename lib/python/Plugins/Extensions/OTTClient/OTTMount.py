from Components.Console import Console
from Components.config import config

import os

mountstate = False
mounthost = None

class OTTMount:
	def __init__(self, session):
		self.session = session
		self.console = Console()
		self.mountpoint = '/media/hdd'
		self.share = 'Harddisk'
		
	def automount(self):
		global mountstate
		global mounthost
		mountstate = False
		mounthost = None
		if config.ipboxclient.mounthdd.value:
			if self.isMountPoint(self.mountpoint):
				if not self.umount(self.mountpoint):
					print 'Cannot umount ' + self.mounpoint
					return
					
			if not self.mount(config.ipboxclient.host.value, self.share, self.mountpoint):
				print 'Cannot mount ' + config.ipboxclient.host.value + '/' + self.share + ' to ' + self.mountpoint
			else:
				mountstate = True
				mounthost = config.ipboxclient.host.value

	def remount(self):
		global mountstate
		global mounthost
		if mountstate and not config.ipboxclient.mounthdd.value:
			self.umount(self.mountpoint)
			mountstate = False
		elif not mountstate and config.ipboxclient.mounthdd.value:
			self.automount()
		elif mountstate and config.ipboxclient.mounthdd.value != mounthost:
			self.automount()
	
	def isMountPoint(self, path):
		return os.system('mountpoint ' + path) == 0
		
	def umount(self, path = None):
		return os.system('umount ' + path) == 0
		
	def mount(self, ip, share, path):
		try:
			os.makedirs(path)
		except Exception:
			pass
		return os.system('mount -t cifs -o rw,nolock,noatime,noserverino,iocharset=utf8,username=guest,password= //' + ip + '/' + share + ' ' + path) == 0

