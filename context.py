# -*- coding: utf-8 -*-
"""
Context menu entry point. Appears only when browsing inside a movie
collection (see addon.xml's <visible> condition). Reads back whatever view
Kodi has already saved for the collection you're standing in and stores it
as this addon's "captured" default, ready to be applied to every other
collection from the settings screen.
"""
import xbmcgui

from resources.lib.utils import log, get_str, set_setting
from resources.lib.viewdb import capture_current_view

if __name__ == '__main__':
    log("Capture triggered from context menu")
    captured = capture_current_view()

    if captured is None:
        xbmcgui.Dialog().notification(
            get_str(32000), get_str(32015), xbmcgui.NOTIFICATION_ERROR, 5000
        )
    else:
        set_setting("captured_view_mode", captured["view_mode"])
        set_setting("captured_sort_method", captured["sort_method"])
        set_setting("captured_sort_order", captured["sort_order"])
        set_setting("captured_sort_attributes", captured["sort_attributes"])
        set_setting("captured_skin", captured["skin"])
        set_setting("captured_view_name", captured["view_name"])
        set_setting("captured_source_path", captured["source_path"])

        log("Captured view '%s' (mode=%s) from %s" % (
            captured["view_name"], captured["view_mode"], captured["source_path"]))

        xbmcgui.Dialog().notification(
            get_str(32000),
            get_str(32011).format(captured["view_name"] or "current"),
            xbmcgui.NOTIFICATION_INFO, 4000
        )
