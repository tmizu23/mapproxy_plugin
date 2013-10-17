# -*- coding: utf-8 -*-

def classFactory(iface):
  from mapproxy_plugin import MapProxyPlugin
  return MapProxyPlugin(iface)
