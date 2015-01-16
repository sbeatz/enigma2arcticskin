import re, os, threading
from Setup import ArcticSetupScreen
from Components.ConfigList import ConfigList, ConfigListScreen
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigInteger, ConfigSelection, getConfigListEntry, ConfigText, ConfigDirectory, ConfigYesNo, configfile, ConfigSelection, ConfigSubsection, ConfigPIN, NoSave, ConfigNothing, ConfigClock

config.plugins.ArcticSetup = ConfigSubsection()
config.plugins.ArcticSetup.InfobarStyle = ConfigSelection(choices = [("0", _("InfoBar1")), ("1", _("InfoBar2")), ("2", _("InfoBar3")), ("3", _("InfoBar4")), ("4", _("InfoBar5")), ("5", _("InfoBar6"))], default = "0")
config.plugins.ArcticSetup.ChannelListStyle = ConfigSelection(choices = [("0", _("Channellist 1")), ("1", _("Channellist 2")), ("2", _("Channellist 3"))], default = "0")
config.plugins.ArcticSetup.MovieListStyle = ConfigSelection(choices = [("0", _("Movielist 1")), ("1", _("Movielist 2"))], default = "0")
config.plugins.ArcticSetup.EnableFadeIn = ConfigYesNo(default = False)
config.plugins.ArcticSetup.Blockmode = ConfigYesNo(default = False)

def main(session, **kwargs):
        session.open(ArcticSetupScreen)

def Plugins(**kwargs):
    list = []
    list.append(PluginDescriptor(name="Arctic Skin-Setup", description=_("Arctic Skin-Setup"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon = "movies.png", fnc=main))
    return list
