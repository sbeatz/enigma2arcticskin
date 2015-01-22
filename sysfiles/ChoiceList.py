from MenuList import MenuList
from Tools.Directories import SCOPE_CURRENT_SKIN, resolveFilename
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont
from Tools.LoadPixmap import LoadPixmap
from Components.config import config
def ChoiceEntryComponent(key = "", text = ["--"]):
	res = [ text ]
	if text[0] == "--":
		if config.skin.primary_skin.value == "Arctic/skin.xml":
			res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 5, 800, 36, 0, RT_HALIGN_LEFT , "-"*200))
		else:
			res.append((eListboxPythonMultiContent.TYPE_TEXT, 0, 00, 800, 25, 0, RT_HALIGN_LEFT , "-"*200))
	else:
		if config.skin.primary_skin.value != "Arctic/skin.xml":
			res.append((eListboxPythonMultiContent.TYPE_TEXT, 45, 00, 800, 25, 0, RT_HALIGN_LEFT, text[0]))
		else:
			res.append((eListboxPythonMultiContent.TYPE_TEXT, 45, 5, 800, 36, 0, RT_HALIGN_LEFT, text[0]))
	
		png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/key_" + key + ".png"))

		if png is not None:
			if config.skin.primary_skin.value == "Arctic/skin.xml":
				res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 5, 10, 35, 25, png))
			else:
				res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 5, 0, 35, 25, png))
	
	return res

class ChoiceList(MenuList):
	def __init__(self, list, selection = 0, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		if config.skin.primary_skin.value == "Arctic/skin.xml":
			self.l.setFont(0, gFont("Regular", 22))
			self.l.setItemHeight(36)
		else:
			self.l.setFont(0, gFont("Regular", 20))
			self.l.setItemHeight(25)
		self.selection = selection

	def postWidgetCreate(self, instance):
		MenuList.postWidgetCreate(self, instance)
		self.moveToIndex(self.selection)
