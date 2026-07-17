# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

VERSION = "1.0.0"


def get_addon():
    return xbmcaddon.Addon()


def log(message, level=xbmc.LOGINFO):
    xbmc.log("[Collection View Manager v%s] %s" % (VERSION, message), level)


def get_str(string_id):
    return get_addon().getLocalizedString(string_id)
