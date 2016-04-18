from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.config import config, ConfigText, configfile
from Components.Sources.List import List
from Components.Label import Label
from Components.PluginComponent import plugins
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, fileExists, pathExists, createDir
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from os import system, listdir, chdir, getcwd, remove as os_remove
from enigma import eDVBDB

class MBPanelAddons(Screen):
	skin = """
	<screen name="MBPanelAddons" position="0,0" size="541,720" flags="wfNoBorder" backgroundColor="transparent">
		<ePixmap pixmap="menu/bg_miracle_panel.png" position="0,0" size="540,720" alphatest="on" zPosition="-1" />
		<widget source="list" render="Listbox" position="10,107" size="503,533" selectionPixmap="MB-Common/buttons/FocusBar_H60x503.png" foregroundColor="window-fg" backgroundColor="window-bg" transparent="0" enableWrapAround="1" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
			{"template": [
			MultiContentEntryText(pos = (90, 5), size = (510, 30), flags = RT_VALIGN_CENTER,font=0, text = 0),
			MultiContentEntryPixmapAlphaTest(pos = (10, 0), size = (60, 60), png = 1),
			MultiContentEntryText(pos = (90, 33), size = (510, 30), font=1, flags = RT_VALIGN_TOP, text = 3),
			],
			"fonts": [gFont("Regular", 24),gFont("Regular", 16)],
			"itemHeight": 60
			}
			</convert>
		</widget>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = []
		self["list"] = List(self.list)
		self.updateList()
		
		if (not pathExists("/usr/uninstall")):
			createDir("/usr/uninstall")
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close,

		})
		
	def updateList(self):
		self.list = [ ]

		mypath = resolveFilename(SCOPE_PLUGINS)
		mypath = mypath + "Extensions/MBPanel/"
		
		mypixmap = mypath + "icons/icon_addons.png"
		png = LoadPixmap(mypixmap)
		name = _("Online Feeds Extensions")
		desc = (_("Download OE-A addons"))
		idx = 0
		res = (name,png,idx,desc)
		#self.list.append(res)
		
		mypixmap = mypath + "icons/icon_addons.png"
		png = LoadPixmap(mypixmap)
		name = _("Online Feeds all Packages")
		desc = (_("Download OE-A all packages"))
		idx = 1
		res = (name,png,idx,desc)
		#self.list.append(res)
		
		mypixmap = mypath + "icons/icon_addons.png"
		png = LoadPixmap(mypixmap)
		name = _("Online Miraculous image update")
		desc = (_("Perform on-line update"))
		idx = 2
		res = (name,png,idx,desc)
		#self.list.append(res)
		
		mypixmap = mypath + "icons/icon_addons.png"
		png = LoadPixmap(mypixmap)
		name = _("Manual Install Miraculous packages")
		desc = (_("Install manual addons tar.gz from /tmp"))
		idx = 3
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = mypath + "icons/icon_addons.png"
		png = LoadPixmap(mypixmap)
		name = _("Manual Install Ipk packages")
		desc = (_("Install manual addons ipk from /tmp"))
		idx = 4
		res = (name,png,idx,desc)
		self.list.append(res)
		
		mypixmap = mypath + "icons/icon_addons.png"
		png = LoadPixmap(mypixmap)
		name = _("Addons Uninstall Panel")
		desc = (_("Uninstall softcams and addons"))
		idx = 5
		res = (name,png,idx,desc)
		self.list.append(res)
		
		self["list"].list = self.list
		
	def KeyOk(self):
		
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[2]
			
		if self.sel == 0:
			from Plugins.SystemPlugins.SoftwareManager.plugin import PluginManager
			self.session.open(PluginManager, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")
		elif self.sel == 1:
			from Plugins.SystemPlugins.SoftwareManager.plugin import PacketManager
			self.session.open(PacketManager, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")
		elif self.sel == 2:
			self.session.openWithCallback(self.runUpgrade, MessageBox, _("Do you want to update your Miraculous image?")+"\n"+_("\nAfter pressing OK, please wait!"))
		elif self.sel == 3:
			self.checkPanel()
		elif self.sel == 4:
			self.checkPanel2()
		elif self.sel == 5:
			self.session.open(Nab_uninstPanel)
	
	
	def checkPanel(self):
		check = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.tgz') != -1:
				check = 1
		if check == 1:
			self.session.open(Nab_downPanel)
		else:
			mybox = self.session.open(MessageBox, _("Nothing to install.\nYou have to Upload a bh.tgz package in the /tmp directory before to install Addons"), MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
			
	def checkPanel2(self):
		check = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.ipk') != -1:
				check = 1
		if check == 1:
			self.session.open(Nab_downPanelIPK)
		else:
			mybox = self.session.open(MessageBox, _("Nothing to install.\nYou have to Upload an ipk package in the /tmp directory before to install Addons"), MessageBox.TYPE_INFO)
			mybox.setTitle(_("Info"))
			
			
	def runUpgrade(self, result):
		if result:
			from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
			self.session.open(UpdatePlugin, "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager")

class Nab_downPanel(Screen):
	skin = """
	<screen name="Nab_downPanel" position="0,0" size="541,720" flags="wfNoBorder" backgroundColor="transparent">
		<ePixmap pixmap="menu/bg_miracle_panel.png" position="0,0" size="540,720" alphatest="on" zPosition="-1" />
		<widget source="list" render="Listbox" position="10,107" size="503,533" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.flist = []
		idx = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.tgz') != -1:
				res = (fil, idx)
				self.flist.append(res)
				idx = idx + 1
		
		self["list"] = List(self.flist)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})

	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[0]
			message = _("Do you want to install the Addon:\n ") + self.sel + " ?"
			ybox = self.session.openWithCallback(self.installadd2, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Installation Confirm"))

	def installadd2(self, answer):
		if answer is True:
			dest = "/tmp/" + self.sel
			mydir = getcwd()
			chdir("/")
			cmd = "tar -xzf " + dest
			rc = system(cmd)
			chdir(mydir)
			cmd = "rm -f " + dest
			rc = system(cmd)
			if fileExists("/usr/sbin/nab_e2_restart.sh"):
				rc = system("rm -f /usr/sbin/nab_e2_restart.sh")
				mybox = self.session.openWithCallback(self.hrestEn, MessageBox, _("Gui will be now hard restarted to complete package installation.\nPress ok to continue"), MessageBox.TYPE_INFO)
				mybox.setTitle(_("Info"))
			else:
				mybox = self.session.open(MessageBox, _("Addon Succesfully Installed."), MessageBox.TYPE_INFO)
				mybox.setTitle(_("Info"))
				self.close()

	def hrestEn(self, answer):
		self.eDVBDB = eDVBDB.getInstance()
		self.eDVBDB.reloadServicelist()
		self.eDVBDB.reloadBouquets()
		self.session.open(TryQuitMainloop, 3)


class Nab_downPanelIPK(Screen):
	skin = """
	<screen name="Nab_downPanelIPK" position="0,0" size="541,720" flags="wfNoBorder" backgroundColor="transparent" title="MB Manual Install Ipk Packages">
		<ePixmap pixmap="menu/bg_miracle_panel.png" position="0,0" size="540,720" alphatest="on" zPosition="-1" />
		<widget source="list" render="Listbox" position="10,107" size="503,533" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
		<widget name="warntext" position="0,505" size="541,100" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.flist = []
		idx = 0
		pkgs = listdir("/tmp")
		for fil in pkgs:
			if fil.find('.ipk') != -1:
				res = (fil, idx)
				self.flist.append(res)
				idx = idx + 1
		
		self["warntext"] = Label(_("Here you can install any kind of ipk packages."))
		self["list"] = List(self.flist)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})

	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[0]
			message = _("Do you want to install the Addon:\n ") + self.sel + " ?"
			ybox = self.session.openWithCallback(self.installadd2, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Installation Confirm"))

	def installadd2(self, answer):
		if answer is True:
			dest = "/tmp/" + self.sel
			mydir = getcwd()
			chdir("/")
			cmd = "opkg install " + dest
			cmd2 = "rm -f " + dest
			self.session.open(Console, title=_("Ipk Package Installation"), cmdlist=[cmd, cmd2])
			chdir(mydir)

class Nab_uninstPanel(Screen):
	skin = """
	<screen name="Nab_uninstPanel" position="0,0" size="541,720" flags="wfNoBorder" backgroundColor="transparent" title="MB Uninstall Panel">
		<ePixmap pixmap="menu/bg_miracle_panel.png" position="0,0" size="540,720" alphatest="on" zPosition="-1" />
		<widget source="list" render="Listbox" position="10,107" size="503,533" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.flist = []
		idx = 0
		pkgs = listdir("/usr/uninstall")
		for fil in pkgs:
			if fil.find('.nab') != -1 or fil.find('.del') != -1:
				res = (fil, idx)
				self.flist.append(res)
				idx = idx + 1
		
		self["list"] = List(self.flist)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.KeyOk,
			"back": self.close

		})
		
	def KeyOk(self):
		self.sel = self["list"].getCurrent()
		if self.sel:
			self.sel = self.sel[0]
			message = _("Are you sure you want to Remove Package:\n ") + self.sel + "?"
			ybox = self.session.openWithCallback(self.uninstPack, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle("Uninstall Confirmation")
		
	
	def uninstPack(self, answer):
		if answer is True:
			orig = "/usr/uninstall/" + self.sel
			cmd = "sh " + orig
			rc = system(cmd)
			mybox = self.session.open(MessageBox, _("Addon Succesfully Removed."), MessageBox.TYPE_INFO)
			mybox.setTitle("Info")
			self.close()

class MBPanelScript(Screen):
	skin = """
	<screen position="80,100" size="560,410" title="MB Script Panel">
		<widget source="list" render="Listbox" position="10,10" size="540,300" scrollbarMode="showOnDemand" >
			<convert type="StringList" />
		</widget>
		<widget name="statuslab" position="10,320" size="540,30" font="Regular;16" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="210,360" size="140,40" alphatest="on" />
		<widget name="key_red" position="210,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["statuslab"] = Label("N/A")
		self["key_red"] = Label(_("Execute"))
		self.mlist = []
		self.populateSL()
		self["list"] = List(self.mlist)
		self["list"].onSelectionChanged.append(self.schanged)
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"ok": self.myGo,
			"back": self.close,
			"red": self.myGo
		})
		self.onLayoutFinish.append(self.refr_sel)
		
	def refr_sel(self):
		self["list"].index = 1
		self["list"].index = 0
		
	def populateSL(self):
		myscripts = listdir("/usr/script")
		for fil in myscripts:
			if fil.find('.sh') != -1:
				fil2 = fil[:-3]
				desc = "N/A"
				f = open("/usr/script/" + fil,'r')
				for line in f.readlines():
					if line.find('#DESCRIPTION=') != -1:
						line = line.strip()
						desc = line[13:]
				f.close()
				res = (fil2, desc)
				self.mlist.append(res)			

	def schanged(self):
		mysel = self["list"].getCurrent()
		if mysel:
			mytext = " " + mysel[1]
			self["statuslab"].setText(mytext)

			
	def myGo(self):
		mysel = self["list"].getCurrent()
		if mysel:
			mysel = mysel[0]
			mysel2 = "/usr/script/" + mysel + ".sh"
			mytitle = _("MB Script: ") + mysel
			self.session.open(Console, title=mytitle, cmdlist=[mysel2])

