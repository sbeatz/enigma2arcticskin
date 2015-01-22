# coders by Vlamo 2012
# mod.zombi
# LN - add getPathInfo
from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Poll import Poll
from os import popen, statvfs, path

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]


class extDiskSpaceInfo(Poll, Converter):
	HDDTEMP = 0
	MEMFREE = 1
	USBINFO = 2
	HDDINFO = 3
	FLASHINFO = 4
	FLASHINFO2 = 5
	MOVIEDIR = 6

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
        
		type = type.split(',')
		self.shortFormat = "Short" in type
		self.fullFormat  = "Full"  in type
		if "HddTemp" in type:
			self.type = self.HDDTEMP
		elif "MemFree" in type:
			self.type = self.MEMFREE
		elif "UsbInfo" in type:
			self.type = self.USBINFO
		elif "HddInfo" in type:
			self.type = self.HDDINFO
		elif "FlashInfo2" in type:
			self.type = self.FLASHINFO2
		elif "MovieDir" in type:
			self.type = self.MOVIEDIR
		else:
			self.type = self.FLASHINFO	
		
		if self.type in (self.FLASHINFO,self.FLASHINFO2,self.HDDINFO,self.USBINFO):
			self.poll_interval = 5000
		else:
			self.poll_interval = 1000
		self.poll_enabled = True

	def doSuspend(self, suspended):
		if suspended:
			self.poll_enabled = False
		else:
			self.downstream_elements.changed((self.CHANGED_POLL,))
			self.poll_enabled = True

	@cached
	def getText(self):
		text = "N/A"
		if self.type == self.HDDTEMP:
			text = self.getHddTemp()
		else:
			entry = {
					self.MEMFREE:   ("Mem","Ram"),
					self.USBINFO:   ("/media/usb","USB"),
					self.HDDINFO:   ("/media/hdd","HDD"),
					self.FLASHINFO: ("/","Flash"),
					self.FLASHINFO2: ("/data","DATA"),
					self.MOVIEDIR:   (config.movielist.last_videodir.value,""),
				}[self.type]
			if self.type in (self.USBINFO,self.HDDINFO,self.FLASHINFO,self.FLASHINFO2):
				list = self.getDiskInfo(entry[0])
			elif self.type == self.MOVIEDIR:
				list = self.getPathInfo()
			else:
				list = self.getMemInfo(entry[0])
			if list[0] == 0:
				if config.osd.language.value == "de_DE":
					text = "Gesamt: %s nicht Verfuegbar"%(entry[1])
				else:
					text = "Total: %s not Available"%(entry[1])
			elif self.shortFormat:
				if config.osd.language.value == "de_DE":
					text = "%s" % (self.getSizeStr(list[2]))
				else:
					text = "%s Total: %s Used: %s%%" % (entry[1], self.getSizeStr(list[0]), list[3])
			elif self.fullFormat:
				if config.osd.language.value == "de_DE":
					text = "%s Gesamt: %s Frei: %s Belegt: %s (%s%%)" % (entry[1], self.getSizeStr(list[0]), self.getSizeStr(list[2]), self.getSizeStr(list[1]), list[3])
				else:
					text = "%s Total: %s Free: %s Available: %s (%s%%)" % (entry[1], self.getSizeStr(list[0]), self.getSizeStr(list[2]), self.getSizeStr(list[1]), list[3])
			else:
				if config.osd.language.value == "de_DE":
					text = "Frei: %s" % (self.getSizeStr(list[2]))
				else:
					text = "%s Total: %s Used: %s Available: %s" % (entry[1], self.getSizeStr(list[0]), self.getSizeStr(list[1]), self.getSizeStr(list[2]))
		return text

	@cached
	def getValue(self):
		result = 0
		if self.type in (self.MEMFREE):
			entry = {self.MEMFREE: "Mem"}[self.type]
			result = self.getMemInfo(entry)[3]
		elif self.type in (self.USBINFO,self.HDDINFO,self.FLASHINFO,self.FLASHINFO2):
			path = {self.USBINFO: "/media/usb", self.HDDINFO: "/media/hdd", self.FLASHINFO: "/", self.FLASHINFO2: "/data"}[self.type]
			result = self.getDiskInfo(path)[3]
		elif self.type == self.MOVIEDIR:
			result = self.getPathInfo()[3]
		return result

	text = property(getText)
	value = property(getValue)
	range = 100

	def getHddTemp(self):
		textvalue = "No info"
		info = "0"
		try:
			out_line = popen("hddtemp -n -q /dev/sda").readline()
			info = "Hdd C:" + out_line[:4]
			textvalue = info
		except:
			pass
		return textvalue

	def getMemInfo(self, value):
		result = [0,0,0,0]	# (size, used, avail, use%)
		try:
			check = 0
			fd = open("/proc/meminfo")
			for line in fd:
				if value + "Total" in line:
					check += 1
					result[0] = int(line.split()[1]) * 1024		# size
				elif value + "Free" in line:
					check += 1
					result[2] = int(line.split()[1]) * 1024		# avail
				if check > 1:
					if result[0] > 0:
						result[1] = result[0] - result[2]	# used
						result[3] = result[1] * 100 / result[0]	# use%
					break
			fd.close()
		except:
			pass
		return result

	def getDiskInfo(self, path):
		def isMountPoint():
			try:
				fd = open('/proc/mounts', 'r')
				for line in fd:
					l = line.split()
					if len(l) > 1 and l[1] == path:
						return True
				fd.close()
			except:
				return None
			return False
		
		result = [0,0,0,0]	# (size, used, avail, use%)
		if isMountPoint():
			try:
				st = statvfs(path)
			except:
				st = None
			if not st is None and not 0 in (st.f_bsize, st.f_blocks):
				result[0] = st.f_bsize * st.f_blocks	# size
				result[2] = st.f_bsize * st.f_bavail	# avail
				result[1] = result[0] - result[2]	# used
				result[3] = result[1] * 100 / result[0]	# use%
		return result
	
	def getPathInfo(self):
		result = [0,0,0,0]	# (size, used, avail, use%)
		try:
			if path.exists(config.movielist.last_videodir.value):
				stat = statvfs(config.movielist.last_videodir.value)
				result[0] = stat.f_bsize * stat.f_blocks											# size
				result[2] = (stat.f_bavail if stat.f_bavail!=0 else stat.f_bfree) * stat.f_bsize	# available
				result[1] = stat.f_bsize * (stat.f_blocks - stat.f_bfree)							# used
				result[3] = result[1] * 100 / result[0]												# used%
			return result
		except:
			return result 

	def getSizeStr(self, value, u=0):
		fractal = 0
		if value >= 1024:
			fmt = "%(size)u.%(frac)d %(unit)s"
			while (value >= 1024) and (u < len(SIZE_UNITS)):
				(value, mod) = divmod(value, 1024)
				fractal = mod * 10 / 1024
				u += 1
		else:
			fmt = "%(size)u %(unit)s"
		return fmt % {"size": value, "frac": fractal, "unit": SIZE_UNITS[u]}
		
	def doSuspend(self, suspended):
		if suspended:
			self.poll_enabled = False
		else:
			self.downstream_elements.changed((self.CHANGED_POLL,))
			self.poll_enabled = True
	        