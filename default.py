# -*- coding: utf-8 -*-
"""
Script entry point (declared as xbmc.python.script in addon.xml). With no
action, opens the addon's settings. With action=apply (fired by the
"Apply to all movie collections now" settings button, or reachable directly
via RunScript for a keymap/other trigger), applies the currently-captured
view state to every movie collection in the library.
"""
import sys

from resources.lib.utils import log, get_addon
from resources.lib.actions import apply_captured_to_all


def _get_action():
    for arg in sys.argv[1:]:
        if arg.startswith("action="):
            return arg.split("=", 1)[1]
    return "settings"


if __name__ == '__main__':
    action = _get_action()
    log("default.py invoked, action=%s" % action)

    if action == "apply":
        apply_captured_to_all()
    else:
        get_addon().openSettings()
