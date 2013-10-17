# -*- coding: utf-8 -*-
import sys, os, glob, shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/bin')
import mapproxy_execute


translator = QTranslator()
translator.load(
    os.path.dirname(os.path.abspath(__file__)) + "/i18n/mapproxyplugin_" + QLocale.system().name()[0:2] + ".qm")
QApplication.installTranslator(translator)


class MPLayerType:
    def __init__(self, plugin, base, name, title, icon, crs):
        self.__plugin = plugin
        self.base = base
        self.name = name
        self.title = title
        self.icon = icon
        self.crs = crs
        self.id = None

    def addLayer(self):
        self.__plugin.addLayer(self)


class MPLayerTypeRegistry:
    def __init__(self):
        self.__mpLayerTypes = {}
        self.__layerTypeId = 0

    def add(self, layerType):
        layerType.id = self.__layerTypeId
        self.__mpLayerTypes[self.__layerTypeId] = layerType
        self.__layerTypeId += 1

    def types(self):
        return self.__mpLayerTypes.values()

    def getById(self, id):
        return self.__mpLayerTypes[id]


class MapProxyPlugin:
    def __init__(self, iface):
        self.iface = iface


    def initGui(self):
        pathPlugin = "%s%s%%s" % ( os.path.dirname(__file__), os.path.sep )
        self.readmeAddAction = QAction(QIcon(pathPlugin % "readme.png"), "ReadMe", self.iface.mainWindow())
        QObject.connect(self.readmeAddAction, SIGNAL("triggered()"), self.readme)
        self.iface.addPluginToMenu("MapProxy plugin", self.readmeAddAction)
        self.installAddAction = QAction(QIcon(pathPlugin % "mapproxy.png"), "Install MapProxy", self.iface.mainWindow())
        QObject.connect(self.installAddAction, SIGNAL("triggered()"), self.install)
        self.iface.addPluginToMenu("MapProxy plugin", self.installAddAction)
        self.runAddAction = QAction(QIcon(pathPlugin % "mapproxy_run.png"), "Run MapProxy", self.iface.mainWindow())
        QObject.connect(self.runAddAction, SIGNAL("triggered()"), self.run)
        self.iface.addPluginToMenu("MapProxy plugin", self.runAddAction)
        self.cacheAddAction = QAction(QIcon(pathPlugin % "cache.png"), "Remove Cache", self.iface.mainWindow())
        QObject.connect(self.cacheAddAction, SIGNAL("triggered()"), self.cache)
        self.iface.addPluginToMenu("MapProxy plugin", self.cacheAddAction)

    def unload(self):
        # Remove the plugin menu item and icon
        if hasattr(self, 'layerAddActions'):
            for action in self.layerAddActions:
                self.iface.removePluginMenu("MapProxy plugin", action)

        self.iface.removePluginMenu("MapProxy plugin", self.installAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.runAddAction)

        mapproxy_execute.kill()

    def addLayer(self, layerType):
        #if possible, set mapproxy service epsg to qgis project epsg
        qgisepsg = str(self.iface.mapCanvas().mapRenderer().destinationCrs().authid())
        epsg = layerType.crs[0]
        for crs in layerType.crs:
            if qgisepsg == crs:
                epsg = crs

        self.iface.addRasterLayer(
            "crs=" + epsg + "&layers=" + layerType.name + "&styles=&format=image/png&url=http://localhost:8080/" + layerType.base + "/service?",
            layerType.name, "wms")
        #if WMTS
        #self.iface.addRasterLayer("url=http://localhost:8080/" + layerType.base + "/service?service=wmts&version=1.0.0&tileMatrixSet=web&crs=EPSG:3857&layers=" + layerType.name + "&styles=&format=image/png",layerType.name,"wms")

    def run(self):
        pathPlugin = "%s%s%%s" % ( os.path.dirname(__file__), os.path.sep )
        if not os.path.isdir(pathPlugin % "bin" + os.sep + "mypython"):
            QMessageBox.information(None, "Information:",
                                    QCoreApplication.translate("message", "You need to install mapproxy first"))
            return

        projectdir = pathPlugin % "project"
        myos = mapproxy_execute.run("\"" + projectdir + "\"")
        if myos == "Windows":
            rep = QMessageBox.question(None, "Info:", QCoreApplication.translate("message",
                                                                                 "Are you sure you want to run mapproxy? It will run on Command Prompt.Please close it by hand when you'll stop.You can confirm the state on http://localhost:8080"),
                                       QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
        else:
            rep = QMessageBox.question(None, "Info:", QCoreApplication.translate("message",
                                                                                 "Are you sure you want to run mapproxy? You can confirm the state on http://localhost:8080"),
                                       QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)

        if rep == QMessageBox.Cancel:
            return

        #Layers
        files = glob.glob(projectdir + os.sep + "*.yaml")
        self.mpLayerTypeRegistry = MPLayerTypeRegistry()
        self.layerAddActions = []

        for filename in files:
            filebase = os.path.splitext(os.path.basename("\"" + filename + "\""))[0]
            yd = mapproxy_execute.layers("\"" + filename + "\"")

            for layer in yd['layers']:
                self.mpLayerTypeRegistry.add(
                    MPLayerType(self, filebase, layer['name'], layer['title'], filebase + '.png',
                                yd['services']['wms']['srs']))
        for layerType in self.mpLayerTypeRegistry.types():
            action = QAction(QIcon(pathPlugin % layerType.icon), layerType.title, self.iface.mainWindow())
            self.layerAddActions.append(action)
            QObject.connect(action, SIGNAL("triggered()"), layerType.addLayer)
            self.iface.addPluginToMenu("MapProxy plugin", action)

    def install(self):
        rep = QMessageBox.question(None, "",
                                   QCoreApplication.translate("message", "Are you sure you want to install mapproxy?"
                                                                         "So it will take a time to install, please wait for the message to appear."),
                                   QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
        if rep == QMessageBox.Yes:
            p = mapproxy_execute.install()
            if p == 0:
                QMessageBox.information(None, "Info:",
                                        QCoreApplication.translate("message", "mapproxy install finished"))
            else:
                QMessageBox.information(None, "Error:",
                                        QCoreApplication.translate("message", "mapproxy install fail !"))

    def cache(self):
        rep = QMessageBox.question(None, "",
                                   QCoreApplication.translate("message", "Are you sure you want to remove cache?"),
                                   QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Yes)
        if rep == QMessageBox.Yes:
            pathPlugin = "%s%s%%s" % ( os.path.dirname(__file__), os.path.sep )
            shutil.rmtree(pathPlugin % "project" + os.sep + "cache_data", True)

    def readme(self):
        pathPlugin = "%s%s%%s" % ( os.path.dirname(__file__), os.path.sep )
        projectdir = pathPlugin % "project"
        QMessageBox.information(None, "ReadMe", QCoreApplication.translate("message", "<h1>MapProxy Plugin</h1>"
                                                                                      "<ol>"
                                                                                      "<li>Install mapproxy</li>"
                                                                                      "<li>Run mapproxy. If success, layers are added in the menu</li>"
                                                                                      "<li>Select layer</li>"
                                                                                      "</ol>"
                                                                                      "<p>you can set layers by configuring yaml mapproxy file in this dirctory.<br>" + projectdir + "</p>"))
