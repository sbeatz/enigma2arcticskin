# -*- coding: utf-8 -*-
import re, os, threading
from re import findall, search, split, sub
from enigma import RT_WRAP, RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, gFont, eListbox,eListboxPythonMultiContent, getDesktop, BT_SCALE, BT_FIXRATIO
from Components.AVSwitch import AVSwitch
from Components.GUIComponent import GUIComponent
from os import path as os_path, listdir as os_listdir, chdir as os_chdir, getcwd as os_getcwd,  symlink
from Screens.Screen import Screen
import os
from enigma import addFont, eListboxPythonMultiContent, eConsoleAppContainer, eBackgroundFileEraser, eListbox, ePixmap, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, loadPNG, RT_WRAP, eServiceReference, getDesktop, loadPic, loadJPG, RT_VALIGN_CENTER, gPixmapPtr, ePicLoad, eTimer, ePoint, eSize, iPlayableService, eServiceCenter, ePythonMessagePump, iServiceInformation, eEPGCache, eRect, BT_SCALE, BT_FIXRATIO
import Screens.Standby
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Console import Console
import shutil
import xml.etree.cElementTree
import xml
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config,ConfigNothing, ConfigDirectory, NoSave, ConfigClock
import urllib
import json
from urllib2 import Request, urlopen, URLError, HTTPError
from Components.About import about
import sys, os, getopt
import threading, time, Queue
from threading import Thread
import xmltodict
from Components.Pixmap import Pixmap, MultiPixmap
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN, SCOPE_CURRENT_SKIN, createDir
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest
import skin

ListBoxImageLoaderQueue = Queue.Queue()



def VMC_BaseFunctions_downloadFile(url, target, timeout):
    try:
        urllib.urlretrieve (url, target)
    except Exception, ex:
        print str(ex)


def DownloadListBoxImage(q):
    while True:
        print 'Looking for the next link' 
        item, List = q.get()
        print 'Downloading ' + str((str(item.imagelink)))
        print 'to ' + item.imagepath
        VMC_BaseFunctions_downloadFile((str(item.imagelink)),item.imagepath,10)
        List.updateListObject(item.index)
        q.task_done()

class CheckUpdate():
    def __init__(self, session):
        self.session = session

    def checkForUpdate(self):
        versionstring = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/version','r').read()
        self.version = int(versionstring.replace('.',''))
        urllib.urlretrieve('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/version','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/onlineversion')
        self.onlineversionstring = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/onlineversion','r').read()
        self.onlineversion = int(self.onlineversionstring.replace('.',''))
        if self.onlineversion > self.version:
            self.session.openWithCallback(self.doUpdate, MessageBox, _("Es gibt ein Update des Arctic Skin auf Version " + self.onlineversionstring + " - Wollen Sie es jetzt installieren?"), MessageBox.TYPE_YESNO)

    def doUpdate(self, answer):
        if answer:
            urllib.urlretrieve('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/skin.xml','/usr/share/enigma2/Arctic/skin_tmp.xml')
            update = open('/usr/share/enigma2/Arctic/skin_tmp.xml','r').read()
            print update
            if update.startswith("<skin>") and update.strip().endswith("</skin>"):
                print "Update erfolgreich"
                if str(config.plugins.ArcticSetup.button.value) == "1":
                    update = update.replace('text="a"','text="I"')
                    for root, dirs, files in os.walk('/usr/share/enigma2/Arctic/allScreens', topdown=True, onerror=None, followlinks=False):    
                        files = [file for file in files if file.endswith(".xml")]
                        for file in files:
                            rep = open(os.path.join(root,file),'r').read()
                            rep = rep.replace('text="a"','text="I"')
                            f = open(os.path.join(root,file),'w')
                            f.write(u)
                            f.close()

                else:
                    for root, dirs, files in os.walk('/usr/share/enigma2/Arctic/allScreens', topdown=True, onerror=None, followlinks=False):    
                        files = [file for file in files if file.endswith(".xml")]
                        for file in files:
                            rep = open(os.path.join(root,file),'r').read()
                            u = rep.replace('text="I"','text="a"')
                            f = open(os.path.join(root,file),'w')
                            f.write(u)
                            f.close()                    

                file = open('/usr/share/enigma2/Arctic/skin.xml','w')
                file.write(str(update))
                file.close()

                file = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/version','w')
                file.write(str(self.onlineversion))
                file.close()
                config.plugins.ArcticSetup.VersionString.value = self.onlineversionstring
                config.plugins.ArcticSetup.VersionString.save()
                self.session.openWithCallback(self.restartGUI, MessageBox, _("Arctic wurde erfolgreich aktualisiert!\nWollen Sie jetzt die Enigma2 GUI neu starten?"), MessageBox.TYPE_YESNO)

    def restartGUI(self, answer):
        if answer:
            self.session.open(Screens.Standby.TryQuitMainloop, 3)

class Skinpart():
    index = 0
    type = 0
    dateadded = 0
    title = u''
    filename = ''
    link = None
    imagelink = None
    imagepath = ''
    category = u''
    description = ''
    version = ''
    creator = u''
    isinstalled = False
    updateavailable = False
    items = []
    def __init__(self, title = None, filename = '', link = '', imagelink = '', category = None, description = '', version = None, creator = '', type = 0, dateadded = 0, isinstalled = False, updateavailable = False, index = 0):
        self.index = index
        self.title = title
        print str(title)
        self.filename = filename
        self.link = str(link).replace('https','http')
        self.imagelink = str(imagelink).replace('https','http')
        self.imagepath =  str(imagelink).replace("https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/skinparts/", "/tmp/")
        self.category = category
        self.description = description
        self.version = version
        self.creator = creator
        self.type = type
        self.dateadded = dateadded
        self.isinstalled = isinstalled
        self.updateavailable = updateavailable
        self.items = []

class SkinpartList(GUIComponent, object):
    GUI_WIDGET = eListbox

    def __init__(self):
        GUIComponent.__init__(self)
        self.scale = AVSwitch().getFramebufferScale()
        self.l = eListboxPythonMultiContent()
        self.l.setFont(0, gFont('Regular', 22))
        self.l.setFont(1, gFont('Regular', 16))
        self.l.setBuildFunc(self.buildSkinpartEntry)
        self.l.setItemHeight(50)
        self.onSelectionChanged = []
        self.pixmapCache = {}
        self.selectedID = None
        self.l.setSelectableFunc(self.isSelectable)
        self.list = []
        worker = Thread(target=DownloadListBoxImage, args=(ListBoxImageLoaderQueue,))
        worker.setDaemon(True)
        worker.start()        
        return

    def loadPixmap(self, filename):
        ptr = None
        if filename in self.pixmapCache:
            return self.pixmapCache[filename]
        else:
            if filename[-4:] == '.png':
                ptr = loadPNG(filename)
            elif filename[-4:] == '.jpg':
                ptr = loadJPG(filename)
                if not ptr:
                    ptr = loadPNG(filename)
            if ptr:
                self.pixmapCache[filename] = ptr
            return ptr

    def buildSkinpartEntry(self, data):
        global ListBoxImageLoaderQueue
        width = self.l.getItemSize().width()
        res = [None]
        ptr = None
        if data.type == 0:
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
                        10,
                        0,
                        width - 10,
                        50,
                        0,
                        RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                        str(data.title)
                        ))            
        else:
            if data.imagelink:
                if os.path.exists(str(data.imagepath)):
                    ptr = self.loadPixmap(str(data.imagepath))
                else:
                    ListBoxImageLoaderQueue.put((data, self))            
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
                        410,
                        0,
                        width - 420,
                        50,
                        0,
                        RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                        str(data.title)
                        ))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
                        410,
                        60,
                        width - 420,
                        50,
                        0,
                        RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                        str(data.description)
                        ))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
                        410,
                        110,
                        width - 420,
                        40,
                        1,
                        RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                        "Version: " + str(data.version)
                        ))	
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
                        410,
                        150,
                        width - 420,
                        40,
                        1,
                        RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                        "Erstellt von: " + str(data.creator)
                        ))
            res.append(MultiContentEntryPixmapAlphaTest(pos = (5,5),size = (400, 200),png = ptr,backcolor = None,backcolor_sel = None,options = BT_SCALE))           
        return res

    def isSelectable(self, data):
        return True

    def connectSelChanged(self, fnc):
        if fnc not in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        pass

    def getCurrentSelection(self):
        cur = self.l.getCurrentSelection()
        return cur

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)
        self.instance.setWrapAround(True)

    def preWidgetRemove(self, instance):
        instance.selectionChanged.get().remove(self.selectionChanged)
        instance.setContent(None)
        return

    def setList(self, list, mode):
        if mode == 0:
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(210)
        self.l.setBuildFunc(self.buildSkinpartEntry)
        self.l.setList(list)
        self.list = list

    def up(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveUp)
        return

    def down(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveDown)
        return

    def pageUp(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.pageUp)
        return

    def pageDown(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.pageDown)
        return

    def moveUp(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveUp)
        return

    def moveDown(self):
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveDown)
        return

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def updateListObject(self, index):
        self.l.invalidateEntry(index)

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def setMode(self, mode):
        self.mode = mode

    def getList(self):
        return self.list

class SkinpartsBrowser(Screen):
    skin = '''<screen name="SkinpartsBrowser" position="center,center" size="1200,600" title="Arctic Skinparts">
			 <widget name="SkinpartsList" position="0,0" size="1200,600" scrollbarMode="showOnDemand" scrollbarSliderBorderWidth="0" scrollbarWidth="5" scrollbarBackgroundPicture="/usr/share/enigma2/Arctic/pic/scrollbarbg.png" />


</screen>'''
    def __init__(self, session):    
        self.session = session
        Screen.__init__(self, session)
        self.title = _("Arctic Skin Parts") 
        self.categorylist = []
        self.listmode = 0
        self.catindex = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'InfobarActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'ColorActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'EPGSelectActions' ],
                                    {
                                        "ok": self.keySelect,
                                        "cancel": self.Cancel,
                                        }, -2)
        self["SkinpartsList"] = SkinpartList()
        self.onShown.append(self.getOnlineParts)

    def getOnlineParts(self):
        self.onShown.remove(self.getOnlineParts)
        try:
            request = Request('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/skinparts/skinparts.json')
            skinparts = urlopen(request, timeout=15).read()
            print str(skinparts)
            skinparts = json.loads(str(skinparts))
            skinparts = skinparts['skinparts']['skinpart']
            skincategories = {}
            for s in skinparts:
                print "Category:" +  str(s['category'])
                skincategories[str(s['category'])] = Skinpart(title = str(s['category']), type = 0)        
            for s in skinparts:
                sp = Skinpart(str(s['title']),str(s['filename']),str(s['link']),str(s['imagelink']),str(s['category']),str(s['description']),str(s['version']),str(s['creator']),1,s['dateadded'], index = len(skincategories[str(s['category'])].items))
                skincategories[str(s['category'])].items.append((sp,))        
            for key in sorted(skincategories.iterkeys()):
                self.categorylist.append((skincategories[key],))
            self["SkinpartsList"].setList(self.categorylist, 0)
        except Exception,  ex:
            print "Fehler: " +  str(ex)

    def keySelect(self):
        if self.listmode == 0:
            cur = self["SkinpartsList"].getCurrentSelection()[0]
            self.catindex = self["SkinpartsList"].getCurrentIndex()
            self["SkinpartsList"].setList(cur.items, 1)
            self.listmode = 1
            self["SkinpartsList"].moveToIndex(0)
        else:
            from PIL import Image
            item = self["SkinpartsList"].getCurrentSelection()[0]
            url = item.link
            target = "/usr/share/enigma2/Arctic/allScreens/" + item.filename
            urllib.urlretrieve (url, target)
            url = item.imagelink
            target = "/usr/share/enigma2/Arctic/preview/" + item.filename.replace(".xml", ".jpg").replace("skin_","preview_skin_")
            urllib.urlretrieve (url, target)
            img = Image.open(target).convert('RGBA')
            img = img.resize((400, 225))
            img.save(str(target.replace('.jpg', '.png')))
            os.remove(target)


    def Cancel(self):
        if self.listmode == 0:
            self.close()
        else:
            self.listmode = 0
            self["SkinpartsList"].setList(self.categorylist, 0)
            self["SkinpartsList"].moveUp()
            self["SkinpartsList"].moveDown()
            self["SkinpartsList"].moveToIndex(self.catindex)


class ArcticSetupScreen(ConfigListScreen, Screen):

    def __init__(self, session):    
        self.session = session
        Screen.__init__(self, session)
        self.title = _("Arctic Skin Setup")
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'InfobarActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'ColorActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'EPGSelectActions' ],
                                    {
                                        "ok": self.keySelect,
                                        "cancel": self.Cancel,
                                        "green": self.keyGreen,
                                        'red': self.Cancel,
                                        }, -1)
        self.list = [ ]
        self.buttonstyle = config.plugins.ArcticSetup.button.value
        self.colorstyle =  config.plugins.ArcticSetup.colorstyle.value
        self.versionstring = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/version','r').read()
        self.version = int(self.versionstring.replace('.',''))
        self.title = _("Arctic Skin Setup - Skin Version " + config.plugins.ArcticSetup.VersionString.value)        
        ConfigListScreen.__init__(self, self.list, session)
        self.createSetup()
        self.onShown.append(self.checkUpdate)

    def checkUpdate(self):
        self.onShown.remove(self.checkUpdate)
        CheckUpdate(self.session).checkForUpdate()

    def keySelect(self):
        ptime = config.plugins.ArcticSetup.primetime.value
        cur = self["config"].getCurrent()
        if cur == self.Update:
            self.onlineUpdate()





    def createSetup(self):

        self.Update = getConfigListEntry(_("Skin Update"), NoSave(ConfigNothing()))
        self.list.append(getConfigListEntry(_("Farbstil"),config.plugins.ArcticSetup.colorstyle, None))
        self.list.append(getConfigListEntry(_("Buttonstil"), config.plugins.ArcticSetup.button, None))
        self.list.append(getConfigListEntry(_("Primetime"),config.plugins.ArcticSetup.primetime, None))
        self.list.append(self.Update)

        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def onlineUpdate(self):
        CheckUpdate(self.session).checkForUpdate()

    def restartGUI(self, answer):
        if answer:
            self.session.open(Screens.Standby.TryQuitMainloop, 3)
        else:
            self.close()


    def Cancel(self):
        #config.plugins.ArcticSetup.save()
        for x in self["config"].list:
            try:
                x[1].save()  
            except:
                pass
        if self.colorstyle !=  config.plugins.ArcticSetup.colorstyle.value:
            update = open('/usr/share/enigma2/Arctic/skin.xml','r').read()
            update = update.replace('badges/video/', '')
            update = update.replace('path="audioicon"', 'path="pic/audioicon"')
            file = open('/usr/share/enigma2/Arctic/skin.xml','w')
            file.write(str(update))
            file.close()            
            for root, dirs, files in os.walk('/usr/share/enigma2/Arctic/allScreens', topdown=True, onerror=None, followlinks=False):    
                files = [file for file in files if file.endswith((".xml"))]
                for file in files:
                    rep = open(os.path.join(root,file),'r').read()
                    u = rep.replace('badges/video/', '')
                    u = u.replace('path="audioicon"', 'path="pic/audioicon"')
                    f = open(os.path.join(root,file),'w')
                    f.write(u)
                    f.close()             
            if config.plugins.ArcticSetup.colorstyle.value == "0":
                print "Linking light"
                os.popen('ln -sfn /usr/share/enigma2/Arctic/light/*.* /usr/share/enigma2/Arctic/pic')
                os.popen('ln -sfn /usr/share/enigma2/Arctic/light/audioicon /usr/share/enigma2/Arctic/pic')
                #symlink('/usr/share/enigma2/Arctic/light/*.*', '/usr/share/enigma2/Arctic/pic')
                #symlink('/usr/share/enigma2/Arctic/light/audioicon', '/usr/share/enigma2/Arctic/pic')
            elif config.plugins.ArcticSetup.colorstyle.value == "1":
                print "Linking dark"
                os.popen('ln -sfn /usr/share/enigma2/Arctic/dark/*.* /usr/share/enigma2/Arctic/pic')
                os.popen('ln -sfn /usr/share/enigma2/Arctic/dark/audioicon /usr/share/enigma2/Arctic/pic')                
                #symlink('/usr/share/enigma2/Arctic/dark/*.*', '/usr/share/enigma2/Arctic/pic')
                #symlink('/usr/share/enigma2/Arctic/dark/audioicon', '/usr/share/enigma2/Arctic/pic')               
            elif config.plugins.ArcticSetup.colorstyle.value == "2":
                print "Linking  black"
                os.popen('ln -sfn /usr/share/enigma2/Arctic/black/*.* /usr/share/enigma2/Arctic/pic')
                os.popen('ln -sfn /usr/share/enigma2/Arctic/black/audioicon /usr/share/enigma2/Arctic/pic')                
                #symlink('/usr/share/enigma2/Arctic/black/*.*', '/usr/share/enigma2/Arctic/pic')
                #symlink('/usr/share/enigma2/Arctic/black/audioicon', '/usr/share/enigma2/Arctic/pic')
        #try:
		#			from enigma import eWindowStyleManager, eWindowStyleSkinned, eSize, eListboxPythonStringContent, eListboxPythonConfigContent
#
#					from skin import parseSize, parseFont, parseColor
#					try:
#						from skin import parseValue
#					except:
#						pass
#				
#					stylemgr = eWindowStyleManager.getInstance()
#					desktop = getDesktop(0)
#					styleskinned = eWindowStyleSkinned()
#
#				
#			
#					skin_path = resolveFilename(SCOPE_CURRENT_SKIN) + "skin_user_colors.xml"
#					if not fileExists(skin_path):
#						print("DEFAULT SKIN USED")
#						skin_path = resolveFilename(SCOPE_CURRENT_SKIN) + "skin.xml"
#					else: print("skin_user_colors.xml USED")
#					file_path = resolveFilename(SCOPE_SKIN)
#				
#					conf = xml.etree.cElementTree.parse(skin_path)
#					for x in conf.getroot():
#						if x.tag == "colors":
#							skin.colorNames = dict()
#							skin.colorNamesHuman = dict()		
#							colors =  x
#							for y in colors:
#								print str(y)
#								
#								name =  y.get("name")
#								color = y.get("value")
#								print("Parsing Color: " + str(name))
#								print("Parsing Value: " + str(color))
#								if name and color:
#										skin.colorNames[name] = parseColor(color)
#										if color[0] != '#':
#											for key in skin.colorNames:
#												if key == color:
#													skin.colorNamesHuman[name] = skin.colorNamesHuman[key]
#													break
#										else:
#											humancolor = color[1:]
#											if len(humancolor) >= 6:
#												skin.colorNamesHuman[name] = int(humancolor,16)
#								else:
#										print ("need color and name, got %s %s" % (name, color))							
#									
#								
#		
#						elif x.tag == "windowstyle" and x.get("id") == "0":
#							font = gFont("Regular", 20)
#							offset = eSize(20, 5)
#							windowstyle = x
#							for x in windowstyle:
#								if x.tag == "title":
#									font = parseFont(x.get("font"), ((1,1),(1,1)))
#									offset = parseSize(x.get("offset"), ((1,1),(1,1)))
#								elif x.tag == "color":
#									colorType = x.get("name")
#									color = parseColor(x.get("color"))
#									try:
#										styleskinned.setColor(eWindowStyleSkinned.__dict__["col" + colorType], color)
#									except:
#										pass
#								elif x.tag == "borderset":
#									bsName = str(x.get("name"))
#									borderset =  x
#									for x in borderset:
#										if x.tag == "pixmap":
#											bpName = x.get("pos")
#											styleskinned.setPixmap(eWindowStyleSkinned.__dict__[bsName], eWindowStyleSkinned.__dict__[bpName], LoadPixmap(file_path + x.get("filename"), desktop))
#									print("BORDERSET CHANGED")
#							styleskinned.setTitleFont(font)
#							styleskinned.setTitleOffset(offset)
#						
#				
#	
#					pngcache =  []
#					#skin.dom_skins = []
#					for x in skin.pngcache:
#						print("RELOADING IMAGE: " + str(x[0]))
#						ptr = loadPixmap(x[0], desktop)
#						pngcache.append((x[0],ptr))
#					skin.pngcache = pngcache
#					#skin.load_modular_files()
#					#skin.loadSkin('Arctic/skin.xml')
#					stylemgr.setStyle(0, styleskinned)
#					self.session.infobar = None
#					IB = Screens.InfoBar.InfoBar(self.session)
#					#self.session.open(IB)
#					self.session.infobar = IB
 #       except Exception, ex:
#					print("FEHLER BEIM SETZEN DES NEUEN STYLES: " + str(ex))            
#

        if self.buttonstyle != config.plugins.ArcticSetup.button.value:
            update = open('/usr/share/enigma2/Arctic/skin.xml','r').read()
            if config.plugins.ArcticSetup.button.value == "1":
                update = update.replace('text="a"','text="I"')
                for root, dirs, files in os.walk('/usr/share/enigma2/Arctic/allScreens', topdown=True, onerror=None, followlinks=False):    
                    files = [file for file in files if file.endswith((".xml"))]
                    for file in files:
                        rep = open(os.path.join(root,file),'r').read()
                        u = rep.replace('text="a"','text="I"')
                        f = open(os.path.join(root,file),'w')
                        f.write(u)
                        f.close()

            else:                
                update = update.replace('text="a"','text="I"')
                for root, dirs, files in os.walk('/usr/share/enigma2/Arctic/allScreens', topdown=True, onerror=None, followlinks=False):    
                    files = [file for file in files if file.endswith((".xml"))]
                    for file in files:
                        rep = open(os.path.join(root,file),'r').read()
                        u = rep.replace('text="I"','text="a"')
                        f = open(os.path.join(root,file),'w')
                        f.write(u)
                        f.close()

            file = open('/usr/share/enigma2/Arctic/skin.xml','w')
            file.write(str(update))
            file.close()
	if self.buttonstyle != config.plugins.ArcticSetup.button.value or self.colorstyle !=  config.plugins.ArcticSetup.colorstyle.value:
            self.session.openWithCallback(self.restartGUI, MessageBox, _("Arctic wurde erfolgreich aktualisiert!\nWollen Sie jetzt die Enigma2 GUI neu starten?"), MessageBox.TYPE_YESNO)

        else:                        
            self.session.open(MessageBox, "Die Einstellungen wurden gesichert...", MessageBox.TYPE_INFO, timeout = 3)
            ConfigListScreen.cancelConfirm(self, True)




    def keyGreen(self):
        self.session.openWithCallback(self.skinpartsClosed, SkinpartsBrowser)
    def skinpartsClosed(self):
        pass