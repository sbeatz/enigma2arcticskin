import re, os, threading
from Setup import ArcticSetupScreen
from Components.ConfigList import ConfigList, ConfigListScreen
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigInteger, ConfigSelection, getConfigListEntry, ConfigText, ConfigDirectory, ConfigYesNo, configfile, ConfigSelection, ConfigSubsection, ConfigPIN, NoSave, ConfigNothing, ConfigClock
import skin
import pyinotify
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer
config.plugins.ArcticSetup = ConfigSubsection()
config.plugins.ArcticSetup.Version = ConfigInteger(default = 200)
config.plugins.ArcticSetup.VersionString = ConfigText(default = "2.0.0")
config.plugins.ArcticSetup.primetime = ConfigClock(default=((20 * 3600)+ (15*60)))
config.plugins.ArcticSetup.button = ConfigSelection(choices = [("0", "Rund"), ("1", "Linie")], default = "0")
config.plugins.ArcticSetup.colorstyle = ConfigSelection(choices = [("0", "Light"), ("1", "Dark"), ("2", "Black")], default = "0")
config.plugins.ArcticSetup.AutoSwitch = ConfigYesNo(default = True)
config.plugins.ArcticSetup.daycolorstyle = ConfigSelection(choices = [("0", "Light"), ("1", "Dark"), ("2", "Black")], default = "0")
config.plugins.ArcticSetup.nightcolorstyle = ConfigSelection(choices = [("0", "Light"), ("1", "Dark"), ("2", "Black")], default = "0")
config.plugins.ArcticSetup.nighttime = ConfigClock(default=6 * 3600)
config.plugins.ArcticSetup.morningtime = ConfigClock(default=6 * 3600)
CHANGENOTIFIER = None
class skinswitch():
    def __init__(self):
        self.session =  None
        self.timer = eTimer()
        self.timer.callback.append(self.daily)
    def saveSession(self, session):
        self.session = session
    def start(self):
        self.timer.stop()
        now = datetime.datetime.now()
        now = now.hour * 60 + now.minute
        day_time = config.plugins.ArcticSetup.nighttime.value[0] * 60 + config.plugins.ArcticSetup.nighttime.value[1]
        night_time =  config.plugins.ArcticSetup.morningtime.value[0] * 60 + config.plugins.ArcticSetup.morningtime.value[1]

        if now < day_time:
            start_time = day_time - now
        else:
            if now < night_time:
                start_time = night_time - now
            else:
                start_time = 1440 - now + day_time
        self.timer.start(start_time * 60 * 1000, True)
        now = str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        return
    def loadPixmap(self, path, desktop):
        cached = False
        option = path.find("#")
        if option != -1:
            options = path[option+1:].split(',')
            path = path[:option]
            cached = "cached" in options
        ptr = LoadPixmap(path, desktop, cached)
        if ptr is None:
            print("pixmap file %s not found!" % (path))
        return ptr            
    def daily(self):
        self.timer.stop()
        self.runUpdate()
        self.timer = eTimer()
        self.timer.callback.append(self.runUpdate)
        now = datetime.datetime.now()
        now = now.hour * 60 + now.minute
        day_time = config.plugins.ArcticSetup.nighttime.value[0] * 60 + config.plugins.ArcticSetup.nighttime.value[1]
        night_time =  config.plugins.ArcticSetup.morningtime.value[0] * 60 + config.plugins.ArcticSetup.morningtime.value[1]
        if now < day_time:
            start_time = day_time - now
        else:
            if now < night_time:
                start_time = night_time - now
            else:
                start_time = 1440 - now + day_time
        self.timer.start(start_time * 60 * 1000, False)
        now = str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))


    def runUpdate(self):
        now = str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        try:
            from enigma import eWindowStyleManager, eWindowStyleSkinned, eSize, eListboxPythonStringContent, eListboxPythonConfigContent
            try:
                from enigma import eWindowStyleScrollbar
            except:
                pass
            from skin import parseSize, parseFont, parseColor
            try:
                from skin import parseValue
            except:
                pass

            stylemgr = eWindowStyleManager.getInstance()
            desktop = getDesktop(0)
            styleskinned = eWindowStyleSkinned()

            try:
                stylescrollbar = eWindowStyleScrollbar()
                skinScrollbar = True
            except:
                skinScrollbar = False


            skin_path = resolveFilename(SCOPE_CURRENT_SKIN) + "skin_user_colors.xml"
            if not fileExists(skin_path):
                skin_path = resolveFilename(SCOPE_CURRENT_SKIN) + "skin.xml"
            file_path = resolveFilename(SCOPE_SKIN)

            conf = xml.etree.cElementTree.parse(skin_path)
            for x in conf.getroot():
                if x.tag == "colors":
                    colors =  x
                    for x in colors:
                        if x.tag ==  "value":
                            name =  x.get("name")
                            color = x.get("value")
                            if name and color:
                                skin.colorNames[name] = parseColor(color)
                                if color[0] != '#':
                                    for key in skin.colorNames:
                                        if key == color:
                                            skin.colorNamesHuman[name] = skin.colorNamesHuman[key]
                                            break
                                else:
                                    humancolor = color[1:]
                                    if len(humancolor) >= 6:
                                        skin.colorNamesHuman[name] = int(humancolor,16)
                            else:
                                raise SkinError("need color and name, got %s %s" % (name, color))							



                elif x.tag == "windowstyle" and x.get("id") == "0":
                    font = gFont("Regular", 20)
                    offset = eSize(20, 5)
                    windowstyle = x
                    for x in windowstyle:
                        if x.tag == "title":
                            font = parseFont(x.get("font"), ((1,1),(1,1)))
                            offset = parseSize(x.get("offset"), ((1,1),(1,1)))
                        elif x.tag == "color":
                            colorType = x.get("name")
                            color = parseColor(x.get("color"))
                            try:
                                styleskinned.setColor(eWindowStyleSkinned.__dict__["col" + colorType], color)
                            except:
                                pass
                        elif x.tag == "borderset":
                            bsName = str(x.get("name"))
                            borderset =  x
                            for x in borderset:
                                if x.tag == "pixmap":
                                    bpName = x.get("pos")
                                    styleskinned.setPixmap(eWindowStyleSkinned.__dict__[bsName], eWindowStyleSkinned.__dict__[bpName], LoadPixmap(file_path + x.get("filename"), desktop))
                    styleskinned.setTitleFont(font)
                    styleskinned.setTitleOffset(offset)


            stylemgr.setStyle(0, styleskinned)
            from enigma import getDesktop			
            desktop = getDesktop(0)
            pngcache =  []
            for x in skin.pngcache:
                ptr = loadPixmap(x[0], desktop)
                pngcache.append((x[0],ptr))
            skin.pngcache = pngcache

        except:
            print("FEHLER BEIM SETZEN DES NEUEN STYLES")




def main(session, **kwargs):
    session.open(ArcticSetupScreen)
def Arctic_Init_shutdown():
    global CHANGENOTIFIER
    if CHANGENOTIFIER:
        CHANGENOTIFIER.stop()

def Arctic_Init_autostart(reason, **kwargs):
    global CHANGENOTIFIER
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_CREATE(self, event):
            if str(event.pathname) == '/usr/share/enigma2/Arctic/skin_user_colors.xml':
                rep = open(str(event.pathname),'r').read()
                if rep.startswith('<!--Black-->'):
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/black/*.* /usr/share/enigma2/Arctic/pic')
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/black/skin_default/*.* /usr/share/enigma2/Arctic/skin_default')
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/black/audioicon /usr/share/enigma2/Arctic/pic')
                elif rep.startswith('<!--Dark-->'):
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/dark/*.* /usr/share/enigma2/Arctic/pic')
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/dark/skin_default/*.* /usr/share/enigma2/Arctic/skin_default')
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/dark/audioicon /usr/share/enigma2/Arctic/pic')
                elif rep.startswith('<!--Light-->'):
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/light/*.* /usr/share/enigma2/Arctic/pic')
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/light/skin_default/*.* /usr/share/enigma2/Arctic/skin_default')
                    os.popen('ln -sfn /usr/share/enigma2/Arctic/light/audioicon /usr/share/enigma2/Arctic/pic')
        def process_IN_DELETE(self, event):
            if str(event.pathname) == '/usr/share/enigma2/Arctic/skin_user_colors.xml':
                os.popen('ln -sfn /usr/share/enigma2/Arctic/light/*.* /usr/share/enigma2/Arctic/pic')
                os.popen('ln -sfn /usr/share/enigma2/Arctic/light/skin_default/*.* /usr/share/enigma2/Arctic/skin_default')
                os.popen('ln -sfn /usr/share/enigma2/Arctic/light/audioicon /usr/share/enigma2/Arctic/pic')	
        
        
    if 'session' in kwargs:
        session = kwargs['session']
        if not os.path.exists("/usr/share/enigma2/Arctic/skin_user_colors.xml"):
            os.popen('ln -sfn /usr/share/enigma2/Arctic/colors_Light.xml /usr/share/enigma2/Arctic/skin_user_colors.xml')
            os.popen('ln -sfn /usr/share/enigma2/Arctic/light/*.* /usr/share/enigma2/Arctic/pic')
            os.popen('ln -sfn /usr/share/enigma2/Arctic/light/skin_default/*.* /usr/share/enigma2/Arctic/skin_default')
            os.popen('ln -sfn /usr/share/enigma2/Arctic/light/audioicon /usr/share/enigma2/Arctic/pic')			 

        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE 
        wm1 = pyinotify.WatchManager()
        s1 = pyinotify.Stats()
        wm1.add_watch('/usr/share/enigma2/Arctic/', mask, rec=False, auto_add=False, do_glob=False, quiet=True)
        CHANGENOTIFIER = pyinotify.ThreadedNotifier(wm1, default_proc_fun=EventHandler(s1))
        CHANGENOTIFIER.start()
        if config.plugins.ArcticSetup.AutoSwitch.value:
            autoswitch =  skinswitch()
            autoswitch.saveSession(session)
            try:
                autoswitch.start()
            except Exception, ex:
                print("Start des Skinswitchers fehlgeschlagen")


def Plugins(**kwargs):
    list = []
    list.append(PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART], fnc=Arctic_Init_autostart, wakeupfnc=Arctic_Init_shutdown))
    list.append(PluginDescriptor(name="Arctic Skin-Setup", description=_("Arctic Skin-Setup"), where = [PluginDescriptor.WHERE_PLUGINMENU], fnc=main))
    return list