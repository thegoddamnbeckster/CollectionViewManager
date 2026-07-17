# -*- coding: utf-8 -*-
"""
Reads and writes Kodi's own view-state database (ViewModesN.db) to copy a
captured collection view across every movie collection in the library.

Kodi persists per-path view state (viewMode/sortMethod/sortOrder/
sortAttributes, keyed by window id + path + active skin) automatically
whenever a user changes the view via a skin's own Options > View. There is
no public API to set this remotely or to decode what a given viewMode value
means — so rather than parsing skin XML to enumerate view names (which
differs per skin and would only work for skins we specifically handle), this
module treats a captured row as an opaque value and copies it verbatim to
every other movie-collection path. That makes it work identically regardless
of which skin is active.
"""
import glob
import json
import os
import sqlite3

import xbmc
import xbmcvfs

from resources.lib.utils import log

WINDOW_VIDEO_NAV = 10025


def _find_view_db_path():
    """
    Locate Kodi's ViewModesN.db. The N version suffix changes across Kodi
    releases, so the filename is discovered rather than hardcoded.
    """
    db_dir = xbmcvfs.translatePath("special://database/")
    candidates = sorted(glob.glob(os.path.join(db_dir, "ViewModes*.db")))
    if not candidates:
        return None

    def version_key(path):
        digits = "".join(ch for ch in os.path.basename(path) if ch.isdigit())
        return int(digits) if digits else 0

    # If more than one is somehow present, the highest-versioned one is the
    # one the running Kodi instance actually uses.
    return max(candidates, key=version_key)


def _connect(db_path, timeout=5):
    con = sqlite3.connect(db_path, timeout=timeout)
    con.execute("PRAGMA busy_timeout = 5000")
    return con


def get_current_skin():
    return xbmc.getSkinDir()


def capture_current_view():
    """
    Read back Kodi's own record of the view currently active for the
    container the user is standing in (expected to be inside a movie
    collection when this is called from the context menu item).

    Returns a dict of captured values, or None if Kodi never wrote a row for
    this exact path — which means the user hasn't explicitly changed the
    view here yet (Kodi only persists a row on an explicit view change, not
    for a skin's built-in default).
    """
    folder_path = xbmc.getInfoLabel("Container.FolderPath")
    view_name = xbmc.getInfoLabel("Container.Viewmode")
    skin = get_current_skin()

    db_path = _find_view_db_path()
    if not db_path:
        log("capture_current_view: no ViewModes*.db found", xbmc.LOGERROR)
        return None

    con = _connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT viewMode, sortMethod, sortOrder, sortAttributes "
            "FROM view WHERE window=? AND path=? AND skin=?",
            (WINDOW_VIDEO_NAV, folder_path, skin)
        )
        row = cur.fetchone()
    finally:
        con.close()

    if row is None:
        log("capture_current_view: no saved view state for path=%s, skin=%s "
            "(open Options > View here and pick a view first)" % (folder_path, skin),
            xbmc.LOGWARNING)
        return None

    return {
        "view_mode": row[0],
        "sort_method": row[1],
        "sort_order": row[2],
        "sort_attributes": row[3],
        "skin": skin,
        "view_name": view_name or "",
        "source_path": folder_path,
    }


def get_all_movie_set_paths():
    """Every movie collection's videodb:// path, via VideoLibrary.GetMovieSets."""
    request = json.dumps({
        "jsonrpc": "2.0", "id": 1,
        "method": "VideoLibrary.GetMovieSets",
        "params": {"properties": ["title"]}
    })
    response = json.loads(xbmc.executeJSONRPC(request))
    sets = response.get("result", {}).get("sets", [])
    paths = []
    for s in sets:
        set_id = s.get("setid")
        if set_id is not None:
            paths.append("videodb://movies/sets/%s/?setid=%s" % (set_id, set_id))
    return paths


def apply_view_to_all_collections(captured):
    """
    Write the captured view state to every movie collection's row in
    ViewModesN.db — updating collections that already have a row (e.g. ones
    visited before) and inserting one for collections that don't yet (never
    opened, so Kodi hasn't written anything for them).

    Returns (applied_count, total_count).
    """
    db_path = _find_view_db_path()
    if not db_path:
        raise RuntimeError("No ViewModes*.db found")

    paths = get_all_movie_set_paths()
    if not paths:
        return 0, 0

    con = _connect(db_path)
    applied = 0
    try:
        cur = con.cursor()
        for path in paths:
            cur.execute(
                "SELECT idView FROM view WHERE window=? AND path=? AND skin=?",
                (WINDOW_VIDEO_NAV, path, captured["skin"])
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    "UPDATE view SET viewMode=?, sortMethod=?, sortOrder=?, sortAttributes=? "
                    "WHERE idView=?",
                    (captured["view_mode"], captured["sort_method"],
                     captured["sort_order"], captured["sort_attributes"], existing[0])
                )
            else:
                cur.execute(
                    "INSERT INTO view (window, path, viewMode, sortMethod, sortOrder, sortAttributes, skin) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (WINDOW_VIDEO_NAV, path, captured["view_mode"], captured["sort_method"],
                     captured["sort_order"], captured["sort_attributes"], captured["skin"])
                )
            applied += 1
        con.commit()
    finally:
        con.close()

    return applied, len(paths)
