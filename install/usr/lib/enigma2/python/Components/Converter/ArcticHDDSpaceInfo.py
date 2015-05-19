from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Poll import Poll
from os import popen, statvfs, path


class ArcticHDDSpaceInfo(Poll, Converter):

	def __init__(self, val):
		Converter.__init__(self, val)
		Poll.__init__(self)
		self.poll_interval = 5000
		self.poll_enabled = True

	def doSuspend(self, suspended):
		if suspended:
			self.poll_enabled = False
		else:
			self.downstream_elements.changed((self.CHANGED_POLL,))
			self.poll_enabled = True

	@cached
	def getText(self):
		ret = self.getSize("/media/hdd")
		if ret is None:
		    ret = self.getSize("/media/usb")
		    if not ret is None:
			    return ret
		    else:
			    return "N/A"
		else:
		    return ret

	@cached
	def getValue(self):
		ret = self.getSize("/media/hdd")
		if ret is None:
		    ret = self.getSize("/media/usb")
		    if not ret is None:
			    return ret
		    else:
			    return "N/A"
		else:
		    return ret
		    
		

		
	text = property(getText)
	value = property(getValue)


	
	def getSize(self, path):
		try:
		    st = statvfs(path)
		    st = st.f_bsize * st.f_bavail
		    st = self.convertSizeToString(st)
		    return st
		except Exception, ex:
		    return None

	
	

	def convertSizeToString(self, value, u=0):
	    sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
	    f = 0
	    if value >= 1024:
			s = "%(size)u.%(frac)d %(unit)s"
			while (value >= 1024) and (u < len(sizes)):
				(value, mod) = divmod(value, 1024)
				f = mod * 10 / 1024
				u += 1
	    else:
			s = "%(size)u %(unit)s"
	    return s % {"size": value, "frac": f, "unit": sizes[u]}
		
	def doSuspend(self, suspended):
		if suspended:
			self.poll_enabled = False
		else:
			self.downstream_elements.changed((self.CHANGED_POLL,))
			self.poll_enabled = True
	        