# -*- coding: utf-8 -*-
from enigma import eEPGCache, eServiceReference
from Components.Converter.Converter import Converter
from Components.Element import cached
from datetime import datetime, timedelta
from time import localtime, strftime, mktime, time
from Components.config import config

class ArcticPrimetimeEvent(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.epgcache = eEPGCache.getInstance()
		  			
	@cached
	def getText(self):
		ptime = config.plugins.ArcticSetup.primetime.value
		entry = ''
		ref = self.source.service
		info = ref and self.source.info
		if info is None:
			return entry
		primeTimeEvent = self.source.getCurrentEvent()
		if primeTimeEvent:
			
			if not self.epgcache.startTimeQuery(eServiceReference(ref.toString()), primeTimeEvent.getBeginTime()):
				tomorrow = False
				actualtime = localtime(time())
				prime = datetime(actualtime.tm_year, actualtime.tm_mon, actualtime.tm_mday, ptime[0] , ptime[1])
				if time() > mktime(prime.timetuple()):
					tomorrow = True
					prime += timedelta(days=1)
				primeTime = int(mktime(prime.timetuple()))
				if not self.epgcache.startTimeQuery(eServiceReference(ref.toString()), primeTime):
					event = self.epgcache.getNextTimeEntry()
					if event and (event.getBeginTime() <= int(mktime(prime.timetuple()))):
						if tomorrow == False:
							entry = "%s - %s" % (strftime("%H:%M", localtime(event.getBeginTime())), event.getEventName()) 
						else:
							entry = "%s - %s" % (strftime("Morgen " + "%H:%M", localtime(event.getBeginTime())), event.getEventName())
		return entry
	text = property(getText)
	def changed(self, changedvalue):
		Converter.changed(self, changedvalue)