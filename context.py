# -*- coding: utf-8 -*-
"""
Context menu entry point. Appears on the collection *tile* itself (any
ListItem with DBTYPE "set") — including from the Movies root list, without
needing to browse into the collection first.

One step: pick a view from a list of what the current skin actually offers,
and it's applied to every movie collection in the library immediately. No
manual "go set it via Options > View first" prerequisite.
"""
import xbmc
import xbmcgui

from resources.lib.utils import log, get_str
from resources.lib.skinviews import get_available_views
from resources.lib.actions import run_set_view_flow

if __name__ == '__main__':
    log("Context menu triggered")

    set_id = xbmc.getInfoLabel("ListItem.DBID")
    set_title = xbmc.getInfoLabel("ListItem.Title") or xbmc.getInfoLabel("ListItem.Label")

    if not set_id:
        log("No ListItem.DBID available — cannot identify the collection", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(get_str(32000), get_str(32015), xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        views = get_available_views()
        if not views:
            log("No views detected for the current skin", xbmc.LOGERROR)
            xbmcgui.Dialog().notification(get_str(32000), get_str(32019), xbmcgui.NOTIFICATION_ERROR, 5000)
        else:
            names = [name for _, name in views]
            choice = xbmcgui.Dialog().select(get_str(32025), names)
            if choice != -1:
                view_id, view_name = views[choice]
                run_set_view_flow(view_id, view_name, set_id, set_title)
