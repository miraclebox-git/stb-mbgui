from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label
from Components.config import config, ConfigText, ConfigNumber, ConfigElement, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import ConfigList, ConfigListScreen
from Tools.Directories import fileExists

import math

config.plugins.smartcard = ConfigSubsection()
config.plugins.smartcard.boxidsci0 = ConfigNumber(default = "1122334455")
config.plugins.smartcard.boxidsci1 = ConfigNumber(default = "1122334455")

modes = {"empty" :"Empty", "viasat": "Viasat", "canalnordic": "Canal Digitaal Nordic", "boxer": "Boxer", "other": "Other"}

config.plugins.smartcard.sci0 = ConfigSelection(choices = modes, default = "viasat")
config.plugins.smartcard.sci1 = ConfigSelection(choices = modes, default = "canalnordic")
			
class CardReader(ConfigListScreen,Screen):
	skin = """
		<screen name="CardReader" position="center,center" size="570,350" title="Box Key" >
			  <widget name="config" position="10,10" size="550,130" scrollbarMode="showOnDemand" />
			  <widget name="help_text" position="10,150" size="550,220" scrollbarMode="showOnDemand" font="Regular;17"/>
			  <ePixmap name="key_red_png" pixmap="skin_default/buttons/button_red.png" position="10,320" size="140,40" alphatest="on" />
			  <widget name="key_red" position="40,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />
			  <ePixmap name="key_green_png" pixmap="skin_default/buttons/button_green.png" position="150,320" size="140,40" alphatest="on" />
			  <widget name="key_green" position="180,320" zPosition="1" size="200,40" font="Regular;20" halign="left" valign="top" backgroundColor="#9f1313" transparent="1" />
		</screen>"""
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)

		self.createConfig()

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "CiSelectionActions"],
		{
			"cancel": self.exit,
			"red": self.run,
			"green": self.exit
		}, -2)
		
		self["key_red"] = Label(_("Save"))
		self["key_green"] = Label(_("Cancel"))
		self["help_text"] = Label(_("Please enter your BoxID\n\n(9 or 10 digits - without 0)\n\nYou can find it on back side of Viasat box"))

	def createConfig(self):
		self.list = []
		
		self.list.append(getConfigListEntry(_("Down card-slot card:"), config.plugins.smartcard.sci0))
		if config.plugins.smartcard.sci0.value == "viasat":
			self.list.append(getConfigListEntry(_("\tBox Serial"), config.plugins.smartcard.boxidsci0))
		
		self.list.append(getConfigListEntry(_("Upper card-slot card:"), config.plugins.smartcard.sci1))
		if config.plugins.smartcard.sci1.value == "viasat":
			self.list.append(getConfigListEntry(_("\tBox Serial"), config.plugins.smartcard.boxidsci1))
		
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		
	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.handleKeysLeftAndRight()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.handleKeysLeftAndRight()

	def handleKeysLeftAndRight(self):
		self.createConfig()

	def run(self):
		fh = open("/var/tuxbox/config/oscam.server","w")
		
		reader1 = "[reader]\n"
		reader1 += "Label = Down\n"
		reader1 += "Protocol = internal\n"
		reader1 += "Detect = cd\n"
		reader1 += "Device = /dev/sci0\n"
		reader1 += "Group = 1\n"
		if config.plugins.smartcard.sci0.value == "viasat":
		  
			sci0_boxid_dec = str(config.plugins.smartcard.boxidsci0.value)
			if len(sci0_boxid_dec) < 9:
				msg = _("The entered number for down slot is wrong, it should be 9 or 10 digits")
				self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, 3)
				return
				
			sci0_boxid_dec_prepare = sci0_boxid_dec[0:9]
			sci0_boxid_hex = hex(int(sci0_boxid_dec_prepare))
			sci0_boxid_hex = str(sci0_boxid_hex)[2:]
			if len(sci0_boxid_hex) < 8:
				sci0_boxid_hex = "0" + sci0_boxid_hex
			else:
				sci0_boxid_hex
				
			print "Your converted BoxKey for down slot: ", sci0_boxid_hex.upper()
		
			reader1 += "EMMCache = 1,3,2\n"
			reader1 += "ident = 093E:000000\n"
			reader1 += "mhz = 357\n"
			reader1 += "cardmhz = 357\n"
			reader1 += "boxid = " + sci0_boxid_hex.upper() +"\n"
			reader1 += "ecmwhitelist = 093E:88,84,AA,A6,68,98\n"
		fh.write(reader1)

		fh.write("\n")
		fh.write("\n")
		
		reader2 = "[reader]\n"
		reader2 += "Label = Up\n"
		reader2 += "Protocol = internal\n"
		reader2 += "Detect = cd\n"
		reader2 += "Device = /dev/sci1\n"
		reader2 += "Group = 1\n"
		if config.plugins.smartcard.sci1.value == "viasat":
		  
			sci1_boxid_dec = str(config.plugins.smartcard.boxidsci1.value)
			if len(sci1_boxid_dec) < 9:
				msg = _("The entered number for upper slot is wrong, it should be 9 or 10 digits")
				self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, 3)
				return
				
			sci1_boxid_dec_prepare = sci1_boxid_dec[0:9]
			sci1_boxid_hex = hex(int(sci1_boxid_dec_prepare))
			sci1_boxid_hex = str(sci1_boxid_hex)[2:]
			if len(sci1_boxid_hex) < 8:
				sci1_boxid_hex = "0" + sci1_boxid_hex
			else:
				sci1_boxid_hex
				
			print "Your converted BoxKey for down slot: ", sci1_boxid_hex.upper()  
		  
			reader2 += "EMMCache = 1,3,2\n"
			reader2 += "ident = 093E:000000\n"
			reader2 += "mhz = 357\n"
			reader2 += "cardmhz = 357\n"
			reader2 += "boxid = "+ sci1_boxid_hex.upper() +"\n"
			reader2 += "ecmwhitelist = 093E:88,84,AA,A6,68,98\n"
		fh.write(reader2)
		fh.close()

		
		for x in self["config"].list:
		    x[1].save()   

		eConsoleAppContainer().execute("/usr/camscript/Ncam_Cr.sh restart")
		self.close()
		    
	def exit(self):
		print "Exit"      
		for x in self["config"].list:
		    x[1].cancel()         
		self.close()
