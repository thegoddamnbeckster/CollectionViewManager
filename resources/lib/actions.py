# -*- coding: utf-8 -*-
"""
Core orchestration for the "pick a view, apply it everywhere" flow.

Kodi's own internal view-mode encoding (what actually gets written to
ViewModesN.db) isn't the raw skin view ID and isn't safe to fabricate — so
rather than guess it, this briefly navigates to one real collection and
fires Kodi's own Container.SetViewMode(id) builtin (the same thing Options >
View triggers internally), lets Kodi compute and write the correct value
itself, then copies that resulting row to every other movie collection.
"""
import xbmc
import xbmcgui

from resources.lib.utils import log, get_str
from resources.lib.viewdb import read_view_state, apply_view_to_all_collections, get_current_skin

NAV_WAIT_SETTLE_SEC = 0.3
READBACK_RETRIES = 3


def set_view_for_all_collections(view_id, seed_set_id):
    """
    Set `view_id` (a raw skin view ID, e.g. 54 for Estuary's InfoWall) on
    the collection identified by `seed_set_id`, then copy the resulting
    saved view state to every movie collection in the library.

    Returns (applied_count, total_count) on success. Raises RuntimeError
    with a user-facing message on failure.
    """
    skin = get_current_skin()
    seed_path = "videodb://movies/sets/%s/?setid=%s" % (seed_set_id, seed_set_id)

    xbmc.executebuiltin("ActivateWindow(Videos,%s,return)" % seed_path, True)
    xbmc.executebuiltin("Container.SetViewMode(%d)" % view_id, True)

    state = None
    for attempt in range(READBACK_RETRIES):
        xbmc.sleep(int(NAV_WAIT_SETTLE_SEC * 1000))
        state = read_view_state(seed_path, skin)
        if state is not None:
            break
        log("set_view_for_all_collections: readback attempt %d found nothing yet" % (attempt + 1))

    # Always try to return the user to where they were, even on failure.
    xbmc.executebuiltin("Action(Back)")

    if state is None:
        raise RuntimeError("Kodi never saved a view state for the seed collection after SetViewMode")

    applied, total = apply_view_to_all_collections(state)
    return applied, total


def run_set_view_flow(view_id, view_name, seed_set_id, seed_title):
    """
    Full user-facing flow for one context-menu invocation: set the view,
    apply it everywhere, and show the result as a notification. Never
    raises — all failures are reported via notification instead.
    """
    try:
        applied, total = set_view_for_all_collections(view_id, seed_set_id)
    except Exception as e:
        log("run_set_view_flow failed: %s" % str(e), xbmc.LOGERROR)
        xbmcgui.Dialog().notification(get_str(32000), get_str(32016), xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    if total == 0:
        xbmcgui.Dialog().notification(get_str(32000), get_str(32018), xbmcgui.NOTIFICATION_INFO, 4000)
        return

    log("Applied '%s' (id=%d) to %d/%d collections, seeded from '%s'" % (
        view_name, view_id, applied, total, seed_title))
    xbmcgui.Dialog().notification(
        get_str(32000), get_str(32013).format(view_name, applied, total), xbmcgui.NOTIFICATION_INFO, 5000
    )
