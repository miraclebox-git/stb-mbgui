from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import NumberActionMap, ActionMap
from Components.config import *
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists, SCOPE_PLUGINS
from Components.PluginList import * 
from Components.Sources.List import List 
from Plugins.Plugin import PluginDescriptor 
from Components.PluginComponent import plugins 
from Screens.Setup import Setup
from Screens.HarddiskSetup import HarddiskSelection, HarddiskFsckSelection, HarddiskConvertExt4Selection
from Screens.Console import Console 
import os
from enigma import eEnv

plugin_path_networkbrowser = eEnv.resolve("${libdir}/enigma2/python/Plugins/SystemPlugins/NetworkBrowser")

class MBTools(Screen):
	skin = '''<screen name="MBTools" title="MBTools" position="center,center" size="620,550" >
			  <widget source="list" render="Listbox" position="10,0" size="610,540" scrollbarMode="showOnDemand" >
				  <convert type="TemplatedMultiContent">
				  {"template": [
				  MultiContentEntryText(pos = (90, 0), size = (510, 30), font=0, text = 0),
				  MultiContentEntryPixmapAlphaTest(pos = (10, 10), size = (80, 80), png = 1),
				  MultiContentEntryText(pos = (90, 30), size = (510, 30), font=1, flags = RT_VALIGN_TOP, text = 3),
				  ],
				  "fonts": [gFont("Regular", 24),gFont("Regular", 16)],
				  "itemHeight": 60
				  }
				  </convert>
			  </widget>
		  </screen>'''
		  
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self["list"] = List(self.list)
		
		self.updateList()
		self["actions"] = ActionMap(["WizardActions",
		"ColorActions"], {"ok": self.KeyOk,
		"back": self.close})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		self.sel = self.sel[2]
		if (self.sel == 1):
			try:
				from Plugins.SystemPlugins.DeviceManager.plugin import DeviceManager
				self.session.open(DeviceManager)
			except:
				#from Screens.Setup import Setup, getSetupTitle
				#self.openSetup("harddisk")
				self.session.open(HarddiskSelection)
		elif (self.sel == 2):
			self.session.open(FullBackup)
		elif (self.sel == 3):
			from Plugins.Extensions.MBPanel.filemanager import *
			self.session.open(FilebrowserScreen)
		elif (self.sel == 4):
			from Screens.NetworkSetup import NetworkMiniDLNA
			self.session.open(NetworkMiniDLNA)
		elif (self.sel == 5):
			from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
			self.session.open(NetworkBrowser, None, plugin_path_networkbrowser)
		elif (self.sel == 6):
			from Screens.CronTimer import CronTimers
			self.session.open(CronTimers)
		elif (self.sel == 7):
			from Plugins.SystemPlugins.SetPasswd.plugin import ChangePasswdScreen
			self.session.open(ChangePasswdScreen)
		else:
			self.noYet()
	
	def openSetup(self, dialog):
		self.session.openWithCallback(self.menuClosed, Setup, dialog)

	def menuClosed(self, *res):
		pass
	      
	def noYet(self):
		nobox = self.session.open(MessageBox, _("Function Not Yet Available"), MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))

	def updateList(self):
		self.list = []
		mypath = resolveFilename(SCOPE_PLUGINS)
		mypath = mypath + "Extensions/MBPanel/"

		mypixmap = (mypath + "icons/icon_devices.png")
		png = LoadPixmap(mypixmap)
		name = (_("Device Manager"))
		desc = (_("Manage Your Devices"))
		idx = 1
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_backup.png")
		png = LoadPixmap(mypixmap)
		name = (_("Backup Manager"))
		desc = (_("Backup Your Image for future flashing"))
		idx = 2
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_filemanager.png")
		png = LoadPixmap(mypixmap)
		name = (_("File Manager"))
		desc = (_("Manage your files"))
		idx = 3
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_dlnaserver.png")
		png = LoadPixmap(mypixmap)
		name = (_("DLNA Server"))
		desc = (_("Share Your files with Samsung TV"))
		idx = 4
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_netbrowser.png")
		png = LoadPixmap(mypixmap)
		name = (_("Network Browser"))
		desc = (_("Browse Your network shares"))
		idx = 5
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = (mypath + "icons/icon_crontimers.png")
		png = LoadPixmap(mypixmap)
		name = (_("Cron Timers"))
		desc = (_("Schedule Your functions"))
		idx = 6
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_setpassword.png")
		png = LoadPixmap(mypixmap)
		name = (_("Set Password"))
		desc = (_("Change Your box acces password"))
		idx = 7
		res = (name,png,idx,desc)
		self.list.append(res)
		
		self["list"].list = self.list
		
		

class FullBackup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		  
		self.list = []
		self["config"] = MenuList(self.list)
		self['key_red'] = Label(_('Full Backup'))
		self['key_green'] = Label(_('Cancel'))
		self['label1'] = Label(_('Choose backup location'))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.saveMysets, 'green': self.close, 'back': self.close})

		self.deviceok = True
		
		self.updateList()
		
	def updateList(self):
		(mycf, myusb, myusb2, myusb3, mysd, myhdd) = ('', '', '', '', '', '',)
		myoptions = []
		if fileExists('/proc/mounts'):
			fileExists('/proc/mounts')
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if line.find('/media/cf') != -1:
					mycf = '/media/cf/'
					continue
				if line.find('/media/usb') != -1:
					myusb = '/media/usb/'
					continue
				if line.find('/media/usb2') != -1:
					myusb2 = '/media/usb2/'
					continue
				if line.find('/media/usb3') != -1:
					myusb3 = '/media/usb3/'
					continue				      
				if line.find('/media/card') != -1:
					mysd = '/media/card/'
					continue
				if line.find('/hdd') != -1:
					myhdd = '/media/hdd/'
					continue
			f.close()
		else:
			fileExists('/proc/mounts')
		if mycf:
			mycf
			self.list.append((_("CF card mounted in:\t") +mycf, mycf))
		else:
			mycf
		if myusb:
			myusb
			self.list.append((_("USB mounted in:\t") +myusb, myusb))
		else:
			myusb
		if myusb2:
			myusb2
			self.list.append((_("USB 2 mounted in:\t") +myusb2, myusb2))
		else:
			myusb2
		if myusb3:
			myusb3
			self.list.append((_("USB 3 mounted in:\t") +myusb3, myusb3))
		else:
			myusb3
		if mysd:
			mysd
			self.list.append((_("SD card mounted in:\t") +mysd, mysd))
		else:
			mysd
		if myhdd:
			myhdd
			self.list.append((_("HDD mounted in:\t") +myhdd, myhdd))
		else:
			myhdd

		self["config"].setList(self.list)
		print len(self.list)
		if len(self.list) < 1:
			self['label1'].setText(_('Sorry no device found to store backup. Please check your media in device manager.'))
			self.deviceok = False

	def myclose(self):
		self.close()

	def saveMysets(self):
		if self.deviceok == True:
			mysel = self['config'].getCurrent()
			mytitle = 'Miracle Full Backup on: ' + mysel[1]
			cmd = '/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/bin/full_backup.sh ' + mysel[1]
			self.session.open(Console, title=mytitle, cmdlist=[cmd], finishedCallback=self.myclose)
		else:
  			self.session.open(MessageBox, _('Sorry, there is not any connected devices in your Miraclebox.\nPlease connect HDD or USB to full backup Your Miracle Image!'), MessageBox.TYPE_INFO)
  			
  			
  			
class MBMedia(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["MBTools"]
		self.list = []
		self["list"] = List(self.list)
		
		self.updateList()
		self["actions"] = ActionMap(["WizardActions",
		"ColorActions"], {"ok": self.KeyOk,
		"back": self.close})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		self.sel = self.sel[2]
		if (self.sel == 1):
			from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
			self.session.open(MediaPlayer)
		elif (self.sel == 2):
			from Screens.MovieSelection import MovieSelection
			from Components.ServiceEventTracker import ServiceEventTracker  
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			self.session.open(MovieSelection, ref)
		elif (self.sel == 3):
			from Plugins.Extensions.IniMyTube.ui import MyTubePlayerMainScreen
			self.session.open(MyTubePlayerMainScreen, "/usr/lib/enigma2/python/Plugins/Extensions/IniMyTube")
		else:
			self.noYet()

	def noYet(self):
		nobox = self.session.open(MessageBox, _("Function Not Yet Available"), MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))

	def updateList(self):
		self.list = []
		mypath = resolveFilename(SCOPE_PLUGINS)
		mypath = mypath + "Extensions/MBPanel/"

		mypixmap = (mypath + "icons/icon_mediaplayer.png")
		png = LoadPixmap(mypixmap)
		name = (_("Media Player"))
		desc = (_("Play your Movies and Music"))
		idx = 1
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_recordings.png")
		png = LoadPixmap(mypixmap)
		name = (_("Recordings"))
		desc = (_("Play and watch your Recordings"))
		idx = 2
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_youtube.png")
		png = LoadPixmap(mypixmap)
		name = (_("YouTube"))
		desc = (_("Watch YouTube Clips"))
		idx = 3
		res = (name,png,idx,desc)
		self.list.append(res)

		self["list"].list = self.list
