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
import os

VER="v1.5 - 18.04.2016"

class MBMainMenu(Screen):
	skin = '''<screen name="MBMainMenu" title="MB Panel" position="center,center" size="620,550" >
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
		global VER
		self["list"] = List(self.list)
		self["version"] = Label(_(VER))
		
		self.updateList()
		self["actions"] = ActionMap(["WizardActions",
		"ColorActions"], {"ok": self.KeyOk,
		"back": self.close})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		self.sel = self.sel[2]
		if (self.sel == 1):
			from Plugins.Extensions.MBPanel.softcam import MBSoftCam
			self.session.open(MBSoftCam)
		elif (self.sel == 2):
			self.session.open(Setup, "epgsettings")
		elif (self.sel == 3):
			from Plugins.Extensions.MBPanel.tools import MBTools
			self.session.open(MBTools)
		elif (self.sel == 4):
			#from Plugins.SystemPlugins.SoftwareManager.plugin import PluginManager
			#self.session.open(PluginManager, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")
			from Plugins.Extensions.MBPanel.installer import MBPanelAddons
			self.session.open(MBPanelAddons)
		elif (self.sel == 5):
			from Screens.PluginBrowser import PluginBrowser
			self.session.open(PluginBrowser)
		elif (self.sel == 6):
			from Screens.NetworkSetup import NetworkAdapterSelection
			self.session.open(NetworkAdapterSelection)
		elif (self.sel == 7):
			from Plugins.Extensions.MBPanel.tools import MBMedia
			self.session.open(MBMedia)
		elif (self.sel == 8):
			from Plugins.Extensions.MBPanel.weather import MBMeteoMain
			self.session.open(MBMeteoMain)
		else:
			self.noYet()

	def noYet(self):
		nobox = self.session.open(MessageBox, _("Function Not Yet Available"), MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))

	def updateList(self):
		self.list = []
		mypath = resolveFilename(SCOPE_PLUGINS)
		mypath = mypath + "Extensions/MBPanel/"

		mypixmap = (mypath + "icons/icon_softcam.png")
		png = LoadPixmap(mypixmap)
		name = (_("Softcam Panel"))
		desc = (_("Manage Your Softcams"))
		idx = 1
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_epg.png")
		png = LoadPixmap(mypixmap)
		name = (_("EPG Settings"))
		desc = (_("Setting for EPG and CrossEPG"))
		idx = 2
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = (mypath + "icons/icon_tools.png")
		png = LoadPixmap(mypixmap)
		name = (_("Tools"))
		desc = (_("Device Manager, Backup Manager"))
		idx = 3
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = (mypath + "icons/icon_addons.png")
		png = LoadPixmap(mypixmap)
		name = (_("Addons"))
		desc = (_("Manage and Download Addons"))
		idx = 4
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = (mypath + "icons/icon_plugins.png")
		png = LoadPixmap(mypixmap)
		name = (_("Plugins"))
		desc = (_("Manage and Download Plug-ins"))
		idx = 5
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = (mypath + "icons/icon_network.png")
		png = LoadPixmap(mypixmap)
		name = (_("Network"))
		desc = (_("Check Network Settings and Info"))
		idx = 6
		res = (name,png,idx,desc)
		self.list.append(res)

		mypixmap = (mypath + "icons/icon_media.png")
		png = LoadPixmap(mypixmap)
		name = (_("Media"))
		desc = (_("Watch your movies and recordings"))
		idx = 7
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = (mypath + "icons/icon_weather.png")
		png = LoadPixmap(mypixmap)
		name = (_("Weather"))
		desc = (_("Weather informations for your location"))
		idx = 8
		res = (name,png,idx,desc)
		#self.list.append(res)

		self["list"].list = self.list

def main(session, **kwargs):
	session.open(MBMainMenu)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Miracle Panel"), main, "miraclebox_panel", 1)]
	return []
	
from Plugins.Plugin import PluginDescriptor
def Plugins(**kwargs):
	l = []
	l.append(PluginDescriptor(name=_("Miracle Panel"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart=False, fnc=main))
	l.append(PluginDescriptor(name=_("Miracle Panel"), where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=menu))
	return l
      