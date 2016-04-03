from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSubsection, ConfigBoolean, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigIP
from Components.Network import iNetwork
from Components.Ipkg import IpkgComponent
from enigma import eDVBDB

import os
from xml.dom import minidom

config.misc.installwizard = ConfigSubsection()
config.misc.installwizard.hasnetwork = ConfigBoolean(default = False)
config.misc.installwizard.ipkgloaded = ConfigBoolean(default = False)
config.misc.installwizard.channellistdownloaded = ConfigBoolean(default = False)
config.misc.installwizard.upgradeimage = ConfigBoolean(default = False)

class InstallWizard(Screen, ConfigListScreen):

	STATE_UPDATE = 0
	STATE_CHOISE_CHANNELLIST = 1
	STATE_CHOISE_SOFTCAM = 2
	STATE_CHOISE_IMAGE_UPGRADE = 3
	
	def __init__(self, session, args = None):
		Screen.__init__(self, session)

		self.index = args
		self.list = []
		ConfigListScreen.__init__(self, self.list)

		if self.index == self.STATE_UPDATE:
			config.misc.installwizard.hasnetwork.value = False
			config.misc.installwizard.ipkgloaded.value = False
			modes = {0: " "}
			self.enabled = ConfigSelection(choices = modes, default = 0)
			self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getAdapterList()]
			is_found = False
			for x in self.adapters:
				if x[1] == 'eth0':
					if iNetwork.getAdapterAttribute(x[1], 'up'):
						self.ipConfigEntry = ConfigIP(default = iNetwork.getAdapterAttribute(x[1], "ip"))
						iNetwork.checkNetworkState(self.checkNetworkCB)
						if_found = True
					else:
						iNetwork.restartNetwork(self.checkNetworkLinkCB)
					break
				elif x[1] == 'wlan000':
					if iNetwork.getAdapterAttribute(x[1], 'up'):
						self.ipConfigEntry = ConfigIP(default = iNetwork.getAdapterAttribute(x[1], "ip"))
						iNetwork.checkNetworkState(self.checkNetworkCB)
						if_found = True
					else:
						iNetwork.restartNetwork(self.checkNetworkLinkCB)
					break
			if is_found is False:
				self.createMenu()
		elif self.index == self.STATE_CHOISE_CHANNELLIST:
			modes = {"yes": _(" "), "no": _(" ")}
			self.enabled = ConfigSelection(choices = modes, default = "yes")
			self.createMenu()
		elif self.index == self.STATE_CHOISE_IMAGE_UPGRADE:
			modes = {"yes": _(" "), "no": _(" ")}
			modes2 = {"yes": _(" "), "no": _(" ")}
			self.enabled = ConfigSelection(choices = modes, default = "yes")#ConfigYesNo(default = True)
			self.enabled2 = ConfigSelection(choices = modes2, default = "no")#ConfigYesNo(default = False)
			self.createMenu()

	def checkNetworkCB(self, data):
		if data < 3:
			config.misc.installwizard.hasnetwork.value = True
		self.createMenu()

	def checkNetworkLinkCB(self, retval):
		if retval:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self.createMenu()
	def getMenuFile(self, url):
		inputUrl = url
		xmlFile = os.popen((('wget -q ' + inputUrl) + ' -O-')).read()
		mdom = minidom.parseString(xmlFile)
		return mdom
      
	def createMenu(self):
		try:
			test = self.index
		except:
			return
		self.list = []
		if self.index == self.STATE_UPDATE:
			if config.misc.installwizard.hasnetwork.value:
				self.list.append(getConfigListEntry(_("Your internet connection is working (ip: %s)") % (self.ipConfigEntry.getText()), self.enabled))
			else:
				self.list.append(getConfigListEntry(_("Your receiver does not have an internet connection"), self.enabled))
		elif self.index == self.STATE_CHOISE_CHANNELLIST:
			self.yes = getConfigListEntry(_("No thanks. Go to Service Searching"), self.enabled)
			self.yes2 = getConfigListEntry(_("----------------------------------"), self.enabled)
			self.list.append(self.yes)
			self.list.append(self.yes2)
			self.url="http://miraclebox.se/official-feed/feeds.xml"
			mdom = self.getMenuFile(self.url)
			lista_emu = mdom.getElementsByTagName('item')
			for lista in lista_emu:
				url = lista.getAttribute("url")
				text = lista.getAttribute("text")
				modes1 = {str(url): " "}
				self.channellist = ConfigSelection(choices = modes1, default = str(url))
				self.list.append(getConfigListEntry(str(text),self.channellist))
		elif self.index == self.STATE_CHOISE_IMAGE_UPGRADE:
			self.yes = getConfigListEntry(_("Yes, please check for updates"), self.enabled)
			self.list.append(self.yes)
			self.no = getConfigListEntry(_("No, skip this step"), self.enabled2)
			self.list.append(self.no)
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		if self.index == 0:
			return
		ConfigListScreen.keyLeft(self)
		self.createMenu()

	def keyRight(self):
		if self.index == 0:
			return
		ConfigListScreen.keyRight(self)
		self.createMenu()

	def run(self):
		current = self["config"].getCurrent()
		if self.index == self.STATE_UPDATE:
			if config.misc.installwizard.hasnetwork.value:
				self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (updating packages)'), IpkgComponent.CMD_UPDATE)
		elif self.index == self.STATE_CHOISE_CHANNELLIST and current != self.yes:#self.enabled.value:
			self.fileUrl = self.url[0:-23] + current[1].value
			if (self.fileUrl.endswith(".zip")):
				cmd = (";opkg remove enigma2-plugin-settings-*;wget -q " + self.fileUrl + " -O /tmp/Addon.zip;cd /; unzip -o /tmp/Addon.zip -d /; rm /tmp/Addon.zip")
				self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (downloading channel list)'), IpkgComponent.CMD_REMOVE,  {'package': cmd})
		elif self.index == self.STATE_CHOISE_IMAGE_UPGRADE and current == self.yes:
			#self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (updating packages)'), IpkgComponent.CMD_UPDATE)
			#if config.misc.installwizard.hasnetwork.value:
				from Screens.SoftwareUpdate import UpdatePlugin
				self.session.open(UpdatePlugin)
		return

class InstallWizardIpkgUpdater(Screen):
	skin = """
	<screen position="c-300,c-25" size="600,50" title=" ">
		<widget source="statusbar" render="Label" position="10,5" zPosition="10" size="e-10,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
	</screen>"""

	def __init__(self, session, index, info, cmd, pkg = None):
		self.skin = InstallWizardIpkgUpdater.skin
		Screen.__init__(self, session)

		self["statusbar"] = StaticText(info)

		self.pkg = pkg
		self.index = index
		self.state = 0
		
		self.ipkg = IpkgComponent()
		self.ipkg.addCallback(self.ipkgCallback)

		if self.index == InstallWizard.STATE_CHOISE_CHANNELLIST:
			self.ipkg.startCmd(cmd, {'package': 'enigma2-plugin-settings-*'})
		else:
			self.ipkg.startCmd(cmd, pkg)

	def ipkgCallback(self, event, param):
		if event == IpkgComponent.EVENT_DONE:
			if self.index == InstallWizard.STATE_UPDATE:
				config.misc.installwizard.ipkgloaded.value = True
			elif self.index == InstallWizard.STATE_CHOISE_CHANNELLIST:
				if self.state == 0:
					self.ipkg.startCmd(IpkgComponent.CMD_INSTALL, self.pkg)
					self.state = 1
					return
				else:
					config.misc.installwizard.channellistdownloaded.value = True
					eDVBDB.getInstance().reloadBouquets()
					eDVBDB.getInstance().reloadServicelist()
			self.close()
