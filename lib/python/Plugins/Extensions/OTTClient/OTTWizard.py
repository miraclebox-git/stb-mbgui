from Screens.Wizard import Wizard
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Sources.Boolean import Boolean
from Components.config import config

from Tools import Directories

from OTTDownloader import OTTDownloader
from OTTScan import OTTScan
from OTTMount import OTTMount
from OTTLocale import _

from enigma import eTimer

class OTTWizard(Wizard):

	skin = """
		<screen position="0,0" size="720,576" flags="wfNoBorder" >
			<widget name="text"
					position="153,40"
					size="340,300"
					font="Regular;22" />
					
			<widget source="list"
					render="Listbox"
					position="53,340"
					size="440,180"
					scrollbarMode="showOnDemand" >
					
				<convert type="StringList" />
				
			</widget>
			
			<widget name="config"
					position="53,340"
					zPosition="1"
					size="440,180"
					transparent="1"
					scrollbarMode="showOnDemand" />
					
			<ePixmap pixmap="skin_default/buttons/button_red.png"
					 position="40,225"
					 zPosition="0"
					 size="15,16"
					 transparent="1"
					 alphatest="on" />
					 
			<widget name="languagetext"
					position="55,225"
					size="95,30"
					font="Regular;18" />
					
			<widget name="wizard"
					pixmap="skin_default/wizard.png"
					position="40,50"
					zPosition="10"
					size="110,174"
					alphatest="on" />
					
			<widget name="rc"
					pixmaps="skin_default/rc0.png,skin_default/rc1.png,skin_default/rc2.png"
					position="500,50"
					zPosition="10"
					size="154,500"
					alphatest="on" />
					
			<widget name="arrowdown"
					pixmap="skin_default/arrowdown.png"
					position="-100,-100"
					zPosition="11"
					size="37,70"
					alphatest="on" />
					
			<widget name="arrowdown2"
					pixmap="skin_default/arrowdown.png"
					position="-100,-100"
					zPosition="11"
					size="37,70"
					alphatest="on" />
					
			<widget name="arrowup"
					pixmap="skin_default/arrowup.png"
					position="-100,-100"
					zPosition="11"
					size="37,70"
					alphatest="on" />
					
			<widget name="arrowup2"
					pixmap="skin_default/arrowup.png"
					position="-100,-100"
					zPosition="11"
					size="37,70"
					alphatest="on" />
					
			<widget source="VKeyIcon"
					render="Pixmap"
					pixmap="skin_default/buttons/key_text.png"
					position="40,260"
					zPosition="0"
					size="35,25"
					transparent="1"
					alphatest="on" >
					
				<convert type="ConditionalShowHide" />
				
			</widget>
			
			<widget name="HelpWindow"
					pixmap="skin_default/buttons/key_text.png"
					position="310,435"
					zPosition="1"
					size="1,1"
					transparent="1"
					alphatest="on" />
					
		</screen>"""

	def __init__(self, session):
		self.xmlfile = Directories.resolveFilename(Directories.SCOPE_PLUGINS, "Extensions/OTTClient/ottwizard.xml")

		Wizard.__init__(self, session)

		self.setTitle(_('IPTV Client'))

		self.skinName = ["OTTWizard", "NetworkWizard"]
		self["wizard"] = Pixmap()
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["VKeyIcon"] = Boolean(False)

		if config.misc.iptvmode.value in ('normal'):
			self.close()

	def getTranslation(self, text):
		return _(text)

	def scan(self):
		self.timer = eTimer()
		self.timer.callback.append(self.doscan)
		self.timer.start(100)

	def doscan(self):
		self.timer.stop()
		scanner = OTTScan(self.session)
		self.scanresults = scanner.scan()
		if self.scanresults and len(self.scanresults) > 0:
			self.currStep = self.getStepWithID('choose')
		else:
			self.currStep = self.getStepWithID('nodevices')
		self.currStep += 1
		self.updateValues()

	def getScanList(self):
		devices = []
		for result in self.scanresults:
			devices.append((result[0] + ' (' + result[1] + ')', result[1]))
		
		devices.append((_('Cancel'), 'cancel'))
		return devices

	def selectionMade(self, result):
		selecteddevice = None
		if result != 'cancel':
			for device in self.scanresults:
				if device[1] == result:
					selecteddevice = device
		if selecteddevice:
			config.ipboxclient.host.value = selecteddevice[1]
			config.ipboxclient.host.save()
			config.ipboxclient.port.value = 80
			config.ipboxclient.port.save()
			config.ipboxclient.streamport.value = 8001
			config.ipboxclient.streamport.save()
			config.ipboxclient.auth.value = False
			config.ipboxclient.auth.save()
			config.ipboxclient.mounthdd.value = True
			config.ipboxclient.mounthdd.save()
			config.ipboxclient.firstconf.value = True
			config.ipboxclient.firstconf.save()
			
			mount = OTTMount(self.session)
			mount.remount()

			self.currStep = self.getStepWithID('download')
		else:
			self.currStep = self.getStepWithID('welcome')

	def download(self):
		self.timer = eTimer()
		self.timer.callback.append(self.dodownload)
		self.timer.start(100)
		
	def dodownload(self):
		self.timer.stop()
		downloader = OTTDownloader(self.session)
		try:
			downloader.download()
			self.currStep = self.getStepWithID('end')
		except Exception, e:
			print e
			self.currStep = self.getStepWithID('nodownload')
		self.currStep += 1
		self.updateValues()

