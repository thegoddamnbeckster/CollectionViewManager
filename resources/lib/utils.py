# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

VERSION = "1.0.0"


def get_addon():
    return xbmcaddon.Addon()


def log(message, level=xbmc.LOGINFO):
    xbmc.log("[Collection View Manager v%s] %s" % (VERSION, message), level)


def get_setting(setting_id):
    return get_addon().getSetting(setting_id)


def set_setting(setting_id, value):
    get_addon().setSetting(setting_id, str(value))


def get_str(string_id):
    return get_addon().getLocalizedString(string_id)
