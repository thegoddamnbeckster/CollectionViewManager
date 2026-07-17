# -*- coding: utf-8 -*-
"""
Context menu entry point. Appears on the collection *tile* itself (any
ListItem with DBTYPE "set") — including from the Movies root list, without
needing to browse into the collection. Captures whatever view Kodi has
already saved for that specific collection, then immediately offers to
apply it to every other collection right here — no separate trip to
Settings required unless you'd rather defer that.

Note: this requires the collection to already have a saved view (i.e. you've
entered it at least once and picked a view via Kodi's own Options > View) —
that one-time step still has to happen inside the collection, the normal
Kodi way, but this addon's own menu never needs to.
"""
import xbmcgui

from resources.lib.utils import log, get_str
from resources.lib.actions import capture_from_current_listitem, apply_captured_to_all

if __name__ == '__main__':
    log("Capture triggered from context menu")

    captured_title = capture_from_current_listitem()

    if captured_title is not None:
        if xbmcgui.Dialog().yesno(get_str(32000), get_str(32024).format(captured_title)):
            apply_captured_to_all()
