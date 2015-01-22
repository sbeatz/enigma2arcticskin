#-*- coding: UTF-8 -*-
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER, getPrevAsciiCode, eTimer
from Screen import Screen
from Components.Language import language
from Components.ActionMap import ActionMap, HelpableActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.HelpMenu import HelpableScreen
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Tools.NumericalTextInput import NumericalTextInput

class VirtualKeyBoardList(MenuList):
	def __init__(self, list, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 22))
		self.l.setItemHeight(60)

def VirtualKeyBoardEntryComponent(keys, selectedKey,shiftMode=False):
	key_backspace = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_backspace.png"))
	key_bg = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_bg.png"))
	key_clr = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_clr.png"))
	key_esc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_esc.png"))
	key_ok = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_ok.png"))
	key_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_sel.png"))
	key_shift = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_shift.png"))
	key_shift_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_shift_sel.png"))
	key_space = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_space.png"))
	key_left = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_left.png"))
	key_right = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/vkey_right.png"))
	res = [ (keys) ]
	
	x = 0
	count = 0
	if shiftMode:
		shiftkey_png = key_shift_sel
	else:
		shiftkey_png = key_shift
	for key in keys:
		width = None
		if key == "EXIT":
			width = key_esc.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_esc))
		elif key == "BACKSPACE":
			width = key_backspace.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_backspace))
		elif key == "CLEAR":
			width = key_clr.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_clr))
		elif key == "SHIFT":
			width = shiftkey_png.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=shiftkey_png))
		elif key == "SPACE":
			width = key_space.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_space))
		elif key == "OK":
			width = key_ok.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_ok))
		elif key == "LEFT":
			width = key_left.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_left))
		elif key == "RIGHT":
			width = key_right.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_right))
		else:
			width = key_bg.size().width()
			res.extend((
				MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_bg),
				MultiContentEntryText(pos=(x, 0), size=(width, 60), font=0, text=key.encode("utf-8"), flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER)
			))
		
		if selectedKey == count:
			width = key_sel.size().width()
			res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 60), png=key_sel))

		if width is not None:
			x += width
		else:
			x += 60
		count += 1
	return res


class VirtualKeyBoard(Screen, NumericalTextInput, HelpableScreen):

	def __init__(self, session, title="", text=""):
		Screen.__init__(self, session)
		NumericalTextInput.__init__(self, nextFunc = self.timeoutNI, handleTimeout = True)
		self.setUseableChars(u'1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ')
		self.sms_txt = None
		self.keys_list = []
		self.shiftkeys_list = []
		self.lang = language.getLanguage()
		self.nextLang = None
		self.shiftMode = False
		self.cursor = "XcursorX"
		self.gui_cursor = "| "
		self.text = text + self.cursor
		self.selectedKey = 0
		self.cursor_show = True
		self.cursor_time = 600
		self.cursorTimer = eTimer()
		self.cursorTimer.callback.append(self.toggleCursor)
		self.cursorTimer.start(self.cursor_time, True)
		self["country"] = StaticText("")
		self["header"] = Label(title)
		self["text"] = Label()
		self["list"] = VirtualKeyBoardList([])
		
		self["actions"] = ActionMap(["KeyboardInputActions", "InputAsciiActions"],
			{
				"gotAsciiCode": self.keyGotAscii,
				"deleteBackward": self.backClicked,
			}, -2)
		self["InputBoxActions"] = HelpableActionMap(self, "InputBoxActions",
			{
				"deleteBackward": (self.cursorLeft, _("Move cursor left")),
				"deleteForward": (self.cursorRight, _("Move cursor right")),
				"0": (self.toggleShift, _("Toggle SHIFT mode")),
			}, -2)
		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
				"ok": (self.okClicked, _("Select key")),
				"cancel": (self.exit, _("Cancel")),
			},-2)
		self["ShortcutActions"] = HelpableActionMap(self, "ShortcutActions",
			{		
				"red": (self.backClicked, _("Delete (left of the cursor)")),
				"blue": (self.backSpace, _("Delete (right of the cursor)")),
				"green": (self.ok, _("Save")),
				"yellow": (self.switchLang, _("Switch keyboard layout")),
			}, -2)
		self["WizardActions"] = HelpableActionMap(self, "WizardActions",
			{
				"left": (self.left, _("Left")),
				"right": (self.right, _("Right")),
				"up": (self.up, _("Up")),
				"down": (self.down, _("Down")),
			},-2)
		self["SeekActions"] = HelpableActionMap(self, "SeekActions",
			{
				"seekBack": (self.move_to_begin, _("Move to begin")),
				"seekFwd": (self.move_to_end, _("Move to end")),
			},-2)
		self["NumberActions"] = NumberActionMap(["NumberActions"],
		{
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal
		})

		self.set_GUI_Text()
		HelpableScreen.__init__(self)
		self.onExecBegin.append(self.setKeyboardModeAscii)
		self.onLayoutFinish.append(self.setLang)
		self.onLayoutFinish.append(self.buildVirtualKeyBoard)
	
	def switchLang(self):
		self.lang = self.nextLang
		self.setLang()
		self.buildVirtualKeyBoard()

	def setLang(self):
		if self.lang == 'de_DE':
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"ß",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ü", u"+",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ö", u"ä", u"#",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"@",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"?",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"Ü", u"*",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ö", u"Ä", u"'",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"\\",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'es_ES'
		elif self.lang == 'es_ES':
			#still missing keys (u"ùÙ")
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"ň",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ú", u"+",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ó", u"á", u"#",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-",
				u"@", u"Ł", u"ŕ", u"é", u"č", u"í", u"ě", u"ń",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"?",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"Ú", u"*",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ó", u"Á", u"'",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_",
				u"\\", u"Ŕ", u"É", u"Č", u"Í", u"Ě", u"Ń", u"Ň",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'fi_FI'
		elif self.lang == 'fi_FI':
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"ß",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"é", u"+",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ö", u"ä", u"#",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"@", u"ĺ",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"?",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"É", u"*",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ö", u"Ä", u"'",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"\\", u"Ĺ",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'sv_SE'
		elif self.lang == 'sv_SE':
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"ß",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"é", u"+",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ö", u"ä", u"#",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"@", u"ĺ",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"?",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"É", u"*",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"Ö", u"Ä", u"'",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_", u"\\", u"Ĺ",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'sk_SK'
		elif self.lang =='sk_SK':
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"é",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ú", u"+",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ľ", u"@", u"#",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-", u"š",
				u"č", u"ž", u"ý", u"á", u"í",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"?",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"ť", u"*",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"ň", u"ď", u"'",
				u"Á", u"É", u"Ď", u"Í", u"Ý", u"Ó", u"Ú", u"Ž", u"Š", u"Č", u"Ť", u"Ň",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_",
				u"\\", u"ä", u"ö", u"ü", u"ô", u"ŕ", u"ĺ",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'cs_CZ'
		elif self.lang == 'cs_CZ':
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"é",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"ú", u"+",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"ů", u"@", u"#",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".", u"-",
				u"ě", u"š", u"č", u"ř", u"ž", u"ý", u"á", u"í",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"?",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"ť", u"*",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"ň", u"ď", u"'",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":", u"_",
				u"\\", u"Č", u"Ř", u"Š", u"Ž", u"Ú", u"Á", u"É",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.nextLang = 'en_EN'
		else:
			self.keys_list = [
				u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"-",
				u"q", u"w", u"e", u"r", u"t", u"z", u"u", u"i", u"o", u"p", u"+", u"@",
				u"a", u"s", u"d", u"f", u"g", u"h", u"j", u"k", u"l", u"#", u"\\", u"|",
				u"<", u"y", u"x", u"c", u"v", u"b", u"n", u"m", u",", ".",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.shiftkeys_list = [
				u"EXIT", u"!", u'"', u"§", u"$", u"%", u"&", u"/", u"(", u")", u"=", u"_",
				u"Q", u"W", u"E", u"R", u"T", u"Z", u"U", u"I", u"O", u"P", u"*", u"[",
				u"A", u"S", u"D", u"F", u"G", u"H", u"J", u"K", u"L", u"'", u"?", u"]",
				u">", u"Y", u"X", u"C", u"V", u"B", u"N", u"M", u";", u":",
				u"CLEAR", u"SHIFT", u"SPACE", u"LEFT", u"RIGHT", u"BACKSPACE", u"OK"]
			self.lang = 'en_EN'
			self.nextLang = 'de_DE'
		self.keys_list = self.buildKeyBoardLayout(self.keys_list)
		self.shiftkeys_list = self.buildKeyBoardLayout(self.shiftkeys_list)
		self["country"].setText(self.lang)	

	def buildVirtualKeyBoard(self, selectedKey=0):
		list = []
		self.max_key = -1
		if self.shiftMode:
			self.k_list = self.shiftkeys_list
			for keys in self.k_list:
				keyslen = len(keys)
				self.max_key += keyslen
				if selectedKey < keyslen and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey,True))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1,True))
				selectedKey -= keyslen
		else:
			self.k_list = self.keys_list
			for keys in self.k_list:
				keyslen = len(keys)
				self.max_key += keyslen
				if selectedKey < keyslen and selectedKey > -1:
					list.append(VirtualKeyBoardEntryComponent(keys, selectedKey))
				else:
					list.append(VirtualKeyBoardEntryComponent(keys, -1))
				selectedKey -= keyslen
		self.first_line_len = len(self.k_list[0])
		self.no_of_lines = len(self.k_list)
		self["list"].setList(list)

	def buildKeyBoardLayout(self, key_list):
		line_len = 12
		if self["list"].skinAttributes:
			for (attrib, value) in self["list"].skinAttributes:
				if attrib == "linelength":
					line_len = int(value)
		k_list = []
		line = []
		i = 0
		for key in key_list:
			i += 1
			line.append(key)
			if i == line_len:
				k_list.append(line)
				i = 0
				line = []
		k_list.append(line)
		return k_list

	def toggleCursor(self):
		whitespace = " " * len(self.gui_cursor)
		if self.cursor_show:
			self.cursor_show = False
			txt = self.text.replace(self.cursor, whitespace)
		else:
			self.cursor_show = True
			txt = self.text.replace(self.cursor, self.gui_cursor)
		self["text"].setText(txt)
		self.cursorTimer.start(self.cursor_time, True)

	def set_GUI_Text(self):
		txt = self.text.replace(self.cursor, "| ")
		self["text"].setText(txt)

	def backClicked(self):
		txt = self.text.split(self.cursor)
		del_len = self.checkUnicode(txt[0][-1:])
		self.text = txt[0][:-del_len] + self.cursor + txt[1]
		self.set_GUI_Text()

	def backSpace(self):
		txt = self.text.split(self.cursor)
		del_len = self.checkUnicode(txt[1][:1])
		self.text = txt[0] + self.cursor + txt[1][del_len:]
		self.set_GUI_Text()

	def cursorLeft(self):
		self.moveCursor(-1)

	def cursorRight(self):
		self.moveCursor(+1)

	def checkUnicode(self, char):
		try:
			len(u'%s' % char)
		except UnicodeDecodeError:
			return 2
		return 1

	def moveCursor(self, direction):
		txt = self.text.split(self.cursor)
		if direction < 0:
			direction *= self.checkUnicode(txt[0][-1:])
		elif direction > 0:
			direction *= self.checkUnicode(txt[1][:1])
		pos = self.text.find(self.cursor) + direction
		clean_txt = self.text.replace(self.cursor, "")
		if pos > len(clean_txt):
			self.text = self.cursor + clean_txt
		elif pos < 0:
			self.text = clean_txt + self.cursor
		else:
			self.text = clean_txt[:pos] + self.cursor + clean_txt[pos:]
		self.set_GUI_Text()

	def move_to_begin(self):
		clean_txt = self.text.replace(self.cursor, "")
		self.text = self.cursor + clean_txt
		
	def move_to_end(self):
		clean_txt = self.text.replace(self.cursor, "")
		self.text = clean_txt + self.cursor

	def toggleShift(self):
		if self.shiftMode:
			self.shiftMode = False
		else:
			self.shiftMode = True
		self.buildVirtualKeyBoard(self.selectedKey)

	def keyNumberGlobal(self, number):
		self.cursorTimer.stop()
		if number != self.lastKey and self.lastKey != -1:
			self.nextChar()
		txt = self.getKey(number).encode("UTF-8")
		self.sms_txt = self.text.replace(self.cursor, txt +  self.cursor)
		self.got_sms_key(txt)
		self.set_GUI_SMS_Text()

	def set_GUI_SMS_Text(self):
		txt = self.sms_txt.replace(self.cursor, "| ")
		self["text"].setText(txt)

	def timeoutNI(self):
		if self.sms_txt:
			self.text = self.sms_txt
		self.sms_txt = None
		self.set_GUI_Text()
		self.cursorTimer.start(self.cursor_time, True)

	def okClicked(self):
		if self.shiftMode:
			list = self.shiftkeys_list
		else:
			list = self.keys_list
		selectedKey = self.selectedKey
		
		text = None
		
		for x in list:
			xlen = len(x)
			if selectedKey < xlen:
				if selectedKey < len(x):
					text = x[selectedKey]
				break
			else:
				selectedKey -= xlen
		
		if text is None:
			return
		
		text = text.encode("UTF-8")
		
		if text == "EXIT":
			self.exit()
		elif text == "BACKSPACE":
			self.backClicked()
		elif text == "CLEAR":
			self.text = "" + self.cursor
			self.set_GUI_Text()
		elif text == "SHIFT":
			self.toggleShift()
		elif text == "SPACE":
			self.text = self.text.replace(self.cursor, " " + self.cursor)
			self.set_GUI_Text()
		elif text == "OK":
			self.ok()
		elif text == "LEFT":
			self.cursorLeft()
		elif text == "RIGHT":
			self.cursorRight()
		else:
			self.text = self.text.replace(self.cursor, text + self.cursor)
			self.set_GUI_Text()

	def ok(self):
		text = self.text.encode("utf-8")
		text = text.replace(self.cursor, "")
		self.close(text)

	def exit(self):
		self.close(None)

	def moveActiveKey(self, direction):
		self.selectedKey += direction
		for k in range(0, self.no_of_lines, 1):
			no_of_chars = k * self.first_line_len
			if direction == -1:
				if self.selectedKey == no_of_chars - 1:
					self.selectedKey = no_of_chars - 1 + self.first_line_len
					if self.selectedKey > self.max_key:
						self.selectedKey = self.max_key
					break
			elif direction == 1:
				if self.selectedKey == no_of_chars + self.first_line_len:
					self.selectedKey = no_of_chars
					break
				if self.selectedKey > self.max_key:
					self.selectedKey = (self.no_of_lines -1) * self.first_line_len
					break
			elif direction == -self.first_line_len:
				if self.selectedKey < 0:
					self.selectedKey = (self.no_of_lines -1) * self.first_line_len + self.first_line_len + self.selectedKey
					if self.selectedKey > self.max_key:
						self.selectedKey = self.selectedKey - self.first_line_len
				break
			elif direction == self.first_line_len:
				tmp_key = self.selectedKey - self.first_line_len
				if self.selectedKey > self.max_key:
					line_no = k + 1
					if line_no * self.first_line_len > tmp_key:
						self.selectedKey = tmp_key - (line_no - 1) * self.first_line_len
						break
				elif self.selectedKey <= self.max_key:
					break
		self.showActiveKey()

	def left(self):
		self.moveActiveKey(-1)

	def right(self):
		self.moveActiveKey(+1)

	def up(self):
		self.moveActiveKey(-self.first_line_len)

	def down(self):
		self.moveActiveKey(+self.first_line_len)

	def showActiveKey(self):
		self.buildVirtualKeyBoard(self.selectedKey)

	def inShiftKeyList(self,key):
		for KeyList in self.shiftkeys_list:
			for char in KeyList:
				if char == key:
					return True
		return False

	def got_sms_key(self, char):
		if self.inShiftKeyList(char):
			self.shiftMode = True
			list = self.shiftkeys_list
		else:
			self.shiftMode = False
			list = self.keys_list
		selkey = 0
		for keylist in list:
			for key in keylist:
				if key == char:
					self.selectedKey = selkey
					self.showActiveKey()
					return
				else:
					selkey += 1

	def keyGotAscii(self):
		#char = str(unichr(getPrevAsciiCode()).encode('utf-8'))
		from Components.config import getCharValue
		char = getCharValue(getPrevAsciiCode())
		if len(str(char)) == 1:
			char = char.encode("utf-8")
		if self.inShiftKeyList(char):
			self.shiftMode = True
			list = self.shiftkeys_list
		else:
			self.shiftMode = False
			list = self.keys_list	
		if char == " ":
			char = "SPACE"
		selkey = 0
		for keylist in list:
			for key in keylist:
				if key == char:
					self.selectedKey = selkey
					self.okClicked()
					self.showActiveKey()
					return
				else:
					selkey += 1
