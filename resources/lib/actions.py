# -*- coding: utf-8 -*-
"""
Shared capture/apply orchestration used by both the context menu (context.py)
and the settings "Apply" action (default.py), so the two entry points can't
drift out of sync with each other.
"""
import xbmc
import xbmcgui

from resources.lib.utils import log, get_str, get_setting, set_setting
from resources.lib.viewdb import read_view_state, apply_view_to_all_collections, get_current_skin


def capture_from_current_listitem():
    """
    Capture the view state for the collection ListItem the context menu was
    triggered on and save it as this addon's captured default.

    Returns the collection's title on success (a confirmation notification
    is NOT shown here — the caller decides what to do next, e.g. offer to
    apply immediately), or None on failure (a notification IS shown, since
    there's nothing further for the caller to do).
    """
    set_id = xbmc.getInfoLabel("ListItem.DBID")
    set_title = xbmc.getInfoLabel("ListItem.Title") or xbmc.getInfoLabel("ListItem.Label")
    skin = get_current_skin()

    if not set_id:
        log("No ListItem.DBID available — cannot identify the collection", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(get_str(32000), get_str(32015), xbmcgui.NOTIFICATION_ERROR, 5000)
        return None

    path = "videodb://movies/sets/%s/?setid=%s" % (set_id, set_id)
    state = read_view_state(path, skin)

    if state is None:
        xbmcgui.Dialog().notification(get_str(32000), get_str(32015), xbmcgui.NOTIFICATION_ERROR, 5000)
        return None

    set_setting("captured_view_mode", state["view_mode"])
    set_setting("captured_sort_method", state["sort_method"])
    set_setting("captured_sort_order", state["sort_order"])
    set_setting("captured_sort_attributes", state["sort_attributes"])
    set_setting("captured_skin", state["skin"])
    set_setting("captured_view_name", set_title)
    set_setting("captured_source_path", path)

    log("Captured view from '%s' (setid=%s, mode=%s)" % (set_title, set_id, state["view_mode"]))
    return set_title


def apply_captured_to_all():
    """
    Apply the currently-captured view state to every movie collection.
    Always shows a notification with the outcome.
    """
    view_mode = get_setting("captured_view_mode")
    if not view_mode:
        xbmcgui.Dialog().notification(get_str(32000), get_str(32014), xbmcgui.NOTIFICATION_WARNING, 5000)
        return

    captured_skin = get_setting("captured_skin")
    if captured_skin and captured_skin != get_current_skin():
        xbmcgui.Dialog().notification(get_str(32000), get_str(32017), xbmcgui.NOTIFICATION_WARNING, 6000)
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
        xbmcgui.Dialog().notification(get_str(32000), get_str(32016), xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    if total == 0:
        xbmcgui.Dialog().notification(get_str(32000), get_str(32018), xbmcgui.NOTIFICATION_INFO, 4000)
        return

    log("Applied '%s' to %d/%d collections" % (view_name, applied, total))
    xbmcgui.Dialog().notification(
        get_str(32000), get_str(32013).format(view_name, applied, total), xbmcgui.NOTIFICATION_INFO, 5000
    )
