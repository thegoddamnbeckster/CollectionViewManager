# -*- coding: utf-8 -*-
"""
Discovers the current skin's available view modes for the video-library
window, so the user can pick one by name instead of needing to know Kodi's
internal view IDs.

The <views> declaration is a core Kodi skin-engine feature (interpreted by
Kodi itself to know which views a window supports), not a skin-specific
convention, so this works for any skin that declares one on its video
navigation window — but the window's *filename* (MyVideoNav.xml) and the
per-view file naming (View_<id>_<Name>.xml) are Estuary's own convention.
Skins that don't follow it will just get an empty result, handled by the
caller as "couldn't detect available views".
"""
import glob
import os
import xml.etree.ElementTree as ET

import xbmc
import xbmcaddon
import xbmcvfs

from resources.lib.utils import log

NAV_WINDOW_XML = "MyVideoNav.xml"


def get_available_views():
    """
    Returns a list of (view_id, view_name) tuples for the active skin's
    video-library window, or [] if they couldn't be determined.
    """
    skin_id = xbmc.getSkinDir()
    try:
        skin_path = xbmcvfs.translatePath(xbmcaddon.Addon(skin_id).getAddonInfo("path"))
    except Exception as e:
        log("get_available_views: could not resolve skin path for %s: %s" % (skin_id, e), xbmc.LOGERROR)
        return []

    nav_xml = os.path.join(skin_path, "xml", NAV_WINDOW_XML)
    if not xbmcvfs.exists(nav_xml):
        log("get_available_views: %s not found under %s" % (NAV_WINDOW_XML, skin_path), xbmc.LOGWARNING)
        return []

    try:
        tree = ET.parse(nav_xml)
        views_el = tree.getroot().find("views")
    except Exception as e:
        log("get_available_views: failed to parse %s: %s" % (nav_xml, e), xbmc.LOGERROR)
        return []

    if views_el is None or not views_el.text:
        log("get_available_views: no <views> element in %s" % nav_xml, xbmc.LOGWARNING)
        return []

    view_ids = [int(v.strip()) for v in views_el.text.split(",") if v.strip().isdigit()]
    if not view_ids:
        return []

    xml_dir = os.path.join(skin_path, "xml")
    results = []
    for vid in view_ids:
        matches = glob.glob(os.path.join(xml_dir, "View_%d_*.xml" % vid))
        if matches:
            base = os.path.splitext(os.path.basename(matches[0]))[0]  # "View_54_InfoWall"
            parts = base.split("_", 2)
            name = parts[2] if len(parts) == 3 else ("View %d" % vid)
        else:
            name = "View %d" % vid
        results.append((vid, name))

    return results
