from Plugins.Plugin import PluginDescriptor

from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigClock, ConfigSelection

from OTTClient import OTTClient, OTTClientAutostart
from OTTRemoteTimer import OTTRemoteTimer
from OTTWizard import OTTWizard
from OTTLocale import _

config.ipboxclient = ConfigSubsection()
config.ipboxclient.host = ConfigText(default = "", fixed_size = False)
config.ipboxclient.port = ConfigInteger(default = 80, limits = (1, 65535))
config.ipboxclient.streamport = ConfigInteger(default = 8001, limits = (1, 65535))
config.ipboxclient.auth = ConfigYesNo(default = False)
config.ipboxclient.firstconf = ConfigYesNo(default = False)
config.ipboxclient.username = ConfigText(default = "", fixed_size = False)
config.ipboxclient.password = ConfigText(default = "", fixed_size = False)
config.ipboxclient.schedule = ConfigYesNo(default = False)
config.ipboxclient.scheduletime = ConfigClock(default = 0) # 1:00
config.ipboxclient.repeattype = ConfigSelection(default = "daily", choices = [("daily", _("Daily")), ("weekly", _("Weekly")), ("monthly", _("30 Days"))])
config.ipboxclient.mounthdd = ConfigYesNo(default = False)
config.ipboxclient.remotetimers = ConfigYesNo(default = False)

#MOD
from Components.config import config, ConfigBoolean, configfile
config.misc.firstrun = ConfigBoolean(default = True)
#config.misc.iptvmode = ConfigSelection(default = "normal", choices = [("normal", _("Satellite")), ("iptv", _("IPTV"))])

def ipboxclientRecordTimer():
	return OTTRemoteTimer()

def ipboxclientStart(menuid, **kwargs):
	if menuid == "scan":
		return [(_("Remote IPTV Scanner"), OTTClient, "iptv_client_Start", 13)]
	else:
		return []

def Plugins(**kwargs):
	list = [
		PluginDescriptor(
			where = PluginDescriptor.WHERE_SESSIONSTART,
			fnc = OTTClientAutostart
		),
		#PluginDescriptor(
			#name = "OTTClient",
			#description = _("IPTV network client"),
			#where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
			#fnc = OTTClient
		#),
		PluginDescriptor(
			name = "OTTClient",
			description = _("IPTV network client"),
			where = PluginDescriptor.WHERE_MENU,
			needsRestart = False,
			fnc = ipboxclientStart
		)
	]
	
	if config.ipboxclient.remotetimers.value:
		list.append(PluginDescriptor(
			where = PluginDescriptor.WHERE_RECORDTIMER,
			fnc = ipboxclientRecordTimer
		))
	
	if config.misc.firstrun.value:
	#if not config.ipboxclient.firstconf.value:
		list.append(PluginDescriptor(
			name = _("IPTV wizard"),
			where = PluginDescriptor.WHERE_WIZARD,
			needsRestart = False,
			fnc=(3, OTTWizard)
		))
	return list
