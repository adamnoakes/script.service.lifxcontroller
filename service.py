import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))
import xbmc
from time import time, sleep
import xbmcaddon
from lifxlan import *
import xml.etree.ElementTree as ET

_addon        = xbmcaddon.Addon()
_addon_path   = _addon.getAddonInfo('path')
_addonversion = _addon.getAddonInfo('version')
_addonid      = _addon.getAddonInfo('id')
_addonname    = _addon.getAddonInfo('name')
lifx = LifxLAN(None)
groups = {}

def log(txt):
    message = '%s: %s' % (_addonname, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

def identify_light_groups():
    devices = lifx.get_lights()
    if len(devices) != 0:
        for device in devices:
            if device.get_group_label() not in groups:
                groups[device.get_group_label()] = []
            groups[device.get_group_label()].append(device)

        settings_file = os.path.join(_addon_path, 'resources', 'settings.xml')
        sleep(0.5)
        tree = ET.ElementTree(file=settings_file)
        #Search for the entry in the settings file
        for elem in tree.findall(".//setting"):
            if elem.attrib.get('id') == "group":
                elem.set('values', '|'.join(groups.iterkeys()))
        tree.write(settings_file)

def dim_lights():
    if (_addon.getSetting('group') == '' or 
        _addon.getSetting('dim_duration') == ''):
        return
    for light in groups[_addon.getSetting('group')]:
        if light.power_level == None:
            light.get_power() #caches value to light.power_level
        light.set_power(0, _addon.getSetting('dim_duration'))

def restore_lights():
    if (_addon.getSetting('group') == '' or 
        _addon.getSetting('restore_duration') == ''):
        return
    log('restoring lights' )
    for light in groups[_addon.getSetting('group')]:
        if light.power_level != None:
            power_level = light.power_level
            light.set_power(power_level, _addon.getSetting('restore_duration'))

def _daemon():
    while (not xbmc.abortRequested):
      # Do nothing
      xbmc.sleep(100)

class LIFXPlayer(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )

    def onPlayBackStarted(self):
        dim_lights()

    def onPlayBackResumed(self):
        dim_lights()

    def onPlayBackEnded(self):
        restore_lights()

    def onPlayBackPaused(self):
        log('playback paused')
        restore_lights()

    def onPlayBackStopped(self):
        restore_lights()
        
if __name__ == '__main__':
    log('starting')
    identify_light_groups()
    player = LIFXPlayer()
    _daemon()
    restore_lights()
    del LIFXPlayer
    log('exiting')

