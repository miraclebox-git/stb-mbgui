from Screens.Screen import Screen
from enigma import iServiceInformation, eTimer
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Pixmap import MultiPixmap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigText, getConfigListEntry, ConfigSelection, NoSave
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists
from ServiceReference import ServiceReference
from os import system, listdir, chdir, getcwd, rename as os_rename
import socket
import time
 
from xml.dom import Node
from xml.dom import minidom
from Screens.Console import Console
import urllib

class MBSoftCam(Screen):
	skin = """
	<screen name="MBSoftCam" position="center,center" size="1000,720"  title="Miraclebox SoftCam Panel" flags="wfNoBorder">
        <ePixmap position="339,170" zPosition="3" size="60,40" pixmap="skin_default/buttons/key_ok.png" alphatest="blend" transparent="1" />
        <eLabel text="Miraclebox SoftCam Panel" position="80,30" size="800,38" font="Regular;34" halign="left" transparent="1"/> 
        <widget name="lab1" position="129,90" size="230,25" font="Regular;24" zPosition="2"  transparent="1"/>
        <widget name="list" position="75,126" size="340,38" zPosition="2"  transparent="1"/> 
        <widget name="lab2" position="139,172" size="190,24" font="Regular;20" halign="center" valign="center" zPosition="2" transparent="1"/>
    	<widget name="lab3" position="79,201" size="120,28" font="Regular;24" halign="left" zPosition="2" transparent="1"/> 
        <widget name="activecam" position="79,201" size="350,28" font="Regular;24" halign="left" zPosition="2" transparent="1"/>
        <widget name="Ilab1" position="79,257" size="350,28" font="Regular;24" zPosition="2" transparent="1"/>
        <widget name="Ilab2" position="79,290" size="350,28" font="Regular;24" zPosition="2" transparent="1"/>
        <widget name="Ilab3" position="79,315" size="350,28" font="Regular;24" zPosition="2" transparent="1"/>
        <widget name="Ilab4" position="79,345" size="350,28" font="Regular;24" zPosition="2" transparent="1"/>
        <widget name="Ecmtext" position="79,380" size="440,300" font="Regular;20" zPosition="2" transparent="1"/>
        <ePixmap position="145,650" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="on" zPosition="1" />
        <ePixmap position="430,650" size="140,40" pixmap="skin_default/buttons/yellow.png" alphatest="on" zPosition="1" />
        <ePixmap position="715,650" size="140,40" pixmap="skin_default/buttons/blue.png" alphatest="on" zPosition="1" />
	<widget name="key_red" position="145,650" zPosition="2" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="red" transparent="1" />		
	<widget name="key_yellow" position="430,650" zPosition="2" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="yellow" transparent="1" />
	<widget name="key_blue" position="715,650" zPosition="2" size="140,40" font="Regular;24" halign="center" valign="center" backgroundColor="blue" transparent="1" />
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		
		self["lab1"] = Label()
		self["lab2"] = Label(_("Set Default CAM"))
		self["lab3"] = Label(_("Active CAM"))
		self["Ilab1"] = Label()
		self["Ilab2"] = Label()
		self["Ilab3"] = Label()
		self["Ilab4"] = Label()
		self["activecam"] = Label()
		self["Ecmtext"] = ScrollLabel()

		self['key_red'] = Label(_('(Re)Start'))
		self['key_green'] = Label(_('Stop'))
		self['key_yellow'] = Label(_('Setup'))
		self['key_blue'] = Label(_('Download'))
        
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "CiSelectionActions"],
		{
			"ok": self.keyOk,
			"cancel": self.close,
			"green": self.keyGreen,
			"red": self.keyRed,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"left": self.keyLeft,
			"right": self.keyRight
		}, -1)
		
		self.emlist = []
		self.populate_List()
		self["list"] = MenuList(self.emlist)
		self["lab1"].setText(_("%d  CAM(s) Installed") % (len(self.emlist)))
		self.onShow.append(self.updateBP)
		
		self.timer = eTimer()
		self.timer.callback.append(self.downloadxmlpage)
		self.timer.start(100, 1)
		self.addon = 'emu'
		self.icount = 0
		self.downloading = False

	def populate_List(self):
		self.camnames = {}
		cams = listdir("/usr/camscript")
		for fil in cams:
			if fil.find('Ncam_') != -1:
				f = open("/usr/camscript/" + fil,'r')
				for line in f.readlines():
					line = line.strip()
					if line.find('CAMNAME=') != -1:
						name = line[9:-1]
						self.emlist.append(name)
						self.camnames[name] = "/usr/camscript/" + fil
				f.close()

	def updateBP(self):
		try:
			name = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			sinfo = self.session.nav.getCurrentService().info()
			provider = self.getServiceInfoValue(iServiceInformation.sProvider, sinfo)
			wide = self.getServiceInfoValue(iServiceInformation.sAspect, sinfo)
			width = sinfo and sinfo.getInfo(iServiceInformation.sVideoWidth) or -1
			height = sinfo and sinfo.getInfo(iServiceInformation.sVideoHeight) or -1	
			videosize = "%dx%d" %(width, height)
			aspect = "16:9" 
			if aspect in ( 1, 2, 5, 6, 9, 0xA, 0xD, 0xE ):
				aspect = "4:3"
		except:
			name = "N/A"; provider = "N/A"; aspect = "N/A"; videosize  = "N/A"	
		
		self["Ilab1"].setText(_("Name: ") + name)
		self["Ilab2"].setText(_("Provider: ") + provider)
		self["Ilab3"].setText(_("Aspect Ratio: ") + aspect)
		self["Ilab4"].setText(_("Videosize: ") + videosize)
	
		self.defaultcam = "/usr/camscript/Ncam_Cr.sh"
		if fileExists("/etc/BhCamConf"):
			f = open("/etc/BhCamConf",'r')
			for line in f.readlines():
   				parts = line.strip().split("|")
				if parts[0] == "deldefault":
					self.defaultcam = parts[1]
			f.close()
			
		self.defCamname =  "Card Reader"
		for c in self.camnames.keys():
			if self.camnames[c] == self.defaultcam:
				self.defCamname = c
		pos = 0
		for x in self.emlist:
			if x == self.defCamname:
				self["list"].moveToIndex(pos)
				break
			pos += 1

		mytext = "";
		if fileExists("/tmp/ecm.info"):
			f = open("/tmp/ecm.info",'r')
 			for line in f.readlines():
				mytext = mytext + line.strip() + "\n"
 			f.close()
		if len(mytext) < 5:
			mytext = "\n\n" + _("Ecm Info not available.")
				
		self["activecam"].setText(self.defCamname)
		self["Ecmtext"].setText(mytext)

	def keyLeft(self):
		self["list"].up()

	def keyRight(self):
		self["list"].down()
		
	def getServiceInfoValue(self, what, myserviceinfo):
		v = myserviceinfo.getInfo(what)
		if v == -2:
			v = myserviceinfo.getInfoString(what)
		elif v == -1:
			v = "N/A"
		return v


	def keyOk(self):
		self.sel = self["list"].getCurrent()
		self.newcam = self.camnames[self.sel]
		
		out = open("/etc/BhCamConf",'w')
		out.write("deldefault|" + self.newcam + "\n")
		out.close()
		
		out = open("/etc/CurrentBhCamName", "w")
		out.write(self.sel)
		out.close()
		cmd = "cp -f " + self.newcam + " /usr/bin/StartBhCam"
		system (cmd)
		cmd = "STOP_CAMD," + self.defaultcam
		self.sendtoBh_sock(cmd)
		self.keyOk2()
		#self.session.openWithCallback(self.keyOk2, startstopCam, self.defCamname, "stopping")
		
	def keyOk2(self):
		self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		cmd = "NEW_CAMD," + self.newcam
		self.sendtoBh_sock(cmd)
		oldcam = self.camnames[self.sel]
		self.session.openWithCallback(self.myclose, startstopCam, self.sel, "starting")
		
		
	def sendtoBh_sock(self, data):
		try:
			client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			client_socket.connect("/var/tmp/SoftCam.socket")
			client_socket.send(data)
			client_socket.close()
		except:
			system("start-stop-daemon -S -b -x /usr/bin/camsocker")
				
	def keyYellow(self):
		self.sel = self["list"].getCurrent()
		if self.sel == "Card Reader":
			from Screens.SCi import CardReader
			self.session.open(CardReader)
		else:
			from Screens.CCcamInfo import CCcamInfoMain
			self.session.open(CCcamInfoMain)

	def keyBlue(self):
		if self.downloading == True:
			#try:
			self.session.openWithCallback(self.populate_List, DownloadSoftCams, self.xmlparse, " Cams - BlackHole 2.x.x ")
			#except:
			#	self.close()
		#from Plugins.Extensions.MBPanel.addon_manager import MB_PrzegladaczAddonow
		#self.session.open(MB_PrzegladaczAddonow, "http://openmb.net/feeds/miraculous/custom/catalog_enigma2.xml")
		
	def keyGreen(self):
		self.sel = self["list"].getCurrent()
		self.newcam = self.camnames[self.sel]
		
		out = open("/etc/BhCamConf",'w')
		out.write("deldefault|" + self.newcam + "\n")
		out.close()
		
		out = open("/etc/CurrentBhCamName", "w")
		out.write(self.sel)
		out.close()
		cmd = "cp -f " + self.newcam + " /usr/bin/StartBhCam"
		system (cmd)
		cmd = "STOP_CAMD," + self.defaultcam
		self.sendtoBh_sock(cmd)
		self.session.openWithCallback(self.myclose, startstopCam, self.defCamname, "stopping")
		
	def keyRed(self):
		self.keyOk()

	def downloadxmlpage(self):
		from twisted.web.client import getPage
		url = 'http://panel.vuplus-images.co.uk/addonslist1.6.xml'
		getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

	def errorLoad(self, error):
		print str(error)

	def _gotPageLoad(self, data):
		self.xml = data
		try:
			if self.xml:
				xmlstr = minidom.parseString(self.xml)
				self.data = []
				self.names = []
				icount = 0
				list = []
				xmlparse = xmlstr
				self.xmlparse = xmlstr
				for plugins in xmlstr.getElementsByTagName('plugins'):
					self.names.append(plugins.getAttribute('cont').encode('utf8'))

				self.list = list
				self.downloading = True
			else:
				self.downloading = False
				return
		except:
			self.downloading = False

	def myclose(self):
		time.sleep(2)
		try:
			self.session.nav.playService(self.oldref)
		except:
			pass
		self.close()


class startstopCam(Screen):
	skin = '''<screen name="startstopCam" position="390,100" size="484,250" title="Miracle" flags="wfNoBorder">
		    <widget name="starting" position="0,0" size="484,250" zPosition="-1" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_1.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_2.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_3.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_4.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_5.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_6.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_7.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_8.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_9.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_10.png,/usr/lib/enigma2/python/Plugins/Extensions/MBPanel/icons/softcam/startcam_11.png" transparent="1" />
		    <widget name="text" position="20,20" size="460,60" zPosition="1" font="Regular;20" transparent="1" />
		  </screen>'''

	def __init__(self, session, title, what):
	    Screen.__init__(self, session)
	    msg = _('Please wait while ' + _(what) + '\n') + title + '...'
	    self['starting'] = MultiPixmap()
	    self['text'] = Label(msg)
	    self.activityTimer = eTimer()
	    self.activityTimer.timeout.get().append(self.updatepix)
	    self.onShow.append(self.startShow)
	    self.onClose.append(self.delTimer)

	def startShow(self):
		self.curpix = 0
		self.count = 0
		self['starting'].setPixmapNum(0)
		self.activityTimer.start(10)

	def updatepix(self):
		self.activityTimer.stop()
		if self.curpix > 9:
			self.curpix = 0
		if self.count > 24:
			self.curpix = 10
		self['starting'].setPixmapNum(self.curpix)
		if self.count == 35:
			self.hide()
			self.close()
		self.activityTimer.start(140)
		self.curpix += 1
		self.count += 1

	def delTimer(self):
		del self.activityTimer

class DownloadSoftCams(Screen):
	skin = '''<screen position="center,center" size="900,720" title="Download Miraculous SOFTCAMS" >
	<widget name="countrymenu" position="10,0" size="800,660" scrollbarMode="showOnDemand" />
	<ePixmap name="red" position="5,780" zPosition="4" size="540,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
	<widget name="key_red" position="5,660" zPosition="5" size="120,60" valign="center" halign="center" font="Regular;28" transparent="1" foregroundColor="red" shadowColor="black" shadowOffset="-1,-1" />
	</screen>'''

	def __init__(self, session, xmlparse, selection):
		Screen.__init__(self, session)
		self.xmlparse = xmlparse
		self.selection = selection
		list = []
		for plugins in self.xmlparse.getElementsByTagName('plugins'):
			if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
				for plugin in plugins.getElementsByTagName('plugin'):
					list.append(plugin.getAttribute('name').encode('utf8'))
			continue

		list.sort()
		self['countrymenu'] = MenuList(list)
		self['actions'] = ActionMap(['SetupActions'], {'cancel': self.close,
		'ok': self.selclicked}, -2)
		self['key_red'] = Button(_('Back'))

	def selclicked(self):
		try:
			selection_country = self['countrymenu'].getCurrent()
		except:
			return
		for plugins in self.xmlparse.getElementsByTagName('plugins'):
			if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
				for plugin in plugins.getElementsByTagName('plugin'):
					if plugin.getAttribute('name').encode('utf8') == selection_country:
						urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
						pluginname = plugin.getAttribute('name').encode('utf8')
						self.prombt(urlserver, pluginname)
						continue
			continue

	def prombt(self, com, dom):
		self.com = com
		self.dom = dom
		if self.selection == '{ Skins }':
			self.session.openWithCallback(self.callMyMsg, MessageBox, _('Do not install any skin unless you are sure it is compatible with your image.Are you sure?'), MessageBox.TYPE_YESNO)
		else:
			self.session.open(Console, _('Installing: %s') % dom, ['opkg install -force-overwrite %s' % com])

	def callMyMsg(self, result):
		if result:
			dom = self.dom
			com = self.com
			self.session.open(Console, _('Installing: %s') % dom, ['ipkg install -force-overwrite %s' % com])
