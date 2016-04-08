from Components.Network import iNetwork
from OTTLocale import _

import socket
import threading
import urllib
import urllib2

from xml.dom import minidom

MAX_THREAD_COUNT = 40

class ScanHost(threading.Thread):
	def __init__(self, ipaddress, port):
		threading.Thread.__init__(self)
		self.ipaddress = ipaddress
		self.port = port
		self.isopen = False

	def run(self):
		serverip  = socket.gethostbyname(self.ipaddress)

		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(10)
			result = sock.connect_ex((serverip, self.port))
			sock.close()
			self.isopen = result == 0

		except socket.gaierror:
			self.isopen = False
			
		except socket.error:
			self.isopen = False

class OTTScan:
	def __init__(self, session):
		self.session = session
		
	def scan(self):
		print "[OTTClient] network scan started"
		devices = []
		for key in iNetwork.ifaces:
			if iNetwork.ifaces[key]['up']:
				devices += self.scanNetwork(iNetwork.ifaces[key]['ip'], iNetwork.ifaces[key]['netmask'])
				
		print "[OTTClient] network scan completed. Found " + str(len(devices)) + " devices"
		return devices
		
	def ipRange(self, start_ip, end_ip):
		temp = start_ip
		ip_range = []

		ip_range.append(".".join(map(str, start_ip)))
		while temp != end_ip:
			start_ip[3] += 1
			for i in (3, 2, 1):
				if temp[i] == 256:
					temp[i] = 0
					temp[i-1] += 1
			ip_range.append(".".join(map(str, temp)))

		return ip_range

	def getNetSize(self, netmask):
		binary_str = ''
		for octet in netmask:
			binary_str += bin(int(octet))[2:].zfill(8)
		return len(binary_str.rstrip('0'))
		
	def getBoxName(self, ipaddress):
		try:
			httprequest = urllib2.urlopen('http://' + ipaddress + '/web/about', timeout = 5)
			xmldoc = minidom.parseString(httprequest.read())
			return xmldoc.getElementsByTagName('e2model')[0].firstChild.nodeValue
		except Exception:
			pass
		return None
	
	def scanNetwork(self, ipaddress, subnet):
		print "[OTTClient] scan interface with ip address", ipaddress, "and subnet", subnet
		cidr = self.getNetSize(subnet)

		startip = []
		for i in range(4):
			startip.append(int(ipaddress[i]) & int(subnet[i]))
	
		endip = list(startip)
		brange = 32 - cidr
		for i in range(brange):
			endip[3 - i/8] = endip[3 - i/8] + (1 << (i % 8))

		if startip[0] == 0:	# if start with 0, we suppose the interface is not properly configured
			print "[OTTClient] your start ip address seem invalid. Skip interface scan."
			return []

		startip[3] += 1
		endip[3] -= 1

		print "[OTTClient] scan from ip", startip, "to", endip
		
		threads = []
		threads_completed = []
		for iptoscan in self.ipRange(startip, endip):
			if len(threads) >= MAX_THREAD_COUNT:
				scanhost = threads.pop(0)
				scanhost.join()
				threads_completed.append(scanhost)
				
			scanhost = ScanHost(iptoscan, 80)
			scanhost.start()
			threads.append(scanhost)
		
		for scanhost in threads:
			scanhost.join()
			threads_completed.append(scanhost)
			
		devices = []
		for scanhost in threads_completed:
			if scanhost.isopen:
				print "[OTTClient] device with ip " + scanhost.ipaddress + " listen on port 80, check if it's enigma2"
				boxname = self.getBoxName(scanhost.ipaddress)
				if boxname:
					print "[OTTClient] found " + boxname + " on ip " + scanhost.ipaddress
					devices.append((str(boxname), scanhost.ipaddress))
				else:
					print "[OTTClient] no enigma2 found. Skip host"
		return devices
