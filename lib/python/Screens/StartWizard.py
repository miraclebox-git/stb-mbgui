from Wizard import wizardManager
from Screens.WizardLanguage import WizardLanguage
from Screens.VideoWizard import VideoWizard
from Screens.Rc import Rc
from Screens.Screen import Screen

from boxbranding import getBoxType

from Components.Pixmap import Pixmap
from Components.config import config, ConfigBoolean, configfile, ConfigSelection

from LanguageSelection import LanguageWizard

config.misc.firstrun = ConfigBoolean(default = True)
config.misc.languageselected = ConfigBoolean(default = True)
config.misc.videowizardenabled = ConfigBoolean(default = True)
config.misc.iptvmode = ConfigSelection(default = "normal", choices = [("normal", _("Satellite")), ("iptv", _("IPTV"))])

class StartWizard(WizardLanguage, Rc):
	def __init__(self, session, silent = True, showSteps = False, neededTag = None):
		if config.misc.iptvmode.value in ('normal'):
			self.xmlfile = ["startwizard.xml"]
		else:
			self.xmlfile = ["startwizard_iptv.xml"]
		WizardLanguage.__init__(self, session, showSteps = False)
		Rc.__init__(self)
		self["wizard"] = Pixmap()
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		#Screen.setTitle(self, _("Welcome..."))
		Screen.setTitle(self, _("StartWizard"))
		

	def markDone(self):
		# setup remote control, all stb have same settings except dm8000 which uses a different settings
		if getBoxType() == 'dm8000':
			config.misc.rcused.value = 0
		else:
			config.misc.rcused.value = 1
		config.misc.rcused.save()

		config.misc.firstrun.value = 0
		config.misc.firstrun.save()
		configfile.save()


# mytest.py#L528ff - RestoreSettings
wizardManager.registerWizard(VideoWizard, config.misc.videowizardenabled.value, priority = 1)
wizardManager.registerWizard(LanguageWizard, config.misc.languageselected.value, priority = 0)
# FrontprocessorUpgrade FPUpgrade priority = 8
# FrontprocessorUpgrade SystemMessage priority = 9
wizardManager.registerWizard(StartWizard, config.misc.firstrun.value, priority = 10)
# StartWizard calls InstallWizard
# NetworkWizard priority = 25
