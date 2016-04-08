from Screens.MessageBox import MessageBox
from Screens.InfoBarGenerics import InfoBarTimeshift

from OTTMenu import OTTMenu
from OTTTimer import OTTTimer
from OTTMount import OTTMount
from OTTLocale import _

import os

timerinstance = None

def OTTClient(session, **kwargs):
	global timerinstance
	session.open(OTTMenu, timerinstance)
	
def OTTClientAutostart(reason, session=None, **kwargs):
	global timerinstance
	timerinstance = OTTTimer(session)
	
	#InfoBarTimeshift.ts_disabled = True
	
	mount = OTTMount(session)
	mount.automount()
	
