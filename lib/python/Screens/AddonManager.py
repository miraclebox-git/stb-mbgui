from Screens.MessageBox import MessageBox
from Screens.PluginBrowser import *
from enigma import eDVBDB, loadPNG, eSize, ePoint, eSlider, eTimer, RT_HALIGN_RIGHT, fontRenderClass, eConsoleAppContainer, getDesktop
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Components.GUIComponent import *
from Components.HTMLComponent import *
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.config import *
from Components.ConfigList import *
from Components.FileList import * 
from Components.Sources.List import List 
from Components.Label import Label 
from Components.MenuList import MenuList 
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest 
from Components.Pixmap import Pixmap 
from Components.PluginComponent import plugins 
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap
import os
import sys
import traceback
import StringIO

from xml.dom import EMPTY_NAMESPACE 
import xml.dom.minidom 

from Plugins.Plugin import PluginDescriptor

fp = None

AddonsInternetViewer_Skin = """
		<screen name="AddonsInternetViewer" position="center,center" size="620,550" title="Miracle Management Addons - Internet Addons" >
			<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="800,4"/>
			<widget name="menu" position="10,60" size="610,420" scrollbarMode="showOnDemand"/>
			<widget name="status" position="30,10" size="400,25" font="Regular;21" valign="center" halign="center"/>
			<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,485" size="800,4"/>
			<ePixmap position="30,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="65,509" size="200,25" font="Regular;18"/>
			<ePixmap position="430,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_blue.png" transparent="1" alphatest="on" />
			<widget name="key_blue" position="470,509" size="200,25" font="Regular;20" />
		</screen>"""
		
AddonRemove_Skin = """
		<screen name="AddonRemove" position="center,center" size="620,550" title="Miracle Management Addons - Remove Addon" >
			<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,45" size="800,4"/>
			<widget name="remove" position="10,60" size="610,420" scrollbarMode="showOnDemand"/>
			<widget name="status" position="30,10" size="400,25" font="Regular;21" valign="center" halign="center"/>
			<ePixmap name="border" pixmap="skin_default/div-h.png" position="10,485" size="800,4"/>
			<ePixmap position="30,509" zPosition="0" size="35,25" pixmap="skin_default/buttons/button_red.png" transparent="1" alphatest="on" />
			<widget name="key_red" position="65,509" size="200,25" font="Regular;18"/>
		</screen>"""
		
class BoundFunction():
    __module__ = __name__

    def __init__(self, fnc, *args):
        self.fnc = fnc
        self.args = args

    def __call__(self):
        self.fnc(*self.args)

def createUnInstallFile(ipkgResult, menuName):
	if (not os.path.exists('/usr/uninstall/')):
		os.system('mkdir /usr/uninstall/')
	while 1:
		currentLine = ipkgResult.readline()
		if (currentLine == ''):
			break
		foundPacketNamePos = currentLine.find('Installing ')
		if (foundPacketNamePos is not -1):
			name = currentLine[(foundPacketNamePos + 11):]
			nextSpace = name.find(' (')
			name = name[:nextSpace]
			os.system(('mkdir /usr/uninstall/' + name))
			fp = open(((('/usr/uninstall/' + name) + '/' + name) ), 'w')
			fp.write(menuName)
			fp.close()
			return None
			
def AddonEntry(name, desc, author, version, size, info_txt, info_pic, function):
	res = [(name, function, info_txt, info_pic)]
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		res.append(MultiContentEntryText(pos=(0, 6), size=(800, 35), font=0, text=name))
		if (version != ''):
			res.append(MultiContentEntryText(pos=(292, 38), size=(298, 25), font=1, flags=RT_HALIGN_RIGHT, text=str(('Version: ' + version))))
		if (desc != ''):
			res.append(MultiContentEntryText(pos=(0, 38), size=(800, 25), font=1, text=str(('Desc: ' + desc))))
		if (author != ''):
			res.append(MultiContentEntryText(pos=(0, 54), size=(590, 25), font=1, text=str(('Author: ' + author))))
		if (size != ''):
			res.append(MultiContentEntryText(pos=(292, 54), size=(208, 25), font=1, flags=RT_HALIGN_RIGHT, text=str((('Size: ' + size) + 'kB'))))
	else:
		res.append(MultiContentEntryText(pos=(0, 6), size=(400, 20), font=0, text=name))
		if (version != ''):
			res.append(MultiContentEntryText(pos=(292, 28), size=(98, 15), font=1, flags=RT_HALIGN_RIGHT, text=str(('Version: ' + version))))
		if (desc != ''):
			res.append(MultiContentEntryText(pos=(0, 28), size=(500, 15), font=1, text=str(('Desc: ' + desc))))
		if (author != ''):
			res.append(MultiContentEntryText(pos=(0, 44), size=(390, 15), font=1, text=str(('Author: ' + author))))
		if (size != ''):
			res.append(MultiContentEntryText(pos=(292, 44), size=(108, 15), font=1, flags=RT_HALIGN_RIGHT, text=str((('Size: ' + size) + 'kB'))))
	return res

def AddonMenuEntry(name, desc, function):
	res = [(name, function)]
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		res.append(MultiContentEntryText(pos=(0, 5), size=(800, 35), font=0, text=name))
		if (desc != ''):
			res.append(MultiContentEntryText(pos=(0, 38), size=(800, 25), font=1, text=desc))  
	else:
		res.append(MultiContentEntryText(pos=(0, 5), size=(500, 20), font=0, text=name))
		if (desc != ''):
			res.append(MultiContentEntryText(pos=(0, 28), size=(500, 15), font=1, text=desc))
	return res

class AddonList(MenuList, HTMLComponent, GUIComponent):
	__module__ = __name__
	def __init__(self, list, enableWrapAround = False):
		GUIComponent.__init__(self)
		self.l = eListboxPythonMultiContent()
		self.list = list
		self.l.setList(list)
		screenwidth = getDesktop(0).size().width()
		if screenwidth and screenwidth == 1920:
			self.l.setFont(0, gFont('Regular', 32))
			self.l.setFont(1, gFont('Regular', 24))
			self.l.setItemHeight(80)  
		else:
			self.l.setFont(0, gFont('Regular', 20))
			self.l.setFont(1, gFont('Regular', 14))
			self.l.setItemHeight(50)
		self.onSelectionChanged = []
		self.enableWrapAround = enableWrapAround
		
		GUI_WIDGET = eListbox
		
	def postWidgetCreate(self, instance):
		instance.setContent(self.l)
		instance.selectionChanged.get().append(self.selectionChanged)
		if self.enableWrapAround:
			self.instance.setWrapAround(True)
				
	def selectionChanged(self):
		for f in self.onSelectionChanged:
			f()
			
			
class AddonsScrollLabel(ScrollLabel):
	    __module__ = __name__

	    def resizeAndSet(self, newText, height):
		s = self.instance.size()
		textSize = (s.width(), s.height())
		textSize = (textSize[0], (textSize[1] - height))
		self.instance.resize(eSize(*textSize))
		p = self.instance.position()
		pos = (p.x(), (p.y() + height))
		self.instance.move(ePoint(pos[0], pos[1]))
		self.long_text.resize(eSize(*textSize))
		self.long_text.move(ePoint(pos[0], pos[1]))
		s = self.long_text.size()
		lineheight = fontRenderClass.getInstance().getLineHeight(self.long_text.getFont())
		lines = int((s.height() / lineheight))
		self.pageHeight = int((lines * lineheight))
		self.instance.resize(eSize(s.width(), (self.pageHeight + int((lineheight / 6)))))
		self.scrollbar.move(ePoint((s.width() - 20), 0))
		self.scrollbar.resize(eSize(20, (self.pageHeight + int((lineheight / 6)))))
		self.scrollbar.setOrientation(eSlider.orVertical)
		self.scrollbar.setRange(0, 100)
		self.scrollbar.setBorderWidth(1)
		self.long_text.move(ePoint(0, 0))
		self.long_text.resize(eSize((s.width() - 30), (self.pageHeight * 16)))
		self.setText(newText)
		
class AddonsInternetViewer(Screen):
	__module__ = __name__
	ALLOW_SUSPEND = True
	STATE_IDLE = 0
	STATE_DOWNLOAD = 1
	STATE_INSTALL = 2
	def __init__(self, session, parent, childNode, url):
		Screen.__init__(self, session)
		self.skinName = "AddonsInternetViewer"
		self.skin = AddonsInternetViewer_Skin
		menuList = []
		self.multi = False
		self.url = url
		try:
			header = parent.getAttribute('text').encode('UTF-8')
			menuType = parent.getAttribute('type').encode('UTF-8')
			if (menuType == 'multi'):
				self.multi = True
			else:
				self.multi = False
			menuList = self.buildMenuTree(childNode)
		except:
			tracefp = StringIO.StringIO()
			traceback.print_exc(file=tracefp)
			message = tracefp.getvalue()
		if self.multi:
			self['menu'] = AddonList(menuList)
		else:
			self['menu'] = MenuList(menuList)
			
		self['actions'] = ActionMap(['ColorActions', 'OkCancelActions',
		  'MovieSelectionActions'], {'ok': self.pressOK,
		  'red': self.pressOK,
		  'cancel': self.closeNonRecursive,
		  'exit': self.closeRecursive})
		
		self['status'] = Label(_('Please, choose addon to install:'))
		self['key_red'] = Label(_('Download'))
		self.state = self.STATE_IDLE
		self.StateTimer = eTimer()
		self.StateTimer.stop()
		self.StateTimer.timeout.get().append(self.runInstallation)

	def runInstallation(self):
		if (self.state == self.STATE_DOWNLOAD):
			self.state = self.STATE_IDLE
			self.fileUrl = self.url[0:-23] + self.saved_url
			print self.fileUrl
			if os.path.exists('/tmp/Addon.ipk'):
				os.system('rm /tmp/Addon.ipk')
			if ((self.fileUrl.endswith(".tgz")) or (self.fileUrl.endswith(".tar.gz")) or (self.fileUrl.endswith(".tar.bz2"))):
				os.system((('wget -q ' + self.fileUrl) + ' -O /tmp/Addon.tgz'))
			elif (self.fileUrl.endswith(".zip")):
				os.system((('wget -q ' + self.fileUrl) + ' -O /tmp/Addon.zip'))
			else:
				os.system((('wget -q ' + self.fileUrl) + ' -O /tmp/Addon.ipk'))
			message = str(((_('Do You want to install') + ' ') + self.saved_item_name) + '?')
			if os.path.exists('/tmp/Addon.ipk'):
				installBox = self.session.openWithCallback(self.installIPK, MessageBox, _(message), MessageBox.TYPE_YESNO)
				installBox.setTitle(_('IPK Package Installation...'))
			elif os.path.exists('/tmp/Addon.tgz'):
				installBox = self.session.openWithCallback(self.installTGZ, MessageBox, _(message), MessageBox.TYPE_YESNO)
				installBox.setTitle(_('TGZ Package Installation...'))
			elif os.path.exists('/tmp/Addon.zip'):
				installBox = self.session.openWithCallback(self.installZIP, MessageBox, _(message), MessageBox.TYPE_YESNO)
				installBox.setTitle(_('ZIP Package Installation...'))
			else:
				errorBox = self.session.open(MessageBox, _('Failed to download an Addon...'), MessageBox.TYPE_ERROR)
				errorBox.setTitle(_('Failed...'))
			return None
		elif (self.state == self.STATE_INSTALL):
			if os.path.exists('/tmp/Addon.ipk'):
				resultFile = os.popen('ipkg -force-overwrite install /tmp/Addon.ipk ; rm /tmp/Addon.ipk')
				createUnInstallFile(resultFile, self.saved_item_name)
				infoBox = self.session.openWithCallback(self.rebootGUI, MessageBox, _("Addon installed sucessfully !\nTo get it on plugin list, You need to reload GUI. Would You like to do it right now ?"), MessageBox.TYPE_YESNO)
				infoBox.setTitle(_('Success...'))		
				self['status'].setText(_('Addon installed sucessfully !'))
				self.state = self.STATE_IDLE
				self.StateTimer.stop()
				return None
			elif os.path.exists('/tmp/Addon.tgz'):
				resultFile = os.popen('cd /; tar -xz -f /tmp/Addon.tgz ; rm /tmp/Addon.tgz')
				if fileExists('/tmp/restartgui'):
					infoBox = self.session.openWithCallback(self.rebootGUI, MessageBox, _("Addon installed sucessfully !\nTo get it on plugin list, You need to reload GUI. Would You like to do it right now ?"), MessageBox.TYPE_YESNO)
				else:
					infoBox = self.session.open(MessageBox, _('Addon installed sucessfully !'), MessageBox.TYPE_INFO, 5)
				infoBox.setTitle(_('Success...'))
				self['status'].setText(_('Addon installed sucessfully !'))
				self.state = self.STATE_IDLE
				self.StateTimer.stop()
			elif os.path.exists('/tmp/Addon.zip'):
				resultFile = os.popen('cd /; unzip -o /tmp/Addon.zip -d /; rm /tmp/Addon.zip')
				if fileExists('/tmp/restartgui'):
					infoBox = self.session.openWithCallback(self.rebootGUI, MessageBox, _("Addon installed sucessfully !\nTo get it on plugin list, You need to reload GUI. Would You like to do it right now ?"), MessageBox.TYPE_YESNO)
				else:
					infoBox = self.session.open(MessageBox, _('Addon installed sucessfully !'), MessageBox.TYPE_INFO, 5)
				infoBox.setTitle(_('Success...'))
				self['status'].setText(_('Addon installed sucessfully !'))
				self.state = self.STATE_IDLE
				self.StateTimer.stop()
		elif (self.state == self.STATE_IDLE):
			self['status'].setText(_('Please, choose an addon to install:'))
			self.StateTimer.stop()
			return None


	def rebootGUI(self, yesno):
		if yesno:
			self.session.open(TryQuitMainloop, 3)
		else:
			self['status'].setText(_('Remember to reload enigma2 !'))
		
		
	def downloadIPK(self, item, url, size_str):
		self.saved_item_name = item
		self.saved_url = url
		self.state = self.STATE_DOWNLOAD
		self['status'].setText(_('Downloading an addon... Please wait...'))
		self.StateTimer.start(200, True)
		
		
	def installIPK(self, yesno):
		if yesno:
			self.state = self.STATE_INSTALL
			self['status'].setText(_('Installing an addon... Please wait...'))
			self.StateTimer.start(200, True)
		else:
			infoBox = self.session.open(MessageBox, _('Installation aborted !'), MessageBox.TYPE_INFO)
			self.state = self.STATE_IDLE
			return None
			
	def installTGZ(self, yesno):
		if yesno:
			self.state = self.STATE_INSTALL
			self['status'].setText(_('Installing an addon... Please wait...'))
			self.StateTimer.start(200, True)
		else:
			infoBox = self.session.open(MessageBox, _('Installation aborted !'), MessageBox.TYPE_INFO)
			self.state = self.STATE_IDLE
			return None
			
	def installZIP(self, yesno):
		if yesno:
			self.state = self.STATE_INSTALL
			self['status'].setText(_('Installing an addon... Please wait...'))
			self.StateTimer.start(200, True)
		else:
			infoBox = self.session.open(MessageBox, _('Installation aborted !'), MessageBox.TYPE_INFO)
			self.state = self.STATE_IDLE
			return None
			
	def pressOK(self):
		try:
			if self.multi:
				selection = self['menu'].getCurrent()
				selection[0][1]()
			else:
				selection = self['menu'].l.getCurrentSelection()
				selection[1]()
		except:
			tracefp = StringIO.StringIO()
			traceback.print_exc(file=tracefp)
			message = tracefp.getvalue()
			
			
	def closeMenu(self, *res):
		if (len(res) and res[0]):
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
			self.close(True)
   
	def newMenu(self, destList, node):
		menuTitle = node.getAttribute('text').encode('UTF-8')
		menuDesc = node.getAttribute('desc').encode('UTF-8')
		a = BoundFunction(self.session.openWithCallback, self.closeMenu, AddonsInternetViewer, node, node.childNodes, self.url)
		if self.multi:
			destList.append(AddonMenuEntry(menuTitle, menuDesc, a))
		else:
			destList.append((menuTitle, a))
			
			
	def addItem(self, destList, node):
		item_text = node.getAttribute('text').encode('UTF-8')
		item_url = node.getAttribute('url').encode('UTF-8')
		item_desc = node.getAttribute('desc').encode('UTF-8')
		item_author = node.getAttribute('author').encode('UTF-8')
		item_version = node.getAttribute('version').encode('UTF-8')
		item_size = node.getAttribute('size').encode('UTF-8')
		info_txt = node.getAttribute('info_txt').encode('UTF-8')
		info_pic = node.getAttribute('info_pic').encode('UTF-8')
		a = BoundFunction(self.downloadIPK, item_text, item_url, item_size)
		if self.multi:
			destList.append(AddonEntry(item_text, item_desc, item_author, item_version, item_size, info_txt, info_pic, a))
		else:
			destList.append((item_text, a, info_txt, info_pic))
			
			
	def buildMenuTree(self, childNode):
		list = []
		for x in childNode:
			if (x.nodeType != xml.dom.minidom.Element.nodeType):
				pass
			elif (x.tagName == 'item'):
				self.addItem(list, x)
			elif (x.tagName == 'menu'):
				self.newMenu(list, x)
		return list


	def closeNonRecursive(self):
		self.eDVBDB = eDVBDB.getInstance()
		self.eDVBDB.reloadServicelist()
		self.eDVBDB.reloadBouquets()  
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.close(False)

	def closeRecursive(self):
		self.eDVBDB = eDVBDB.getInstance()
		self.eDVBDB.reloadServicelist()
		self.eDVBDB.reloadBouquets()  
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.close(True)

class AddonsViewer(AddonsInternetViewer):
	__module__ = __name__
	def getMenuFile(self, url):
		inputUrl = url
		xmlFile = os.popen((('wget -q ' + inputUrl) + ' -O-')).read()
		mdom = xml.dom.minidom.parseString(xmlFile)
		return mdom
	      
	def __init__(self, session):
		url="http://miraclebox.se/official-feed/feeds.xml"
		try:
			self.root_url = url
			mdom = self.getMenuFile(self.root_url)
			node = mdom.childNodes[0]
			child = mdom.childNodes[0].childNodes
			AddonsInternetViewer.__init__(self, session, mdom.childNodes[0], mdom.childNodes[0].childNodes, url)
		except:
			tracefp = StringIO.StringIO()
			traceback.print_exc(file=tracefp)
			message = tracefp.getvalue()
			AddonsInternetViewer.__init__(self, session, None, None, None)

class AddonRemove(Screen):
	__module__ = __name__
	def __init__(self, session):
		self.skin = AddonRemove_Skin
		Screen.__init__(self, session)
		
		self['status'] = Label(_('Please, choose addon to remove:'))
		self['key_red'] = Label(_('Remove'))
		
		self.mlist = []
		
		self['remove'] = MenuList(self.mlist)
		
		self['actions'] = ActionMap(['ColorActions', 'WizardActions',
		'DirectionActions'], {'ok': self.askRemoveIPK,
		'red' : self.askRemoveIPK,
		'back': self.closeAndReload}, -1)
		
		self.populateSL()
		
	def refr_sel(self):
		self['remove'].moveToIndex(1)
		self['remove'].moveToIndex(0)

	def closeAndReload(self):
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.close()
		
	def populateSL(self):
		self.mlist = []
		myscripts = os.listdir('/usr/uninstall')
		for fil in myscripts:
		    if ((fil.endswith('.del')) and (fil.startswith('Remove'))):
			fil2 = fil[6:-4]
			self.mlist.append(fil2)
		    elif ((fil.endswith('.del')) and not(fil.startswith('Remove'))):
			fil2 = fil[0:-4]
			self.mlist.append(fil2)
		self['remove'].setList(self.mlist)
	    
	def askRemoveIPK(self):
		try:
			ipkName = self['remove'].getCurrent()
			removeBox = self.session.openWithCallback(self.removeIPK, MessageBox, _((('Do really want to remove ' + ipkName) + '?')), MessageBox.TYPE_YESNO)
			removeBox.setTitle(_('Package Removing...'))
			return None
		except:
			return None

	def removeIPK(self, yesno):
		if yesno:
			mysel = self['remove'].getCurrent()
			mysel2 = (('/usr/uninstall/' + mysel) + '.del')
			if fileExists(mysel2):
				os.system('chmod 777 ' +mysel2)
				os.system(mysel2)
			else:
				mysel2 = (('/usr/uninstall/Remove' + mysel) + '.del')
				os.system('chmod 777 ' +mysel2)
				os.system(mysel2)
			infoBox = self.session.open(MessageBox, (_('Addon removed!')), MessageBox.TYPE_INFO)
			infoBox.setTitle(_(('Remove Package')))
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
			self.populateSL()
		else:
			infoBox = self.session.open(MessageBox, (_('Addon NOT removed!')), MessageBox.TYPE_INFO)
			infoBox.setTitle(_(('Remove Package')))
        