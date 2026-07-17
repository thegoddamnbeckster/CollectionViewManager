# -*- coding: utf-8 -*-
"""
Script entry point (declared as xbmc.python.script in addon.xml). Opens the
addon's settings — the actual "set the view" action is entirely driven by
the context menu (context.py) now, there's nothing else to run here.
"""
from resources.lib.utils import log, get_addon

if __name__ == '__main__':
    log("default.py invoked")
    get_addon().openSettings()
