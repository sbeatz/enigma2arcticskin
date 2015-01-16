# -*- coding: utf-8 -*-
import re, os, threading
from re import findall, search, split, sub
from enigma import RT_WRAP, RT_VALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, gFont, eListbox,eListboxPythonMultiContent, getDesktop
from Components.GUIComponent import GUIComponent
from os import path as os_path, listdir as os_listdir, chdir as os_chdir, getcwd as os_getcwd
from Screens.Screen import Screen
import os
import Screens.Standby
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.ChannelSelection import SimpleChannelSelection
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Console import Console
import shutil
from Components.Pixmap import Pixmap, MultiPixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigDirectory, NoSave
import urllib
from Components.About import about

class ArcticSetupScreen(ConfigListScreen, Screen):
    skin = """
            <screen name="ArcticSetupScreen" position="center,center" size="880,600" flags="wfNoBorder" backgroundColor="#ff000000" title="Artic Setup">
            <eLabel backgroundColor="#00edeceb" position="0,0" size="880,600" zPosition="-1" />
    <widget backgroundColor="#00edeceb" font="Regular;26" foregroundColor="#002c2d2b" position="30,15" render="Label" size="650,35" source="Title" transparent="1" />
    <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/key_red.png" position="30,555" size="20,20" />
    <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/key_green.png" position="230,555" size="20,20" />
    <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/key_yellow.png" position="430,555" size="20,20" />
    <ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/key_blue.png" position="630,555" size="20,20" />
    <widget foregroundColor="#002c2d2b" backgroundColor="#00edeceb" font="Regular;21" halign="left" render="Label" source="key_red" position="60,545" size="160,40" transparent="1" valign="center" />
    <widget foregroundColor="#002c2d2b" backgroundColor="#00edeceb" font="Regular;21" halign="left" render="Label" source="key_green" position="260,545" size="160,40" transparent="1" valign="center" />
    <widget foregroundColor="#002c2d2b" backgroundColor="#00edeceb" font="Regular;21" halign="left" render="Label" source="key_yellow" position="460,545" size="160,40" transparent="1" valign="center" />
    <widget foregroundColor="#002c2d2b" backgroundColor="#00edeceb" font="Regular;21" halign="left" render="Label" source="key_blue" position="660,544" size="160,40" transparent="1" valign="center" />
    <widget backgroundColor="#00edeceb" name="screenshot" position="0,205" size="900,506" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/infobar1.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/infobar2.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/infobar3.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/infobar4.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/infobar5.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/infobar6.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/kanalliste1.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/kanalliste2.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/kanalliste3.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/movieselection1.png,/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/movieselection2.png"/>
    <widget backgroundColor="#00edeceb" itemHeight="50" enableWrapAround="1" name="config" position="30,55" scrollbarMode="showOnDemand" size="820,150" transparent="1" />                            
            </screen>"""

    def __init__(self, session):    
        self.session = session
        Screen.__init__(self, session)
        self.title = _("Arctic Skin Setup")
        self.imageversion = str(about.getVTiVersionString()).replace('.', '')
        
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
            "green": self.keyGreen,
            "red": self.keyRed,
            "blue": self.keyBlue,
            "yellow": self.keyYellow,
            "cancel": self.Cancel,
            "left": self.keyLeft,
            "right": self.keyRight,
            "1": self.patchMediaPortal,
            "2": self.patchSerienRecorder,
            "info": self.updateFiles,
        }, -2)
        self["screenshot"] = MultiPixmap()
        self["key_red"] = StaticText("Skin erstellen")
        self["key_green"] = StaticText("")
        self["key_blue"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self.sysfilesSaved = self.checkFileSafe()
        self.onlineversion = 0
        self.sysfilesOverwritten = self.checkFileOverwritten()
        if self.sysfilesSaved == False:
            self["key_green"] = StaticText("Systemdateien sichern")
        else:
            self["key_blue"] = StaticText("Systemdateien wiederherstellen")

        if self.sysfilesOverwritten == False:
            self["key_yellow"] = StaticText("Systemdateien ueberschreiben")
        versionstring = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/version','r').read()
        self.version = int(versionstring)
        self.checkUpdate()
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session)
        self.createSetup()

    def updateFiles(self):
        urllib.urlretrieve('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/baseskin.xml','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/baseskin.xml')
    
    def checkUpdate(self):
        urllib.urlretrieve('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/version','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/onlineversion')
        onlineversionstring = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/onlineversion','r').read()
        self.onlineversion = int(onlineversionstring)
        if self.onlineversion > self.version:
            self.session.openWithCallback(self.doUpdate, MessageBox, _(u"Es ist ein Update für Arctic Skin verfügbar - Möchten Sie es jetzt installieren?"), MessageBox.TYPE_YESNO)
    
    def doUpdate(self, answer):
        if answer:
            urllib.urlretrieve('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/Setup.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/Setup.py')
            urllib.urlretrieve('https://raw.githubusercontent.com/sbeatz/enigma2arcticskin/master/plugin.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/plugin.py')
            file = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/version','w')
            file.write(str(self.onlineversion)
            file.close()
            self.session.openWithCallback(self.restartGUI, MessageBox, _("Die Arctic Skin App wurde erfolgreich aktualisiert!\nWollen Sie jetzt die Enigma2 GUI neu starten?"), MessageBox.TYPE_YESNO)
        
    def createSetup(self):
        self.updateFiles()
        if os_path.exists('/usr/share/enigma2/Arctic') == False:
            self.session.open(MessageBox, _("Die Arctic Skin ist nicht auf dem System installiert!\n Bitte zuerst die Skin installieren! erfolgreich erstellt!"), MessageBox.TYPE_INFO)
            self.close()
        self.list = []
        self.list.append(getConfigListEntry(_("Style Infobar"), config.plugins.ArcticSetup.InfobarStyle))
        self.list.append(getConfigListEntry(_("Style Channellist"), config.plugins.ArcticSetup.ChannelListStyle))
        self.list.append(getConfigListEntry(_("Style Movielist"), config.plugins.ArcticSetup.MovieListStyle))
        self.list.append(getConfigListEntry(_("Blockmode Textboxen"), config.plugins.ArcticSetup.Blockmode))
        #self.list.append(getConfigListEntry(_("FadeIn - nur VTI8.0"), config.plugins.ArcticSetup.EnableFadeIn))
        self["config"].list = self.list
        self["config"].l.setList(self.list)


    def restartGUI(self, answer):
        if answer:
            self.session.open(Screens.Standby.TryQuitMainloop, 3)
        else:
            self.close()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        cur = self["config"].getCurrent()
        if str(cur[0]) == "Style Infobar":
            self["screenshot"].setPixmapNum(int(str(cur[1].value)))
        if str(cur[0]) == "Style Channellist":
            self["screenshot"].setPixmapNum(6 + int(str(cur[1].value)))
        if str(cur[0]) == "Style Movielist":
            self["screenshot"].setPixmapNum(9 + int(str(cur[1].value)))


    def keyRight(self):
        ConfigListScreen.keyRight(self)
        cur = self["config"].getCurrent()
        if str(cur[0]) == "Style Infobar":
            self["screenshot"].setPixmapNum(int(str(cur[1].value)))
        if str(cur[0]) == "Style Channellist":
            self["screenshot"].setPixmapNum(6 + int(str(cur[1].value)))
        if str(cur[0]) == "Style Movielist":
            self["screenshot"].setPixmapNum(9 + int(str(cur[1].value)))

    def keyRed(self):
        for x in self["config"].list:
            x[1].save()

        baseskin = open('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/baseskin.xml','r').read()

        if str(config.plugins.ArcticSetup.InfobarStyle.value) == "0":
            baseskin = baseskin.replace('name="InfoBar1"', 'name="InfoBar"')
            baseskin = baseskin.replace('name="SecondInfoBar1"', 'name="SecondInfoBar"')
        elif str(config.plugins.ArcticSetup.InfobarStyle.value)== "1":
            baseskin = baseskin.replace('name="InfoBar2"', 'name="InfoBar"')
            baseskin = baseskin.replace('name="SecondInfoBar2"', 'name="SecondInfoBar"')
        elif str(config.plugins.ArcticSetup.InfobarStyle.value) == "2":
            baseskin = baseskin.replace('name="InfoBar3"', 'name="InfoBar"')
            baseskin = baseskin.replace('name="SecondInfoBar3"', 'name="SecondInfoBar"')
        elif str(config.plugins.ArcticSetup.InfobarStyle.value) == "3":
            baseskin = baseskin.replace('name="InfoBar4"', 'name="InfoBar"')
            baseskin = baseskin.replace('name="SecondInfoBar4"', 'name="SecondInfoBar"')
        elif str(config.plugins.ArcticSetup.InfobarStyle.value) == "4":
            baseskin = baseskin.replace('name="InfoBar5"', 'name="InfoBar"')
            baseskin = baseskin.replace('name="SecondInfoBar5"', 'name="SecondInfoBar"')
        elif str(config.plugins.ArcticSetup.InfobarStyle.value) == "5":
            baseskin = baseskin.replace('name="InfoBar6"', 'name="InfoBar"')
            baseskin = baseskin.replace('name="SecondInfoBar6"', 'name="SecondInfoBar"')
        if str(config.plugins.ArcticSetup.ChannelListStyle.value) == "0":
            baseskin = baseskin.replace('name="ChannelSelection1"', 'name="ChannelSelection"')
        elif str(config.plugins.ArcticSetup.ChannelListStyle.value) == "1":
            baseskin = baseskin.replace('name="ChannelSelection2"', 'name="ChannelSelection"')
        elif str(config.plugins.ArcticSetup.ChannelListStyle.value) == "2":
            baseskin = baseskin.replace('name="ChannelSelection3"', 'name="ChannelSelection"')
        if str(config.plugins.ArcticSetup.MovieListStyle.value) == "0":
            baseskin = baseskin.replace('name="MovieSelection1"', 'name="MovieSelection"')
        elif str(config.plugins.ArcticSetup.MovieListStyle.value) == "1":
            baseskin = baseskin.replace('name="MovieSelection2"', 'name="MovieSelection"')
        if config.plugins.ArcticSetup.Blockmode.value == False:
            baseskin = baseskin.replace('halign="block"', 'halign="left"')
        if int(str(self.imageversion)) > 809:
            baseskin = baseskin.replace('scrollbarWidth="5"', 'scrollbarWidth="5" scrollbarBackgroundPicture="Arctic/pic/scrollbarbg.png"')
        file = open('/usr/share/enigma2/Arctic/skin.xml','w')
        file.write(baseskin)
        file.close()
        self.session.openWithCallback(self.restartGUI, MessageBox, _("Die Arctic Skin wurde erfolgreich erstellt!\nWollen Sie jetzt die Enigma2 GUI neu starten?"), MessageBox.TYPE_YESNO)


    def Cancel(self):
        ConfigListScreen.cancelConfirm(self, True)
    
    def keyYellow(self):
        if self.sysfilesOverwritten == False:
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/ConfigList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/ConfigList.py','/usr/lib/enigma2/python/Components/ConfigList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/ChoiceList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/ChoiceList.py','/usr/lib/enigma2/python/Components/ChoiceList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/EpgList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/EpgList.py','/usr/lib/enigma2/python/Components/EpgList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/MovieList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/MovieList.py','/usr/lib/enigma2/python/Components/MovieList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/TimerList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/TimerList.py','/usr/lib/enigma2/python/Components/TimerList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/ServiceList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/ServiceList.py','/usr/lib/enigma2/python/Components/ServiceList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/PluginList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/PluginList.py','/usr/lib/enigma2/python/Components/PluginList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/MessageBox.py','/usr/lib/enigma2/python/Screens/MessageBox.py')
            self.session.openWithCallback(self.restartGUI, MessageBox, _("Die Systemdateien wurden erfolgreich ersetzt!\nWollen Sie jetzt die Enigma2 GUI neu starten?"), MessageBox.TYPE_YESNO)


    def keyBlue(self):
        if self.sysfilesSaved == True:
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ConfigList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ConfigList.py','/usr/lib/enigma2/python/Components/ConfigList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ChoiceList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ChoiceList.py','/usr/lib/enigma2/python/Components/ChoiceList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/EpgList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/EpgList.py','/usr/lib/enigma2/python/Components/EpgList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/MovieList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/MovieList.py','/usr/lib/enigma2/python/Components/MovieList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/TimerList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/TimerList.py','/usr/lib/enigma2/python/Components/TimerList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ServiceList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ServiceList.py','/usr/lib/enigma2/python/Components/ServiceList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/PluginList.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/PluginList.py','/usr/lib/enigma2/python/Components/PluginList.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/Screen.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/Screen.py','/usr/lib/enigma2/python/Screens/Screen.py')
            if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/MessageBox.py'):
                shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/MessageBox.py','/usr/lib/enigma2/python/Screens/MessageBox.py')
            self.session.openWithCallback(self.restartGUI, MessageBox, _("Die Systemdateien wurden erfolgreich wiederhergestellt!\nWollen Sie jetzt die Enigma2 GUI neu starten?"), MessageBox.TYPE_YESNO)


    def keyGreen(self):
        if self.sysfilesSaved == False:
            shutil.copyfile('/usr/lib/enigma2/python/Components/ConfigList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ConfigList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Components/ChoiceList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ChoiceList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Components/EpgList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/EpgList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Components/MovieList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/MovieList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Components/TimerList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/TimerList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Components/ServiceList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ServiceList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Components/PluginList.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/PluginList.py')
            shutil.copyfile('/usr/lib/enigma2/python/Screens/Screen.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/Screen.py')
            shutil.copyfile('/usr/lib/enigma2/python/Screens/MessageBox.py','/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/MessageBox.py')

    def checkFileSafe(self):
        if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systembackup/ConfigList.py'):
            return True
        else:
            return False

    def checkFileOverwritten(self):
        if os_path.exists('/usr/lib/enigma2/python/Screens/MessageBox.py'):
            checkstring = open('/usr/lib/enigma2/python/Screens/MessageBox.py','r').read()
            if '#patchedbyArcticSkin' in checkstring:
                return True
            else:
                return False


    def patchSerienRecorder(self):
        if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/serienrecorder/SerienRecorder.py'):
            checkstring = open('/usr/lib/enigma2/python/Plugins/Extensions/serienrecorder/SerienRecorder.py','r').read()
            checkstring = checkstring.replace("self.chooseMenuList.l.setFont(0, gFont('Regular', 20 + int(config.plugins.serienRec.listFontsize.value)))","self.chooseMenuList.l.setFont(0, gFont('Regular', 20 + int(config.plugins.serienRec.listFontsize.value)));self.chooseMenuList.l.setFont(1, gFont('Regular', 16 + int(config.plugins.serienRec.listFontsize.value)))")
            checkstring = checkstring.replace("self.chooseMenuList.l.setItemHeight(25)","self.chooseMenuList.l.setItemHeight(50)")
            checkstring = checkstring.replace("self['title'].instance.setForegroundColor","#self['title'].instance.setForegroundColor")
            checkstring = checkstring.replace("self['headline'].instance.setForegroundColor","#self['headline'].instance.setForegroundColor")
            checkstring = checkstring.replace(", colorYellow","")
            checkstring = checkstring.replace("self.chooseMenuList.l.setItemHeight(70)","self.chooseMenuList.l.setItemHeight(100)")
            checkstring = checkstring.replace("self.chooseMenuList.l.setItemHeight(50)","self.chooseMenuList.l.setItemHeight(100)")
            checkstring = checkstring.replace(", SerieColor","")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 40, 29, 350, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 40, 29, 350, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 400, 29, 450, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 400, 29, 450, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 400, 29, 450, 24, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 400, 29, 450, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 40, 49, 350, 24, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 40, 49, 350, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 400, 49, 450, 24, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 400, 49, 450, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 40, 29, 250, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 40, 29, 250, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 300, 29, 500, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 300, 29, 500, 24, 1,")
            checkstring = checkstring.replace(", setFarbe","")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 110, 29, 200, 36, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 110, 44, 200, 36, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 375, 29, 500, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 375, 44, 500, 36, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 50, 29, 200, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 50, 44, 200, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 300, 29, 500, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 300, 44, 500, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 110, 29, 200, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 110, 44, 200, 24, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 110, 3, 200, 26, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 110, 3, 200, 36, 0,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 375, 3, 500, 26, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 375, 3, 500, 36, 0,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 00, 5, 80, 40, picon),","(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 00, 20, 80, 40, picon),")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 100, 3, 200, 26, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 100, 4, 200, 36, 0,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 100, 29, 150, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 100, 44, 150, 36, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 365, 3, 500, 26, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 365, 4, 500, 36, 0,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 365, 29, 500, 18, 0,","(eListboxPythonMultiContent.TYPE_TEXT, 365, 44, 500, 36, 1,")
            checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 5, 0, 800, 30, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, name)","(eListboxPythonMultiContent.TYPE_TEXT, 5, 0, 800, 50, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, name)")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            #checkstring = checkstring.replace("","")
            changefile = open('/usr/lib/enigma2/python/Plugins/Extensions/serienrecorder/SerienRecorder.py','w')
            changefile.write(checkstring)
            changefile.close()
        
    def patchMediaPortal(self):
        if os_path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal'):
            shutil.copyfile('/usr/lib/enigma2/python/Plugins/Extensions/ArcticSetup/systemfiles/plugin.pyo','/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/plugin.pyo')
            for root, dirs, files in os.walk('/usr/lib/enigma2/python/Plugins/Extensions/MediaPortal/additions', topdown=True, onerror=None,followlinks=False):
                files = [file for file in files if file.endswith('.py')]
                for file in files:
                    filepath = os.path.join(root, file)
                    checkstring = open(filepath,'r').read()
                    checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 20, 0, 860, 25", "(eListboxPythonMultiContent.TYPE_TEXT, 20, 7, 860, 40")
                    checkstring = checkstring.replace("(eListboxPythonMultiContent.TYPE_TEXT, 20, 7, 860, 40, 0, RT_HALIGN_CENTER |", "(eListboxPythonMultiContent.TYPE_TEXT, 20, 7, 860, 40, 0, RT_HALIGN_LEFT |")
                    checkstring = checkstring.replace("self.chooseMenuList.l.setFont(0, gFont('mediaportal', 23))", "self.chooseMenuList.l.setFont(0, gFont('Regular', 36))")
                    checkstring = checkstring.replace("self.chooseMenuList.l.setFont(0, gFont('Regular', 36))", "self.chooseMenuList.l.setFont(0, gFont('Regular', 24))")                    
                    checkstring = checkstring.replace("self.chooseMenuList.l.setItemHeight(25)", "self.chooseMenuList.l.setItemHeight(50)")
                    changefile = open(filepath,'w')
                    changefile.write(checkstring)
                    changefile.close()
        
