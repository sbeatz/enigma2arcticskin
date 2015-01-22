#
#  CaidDisplay - Converter
#
#  Coded by Dr.Best & weazle (c) 2010
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached
from os.path import isfile
from Poll import Poll

class extCaidDisplay(Poll, Converter, object):
	ecmDict = { }
	ecmMappingFile = "/etc/enigma2/ecmaddressmapping.cfg"
	
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.type = type
		self.systemCaids = {
			"06" : "I",
			"01" : "S",
			"18" : "N",
			"05" : "V",
			"0B" : "CO",
			"17" : "B",
			"0D" : "CW",
			"4A" : "DC",
			"55" : "BG",
			"09" : "ND" }

		self.poll_interval = 2000
		self.poll_enabled = True

		self.loadMappingFile()

	def loadMappingFile(self):
		if isfile(self.ecmMappingFile):
			try:
				f = open(CaidDisplay.ecmMappingFile, "r")
				for line in f.readlines():
					split = line.rstrip("\n").split(" ")
					if len(split) == 2:
						CaidDisplay.ecmDict[split[0]] = split[1]
				f.close()
			except:
				pass

	@cached
	def get_caidlist(self):
		caidlist = {}
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				caids = info.getInfoObject(iServiceInformation.sCAIDs)
				if caids:
					for caid in caids:
						c = "%x" % int(caid)
						if len(c) == 3:
							c = "0%s" % c
						c = c[:2].upper()
						if self.systemCaids.has_key(c) and not caidlist.has_key(c):
							caidlist[c] = (self.systemCaids.get(c),0)
					ecm_info = self.ecmfile()
					if ecm_info:
						emu_caid = ecm_info.get("caid", "")
						if emu_caid and emu_caid != "0x000":
							c = emu_caid.lstrip("0x")
							if len(c) == 3:
								c = "0%s" % c
							c = c[:2].upper()
							caidlist[c] = (self.systemCaids.get(c),1)
		return caidlist

	getCaidlist = property(get_caidlist)

	@cached
	def getText(self):
		textvalue = ""
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				if info.getInfoObject(iServiceInformation.sCAIDs):
					ecm_info = self.ecmfile()
					if ecm_info:
						# caid
						caid = ecm_info.get("caid", "")
						caid = caid.lstrip("0x")
						caid = caid.upper()
						caid = caid.zfill(4)
						# hops
						hops = ecm_info.get("hops", None)
						if hops and hops != "0":
							hops = "hop: %s" % hops
						else:
							hops = ""
						# ecm time	
						ecm_time = ecm_info.get("ecm time", None)
						if ecm_time:
							if "msec" in ecm_time:
								ecm_time = "- (%s)" % ecm_time						
							elif ecm_time != "nan":
								ecm_time = "- (%s s)" % ecm_time
							else:
								ecm_time = ""
						# address
						address = ecm_info.get("address", "")
						if address:
							if address == "/dev/sci0":
								address = "Slot #1"
							elif address == "/dev/sci1":
								address = "Slot #2"
							else:
								host = address.split(":")[0]
								if host in self.ecmDict:
									address = self.ecmDict[host]
						# source	
						using = ecm_info.get("using", "")
						if using:
							if using == "emu":
								textvalue = "decode: EMU %s %s" % (caid, ecm_time)
							elif using == "CCcam-s2s":
								textvalue = "decode: NET %s - %s %s %s" % (caid, address, hops, ecm_time)							
							else:
								textvalue = "decode: %s - %s %s" % (caid, address, ecm_time)		
						else:
							# mgcamd
							source = ecm_info.get("source", None)
							if source:
								if source == "emu":
									textvalue = "decode: EMU %s" % (caid)
								else:
									textvalue = "decode: %s - %s %s" % (caid, source, ecm_time)
							# oscam
							oscsource = ecm_info.get("from", None)
							if oscsource:
								host = oscsource.split(":")[0]
								if host in self.ecmDict:
									oscsource = self.ecmDict[host]
								textvalue = "decode: %s - %s %s %s" % (caid, oscsource, hops, ecm_time)
							# gbox
							decode = ecm_info.get("decode", None)
							prov = ecm_info.get("prov", None)

							paddress = slot = level = dist = ecmtime = ""
							if prov:
								prov = prov[0:4]
								prov_info = self.provfile(prov, caid)
								paddress = prov_info.get("paddress", None)
								if paddress:
									host = paddress.split(":")[0]
									if host in self.ecmDict:
										paddress = self.ecmDict[host]
								slot = prov_info.get("slot", None)
								level = prov_info.get("level", None)
								dist = prov_info.get("distance", None)
							if decode:
								ecmtime = ecm_info.get("ecm time", "")
								if decode == "Internal":
									textvalue = "decode: Internal %s" % (caid)
								elif decode.startswith("com"):
									textvalue = "decode: %s - %s (%s ms)" % (caid, decode, ecmtime)
								elif decode.startswith("slot"):
									textvalue = "decode: %s - %s (%s ms)" % (caid, decode, ecmtime)
								elif decode == "Network":
									textvalue = "NET %s - ID:%s - %s S:%s L:%s D:%s (%s ms)" % (caid, prov, paddress, slot, level, dist, ecmtime)
							
		return textvalue 

	text = property(getText)

	def ecmfile(self):
		ecm = None
		info = {}
		service = self.source.service
		if service:
			frontendInfo = service.frontendInfo()
			if frontendInfo:
				try:
					ecmpath = "/tmp/ecm%s.info" % frontendInfo.getAll(False).get("tuner_number")
					ecm = open(ecmpath, "rb").readlines()
				except:
					try:
						ecm = open("/tmp/ecm.info", "rb").readlines()
					except: pass
			if ecm:
				for line in ecm:
					x = line.lower().find("msec")
					if x != -1:
						info["ecm time"] = line[0:x+4]
					elif line.lower().find("response:") != -1:
						y = line.lower().find("response:")
						if y != -1:
							info["ecm time"] = line[y+9:].strip("\n\r")
					else:
						item = line.split(":", 1)
						if len(item) > 1:
							info[item[0].strip().lower()] = item[1].strip()
						else:
							if not info.has_key("caid"):
								x = line.lower().find("caid")
								if x != -1:
									y = line.find(",")
									if y != -1:
										info["caid"] = line[x+5:y]
		return info
	
	def provfile(self, prov, caid):
		provider = None
		pinfo = {}
		try:
			provider = open("/tmp/share.info", "rb").readlines()
		except: pass
		
		if provider:
			for line in provider:
				x = line.lower().find("id:")
				y = line.lower().find("card ")
				if x != -1 and y != -1:
					if caid != "0500":
						if line[x+3:].strip("\n\r") == prov.strip("\n\r") and line[y+5:y+9] == caid:
							x = line.lower().find("at ")
							if x != -1:
								y = line.lower().find("card ")
								if y != -1:
									pinfo["paddress"] = line[x+3:y-1]
								x = line.lower().find("sl:")
								if x != -1:
									y = line.lower().find("lev:")
									if y != -1:
										pinfo["slot"] = line[x+3:y-1]
										x = line.lower().find("dist:")
										if x != -1:
											pinfo["level"] = line[y+4:x-1]
											y = line.lower().find("id:")
											if y != -1:
												pinfo["distance"] = line[x+5:y-1]
					elif line[x+3:].strip("\n\r") == prov.strip("\n\r") and line[y+5:y+8] == caid[:-1]:
							x = line.lower().find("at ")
							if x != -1:
								y = line.lower().find("card ")
								if y != -1:
									pinfo["paddress"] = line[x+3:y-1]
								x = line.lower().find("sl:")
								if x != -1:
									y = line.lower().find("lev:")
									if y != -1:
										pinfo["slot"] = line[x+3:y-1]
										x = line.lower().find("dist:")
										if x != -1:
											pinfo["level"] = line[y+4:x-1]
											y = line.lower().find("id:")
											if y != -1:
												pinfo["distance"] = line[x+5:y-1]
		return pinfo

	def changed(self, what):
		if (what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo) or what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)
