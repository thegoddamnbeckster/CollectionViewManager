# -*- coding: utf-8 -*-
"""
Context menu entry point. Appears on the collection *tile* itself (any
ListItem with DBTYPE "set") — including from the Movies root list, without
needing to browse into the collection. Reads back whatever view Kodi has
already saved for that specific collection and stores it as this addon's
"captured" default, ready to be applied to every other collection from the
settings screen.

Note: this requires the collection to already have a saved view (i.e. you've
entered it at least once and picked a view via Kodi's own Options > View) —
that one-time step still has to happen inside the collection, the normal
Kodi way, but this addon's own menu never needs to.
"""
import xbmc
import xbmcgui

from resources.lib.utils import log, get_str, set_setting
from resources.lib.viewdb import read_view_state, get_current_skin

if __name__ == '__main__':
    log("Capture triggered from context menu")

    set_id = xbmc.getInfoLabel("ListItem.DBID")
    set_title = xbmc.getInfoLabel("ListItem.Title") or xbmc.getInfoLabel("ListItem.Label")
    skin = get_current_skin()

    if not set_id:
        log("No ListItem.DBID available — cannot identify the collection", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            get_str(32000), get_str(32015), xbmcgui.NOTIFICATION_ERROR, 5000
        )
    else:
        path = "videodb://movies/sets/%s/?setid=%s" % (set_id, set_id)
        state = read_view_state(path, skin)

        if state is None:
            xbmcgui.Dialog().notification(
                get_str(32000), get_str(32015), xbmcgui.NOTIFICATION_ERROR, 5000
            )
        else:
            set_setting("captured_view_mode", state["view_mode"])
            set_setting("captured_sort_method", state["sort_method"])
            set_setting("captured_sort_order", state["sort_order"])
            set_setting("captured_sort_attributes", state["sort_attributes"])
            set_setting("captured_skin", state["skin"])
            set_setting("captured_view_name", set_title)
            set_setting("captured_source_path", path)

            log("Captured view from '%s' (setid=%s, mode=%s)" % (set_title, set_id, state["view_mode"]))

            xbmcgui.Dialog().notification(
                get_str(32000),
                get_str(32011).format(set_title or "collection"),
                xbmcgui.NOTIFICATION_INFO, 4000
            )
