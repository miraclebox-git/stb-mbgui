from Components.config import config
from Components.TimerSanityCheck import TimerSanityCheck
from RecordTimer import RecordTimerEntry, AFTEREVENT
from ServiceReference import ServiceReference
from timer import TimerEntry

from OTTLocale import _

from xml.dom import minidom
from time import localtime, strftime, ctime, time
from bisect import insort

import urllib
import urllib2
import re
import os

def getValueFromNode(event, key):
	tmp = event.getElementsByTagName(key)[0].firstChild
	if (tmp):
		return str(tmp.nodeValue)
	
	return ""

class OTTRemoteTimer():
	_timer_list = []
	_processed_timers = []
	
	on_state_change = []

	last_update_ts = 0
	
	def __init__(self):
		pass

	@property
	def timer_list(self):
		if self.last_update_ts + 30 < time():
			self.getTimers()
		return self._timer_list

	@timer_list.setter
	def timer_list(self, value):
		self._timer_list = value

	@timer_list.deleter
	def timer_list(self):
		del self._timer_list

	@property
	def processed_timers(self):
		if self.last_update_ts + 30 < time():
			self.getTimers()
		return self._processed_timers

	@processed_timers.setter
	def processed_timers(self, value):
		self._processed_timers = value

	@processed_timers.deleter
	def processed_timers(self):
		del self._processed_timers

	def getTimers(self):
		self._timer_list = []
		self._processed_timers = []

		baseurl = self.getBaseUrl()

		print "[OTTRemoteTimer] get remote timer list"

		try:
			httprequest = urllib2.urlopen(baseurl + '/web/timerlist')
			xmldoc = minidom.parseString(httprequest.read())
			timers = xmldoc.getElementsByTagName('e2timer') 
			for timer in timers:
				serviceref = ServiceReference(getValueFromNode(timer, 'e2servicereference'))
				begin = int(getValueFromNode(timer, 'e2timebegin'))
				end = int(getValueFromNode(timer, 'e2timeend'))
				name = getValueFromNode(timer, 'e2name')
				description = getValueFromNode(timer, 'e2description')
				eit = int(getValueFromNode(timer, 'e2eit'))
				disabled = int(getValueFromNode(timer, 'e2disabled'))
				justplay = int(getValueFromNode(timer, 'e2justplay'))
				afterevent = int(getValueFromNode(timer, 'e2afterevent'))
				repeated = int(getValueFromNode(timer, 'e2repeated'))
				location = getValueFromNode(timer, 'e2location')
				tags = getValueFromNode(timer, 'e2tags').split(" ")

				entry = RecordTimerEntry(serviceref, begin, end, name, description, eit, disabled, justplay, afterevent, dirname = location, tags = tags, descramble = 1, record_ecm = 0, isAutoTimer = 0, always_zap = 0)
				entry.repeated = repeated

				entry.orig = RecordTimerEntry(serviceref, begin, end, name, description, eit, disabled, justplay, afterevent, dirname = location, tags = tags, descramble = 1, record_ecm = 0, isAutoTimer = 0, always_zap = 0)
				entry.orig.repeated = repeated

				if entry.shouldSkip() or entry.state == TimerEntry.StateEnded or (entry.state == TimerEntry.StateWaiting and entry.disabled):
					insort(self._processed_timers, entry)
				else:
					insort(self._timer_list, entry)
		except Exception, e:
			print "[OTTRemoteTimer]", e
		
		self.last_update_ts = time()
		
	def getBaseUrl(self):
		baseurl = "http://"
		if config.ipboxclient.auth.value:
			baseurl += config.ipboxclient.username.value
			baseurl += ":"
			baseurl += config.ipboxclient.password.value
			baseurl += "@"
			
		baseurl += config.ipboxclient.host.value
		baseurl += ":"
		baseurl += str(config.ipboxclient.port.value)
		return baseurl
	
	def getNextRecordingTime(self):
		return -1
	
	def getNextZapTime(self):
		return -1
	
	def isNextRecordAfterEventActionAuto(self):
		return False

	def isInTimer(self, eventid, begin, duration, service):
		returnValue = None
		type = 0
		time_match = 0
		isAutoTimer = False
		bt = None
		end = begin + duration
		refstr = ":".join(str(service).split(":")[:10]) + ':'
		for x in self._timer_list:
			if x.isAutoTimer == 1:
				isAutoTimer = True
			else:
				isAutoTimer = False
			check = x.service_ref.ref.toString() == refstr
			if check:
				timer_end = x.end
				type_offset = 0
				if x.justplay:
					type_offset = 5
					if (timer_end - x.begin) <= 1:
						timer_end += 60
				if x.always_zap:
					type_offset = 10

				if x.repeated != 0:
					if bt is None:
						bt = localtime(begin)
						et = localtime(end)
						bday = bt.tm_wday;
						begin2 = bday * 1440 + bt.tm_hour * 60 + bt.tm_min
						end2   = et.tm_wday * 1440 + et.tm_hour * 60 + et.tm_min
					if x.repeated & (1 << bday):
						xbt = localtime(x.begin)
						xet = localtime(timer_end)
						xbegin = bday * 1440 + xbt.tm_hour * 60 + xbt.tm_min
						xend   = bday * 1440 + xet.tm_hour * 60 + xet.tm_min
						if xend < xbegin:
							xend += 1440
						if begin2 < xbegin <= end2:
							if xend < end2: # recording within event
								time_match = (xend - xbegin) * 60
								type = type_offset + 3
							else:           # recording last part of event
								time_match = (end2 - xbegin) * 60
								type = type_offset + 1
						elif xbegin <= begin2 <= xend:
							if xend < end2: # recording first part of event
								time_match = (xend - begin2) * 60
								type = type_offset + 4
							else:           # recording whole event
								time_match = (end2 - begin2) * 60
								type = type_offset + 2
				else:
					if begin < x.begin <= end:
						if timer_end < end: # recording within event
							time_match = timer_end - x.begin
							type = type_offset + 3
						else:           # recording last part of event
							time_match = end - x.begin
							type = type_offset + 1
					elif x.begin <= begin <= timer_end:
						if timer_end < end: # recording first part of event
							time_match = timer_end - begin
							type = type_offset + 4
						else:           # recording whole event
							time_match = end - begin
							type = type_offset + 2
				if time_match:
					if type in (2,7,12): # When full recording do not look further
						returnValue = (time_match, [type], isAutoTimer)
						break
					elif returnValue:
						if type not in returnValue[1]:
							returnValue[1].append(type)
					else:
						returnValue = (time_match, [type])

		return returnValue

	def record(self, entry, ignoreTSC=False, dosave=True):
		print "[OTTRemoteTimer] record ", str(entry)

		entry.service_ref = ServiceReference(":".join(str(entry.service_ref).split(":")[:10]))
		args = urllib.urlencode({
				'sRef': str(entry.service_ref),
				'begin': str(entry.begin),
				'end': str(entry.end),
				'name': entry.name,
				'disabled': str(1 if entry.disabled else 0),
				'justplay': str(1 if entry.justplay else 0),
				'afterevent': str(entry.afterEvent),
				'dirname': str(entry.dirname),
				'tags': " ".join(entry.tags),
				'repeated': str(entry.repeated),
				'description': entry.description
			})

		baseurl = self.getBaseUrl()

		print "[OTTRemoteTimer] web interface url: " + baseurl

		try:
			httprequest = urllib2.urlopen(baseurl + '/web/timeradd?' + args)
			xmldoc = minidom.parseString(httprequest.read())
			status = xmldoc.getElementsByTagName('e2simplexmlresult')[0]
			success = getValueFromNode(status, 'e2state') == "True"
		except Exception, e:
			print "[OTTRemoteTimer]", e
			return None

		self.getTimers()

		if not success:
			timersanitycheck = TimerSanityCheck(self._timer_list,entry)
			if not timersanitycheck.check():
				print "timer conflict detected!"
				print timersanitycheck.getSimulTimerList()
				return timersanitycheck.getSimulTimerList()

		return None

	def timeChanged(self, entry):
		print "[OTTRemoteTimer] timer changed ", str(entry)

		entry.service_ref = ServiceReference(":".join(str(entry.service_ref).split(":")[:10]))
		args = urllib.urlencode({
				'sRef': str(entry.service_ref),
				'begin': str(entry.begin),
				'end': str(entry.end),
				'channelOld': str(entry.orig.service_ref),
				'beginOld': str(entry.orig.begin),
				'endOld': str(entry.orig.end),
				'name': entry.name,
				'disabled': str(1 if entry.disabled else 0),
				'justplay': str(1 if entry.justplay else 0),
				'afterevent': str(entry.afterEvent),
				'dirname': str(entry.dirname),
				'tags': " ".join(entry.tags),
				'repeated': str(entry.repeated),
				'description': entry.description
			})

		baseurl = self.getBaseUrl()
		try:
			httprequest = urllib2.urlopen(baseurl + '/web/timerchange?' + args)
			xmldoc = minidom.parseString(httprequest.read())
			status = xmldoc.getElementsByTagName('e2simplexmlresult')[0]
			success = getValueFromNode(status, 'e2state') == "True"
		except Exception, e:
			print "[OTTRemoteTimer]", e
			return None

		self.getTimers()

		if not success:
			timersanitycheck = TimerSanityCheck(self._timer_list,entry)
			if not timersanitycheck.check():
				print "timer conflict detected!"
				print timersanitycheck.getSimulTimerList()
				return timersanitycheck.getSimulTimerList()

		return None

	def removeEntry(self, entry):
		print "[OTTRemoteTimer] timer remove ", str(entry)

		entry.service_ref = ServiceReference(":".join(str(entry.service_ref).split(":")[:10]))
		args = urllib.urlencode({
				'sRef': str(entry.service_ref),
				'begin': str(entry.begin),
				'end': str(entry.end)
			})

		baseurl = self.getBaseUrl()
		try:
			httprequest = urllib2.urlopen(baseurl + '/web/timerdelete?' + args)
			httprequest.read()
		except Exception, e:
			print "[OTTRemoteTimer]", e
			return

		self.getTimers()

	def isRecording(self):
		isRunning = False
		for timer in self.timer_list:
			if timer.isRunning() and not timer.justplay:
				isRunning = True
		return isRunning

	def saveTimer(self):
		pass

	def shutdown(self):
		pass
