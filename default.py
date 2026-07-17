# -*- coding: utf-8 -*-
"""
Script entry point (declared as xbmc.python.script in addon.xml). With no
action, opens the addon's settings. With action=apply (fired by the
"Apply to all movie collections now" settings button), writes the captured
view state to every movie collection in the library.
"""
import sys

import xbmc
import xbmcgui

from resources.lib.utils import log, get_str, get_setting, get_addon
from resources.lib.viewdb import apply_view_to_all_collections, get_current_skin


def _get_action():
    for arg in sys.argv[1:]:
        if arg.startswith("action="):
            return arg.split("=", 1)[1]
    return "settings"


def _do_apply():
    view_mode = get_setting("captured_view_mode")
    if not view_mode:
        xbmcgui.Dialog().notification(
            get_str(32000), get_str(32014), xbmcgui.NOTIFICATION_WARNING, 5000
        )
        return

    captured_skin = get_setting("captured_skin")
    if captured_skin and captured_skin != get_current_skin():
        xbmcgui.Dialog().notification(
            get_str(32000), get_str(32017), xbmcgui.NOTIFICATION_WARNING, 6000
        )
        return

    captured = {
        "view_mode": int(view_mode),
        "sort_method": int(get_setting("captured_sort_method") or 0),
        "sort_order": int(get_setting("captured_sort_order") or 1),
        "sort_attributes": int(get_setting("captured_sort_attributes") or 0),
        "skin": captured_skin,
    }
    view_name = get_setting("captured_view_name") or "current"

    try:
        applied, total = apply_view_to_all_collections(captured)
    except Exception as e:
        log("Apply failed: %s" % str(e), xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            get_str(32000), get_str(32016), xbmcgui.NOTIFICATION_ERROR, 5000
        )
        return

    if total == 0:
        xbmcgui.Dialog().notification(
            get_str(32000), get_str(32018), xbmcgui.NOTIFICATION_INFO, 4000
        )
        return

    log("Applied '%s' to %d/%d collections" % (view_name, applied, total))
    xbmcgui.Dialog().notification(
        get_str(32000),
        get_str(32013).format(view_name, applied, total),
        xbmcgui.NOTIFICATION_INFO, 5000
    )


if __name__ == '__main__':
    action = _get_action()
    log("default.py invoked, action=%s" % action)

    if action == "apply":
        _do_apply()
    else:
        get_addon().openSettings()
