from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Poll import Poll
from enigma import eDVBVolumecontrol


class ArcticVolume(Poll, Converter):

    def __init__(self, val):
        Converter.__init__(self, val)
        Poll.__init__(self)
        self.poll_interval = 500
        self.poll_enabled = True
        self.volctrl = eDVBVolumecontrol.getInstance()
        #print "ArcticVolume start Converter"	
        

    def doSuspend(self, suspended):
        if suspended:
            self.poll_enabled = False
        else:
            self.downstream_elements.changed((self.CHANGED_POLL,))
            self.poll_enabled = True

    @cached
    def getText(self):
        #print "ArcticVolume: " + str(self.volctrl.getVolume())
        return str(self.volctrl.getVolume())


    @cached
    def getValue(self):
        #print "ArcticVolume: " + str(self.volctrl.getVolume())
        return str(self.volctrl.getVolume())




    text = property(getText)
    value = property(getValue)




