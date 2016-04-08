from Components.config import config

from OTTDownloader import OTTDownloader
from OTTLocale import _

from enigma import eTimer

from time import localtime, time, strftime, mktime

class OTTTimer:
	def __init__(self, session):
		self.session = session
		
		self.ipboxdownloadtimer = eTimer()
		self.ipboxdownloadtimer.callback.append(self.onIpboxDownloadTimer)
		
		self.ipboxpolltimer = eTimer()
		self.ipboxpolltimer.timeout.get().append(self.onIpboxPollTimer)

		self.refreshScheduler()

	def onIpboxPollTimer(self):
		self.ipboxpolltimer.stop()
		self.scheduledtime = self.prepareTimer()

	def getTodayScheduledTime(self):
		backupclock = config.ipboxclient.scheduletime.value
		now = localtime(time())
		return int(mktime((now.tm_year, now.tm_mon, now.tm_mday, backupclock[0], backupclock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))

	def prepareTimer(self):
		self.ipboxdownloadtimer.stop()
		scheduled_time = self.getTodayScheduledTime()
		now = int(time())
		if scheduled_time > 0:
			if scheduled_time < now:
				if config.ipboxclient.repeattype.value == "daily":
					scheduled_time += 24*3600
					while (int(scheduled_time)-30) < now:
						scheduled_time += 24*3600
				elif config.ipboxclient.repeattype.value == "weekly":
					scheduled_time += 7*24*3600
					while (int(scheduled_time)-30) < now:
						scheduled_time += 7*24*3600
				elif config.ipboxclient.repeattype.value == "monthly":
					scheduled_time += 30*24*3600
					while (int(scheduled_time)-30) < now:
						scheduled_time += 30*24*3600
			next = scheduled_time - now
			self.ipboxdownloadtimer.startLongTimer(next)
		else:
			scheduled_time = -1
		return scheduled_time

	def onIpboxDownloadTimer(self):
		self.ipboxdownloadtimer.stop()
		now = int(time())
		wake = self.getTodayScheduledTime()
		if wake - now < 60:
			downloader = OTTDownloader(self.session)
			try:
				downloader.download()
			except Exception, e:
				print e
		self.scheduledtime = self.prepareTimer()

	def refreshScheduler(self):
		now = int(time())
		if config.ipboxclient.schedule.value:
			if now > 1262304000:
				self.scheduledtime = self.prepareTimer()
			else:
				self.scheduledtime = 0
				self.ipboxpolltimer.start(36000)
		else:
			self.scheduledtime = 0
			self.ipboxpolltimer.stop()

