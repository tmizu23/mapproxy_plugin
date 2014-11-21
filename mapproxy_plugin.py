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

## about credit drawing
## reference:
## https://github.com/sourcepole/qgis-watermark-plugin
## https://github.com/minorua/TileLayerPlugin

class MPCreditType(QgsPluginLayerType):

  def __init__(self):
    QgsPluginLayerType.__init__(self, MPCredit.LAYER_TYPE)

  def createLayer(self):
    return MPCredit()

  def showLayerProperties(self, layer):
    layer.updateText()

    # indicate that we have shown the properties dialog
    return True

class MPCredit(QgsPluginLayer):

  LAYER_TYPE="credit"

  def __init__(self,credit):
    QgsPluginLayer.__init__(self, MPCredit.LAYER_TYPE, "credit")
    self.setValid(True)
    self.credit=credit
    #self.credit = "Image produced and distributed by AIST, Source of Landsat 8 data: U.S. Geological Survey."

  def draw(self, rendererContext):

      painter = rendererContext.painter()
      extent = rendererContext.extent()
      mapToPixel = rendererContext.mapToPixel()
      rasterScaleFactor = rendererContext.rasterScaleFactor()
      invRasterScaleFactor = 1.0/rasterScaleFactor

      topleft = mapToPixel.transform(extent.xMinimum(), extent.yMaximum())
      bottomright = mapToPixel.transform(extent.xMaximum(), extent.yMinimum())
      width = (bottomright.x() - topleft.x()) * rasterScaleFactor
      height = (bottomright.y() - topleft.y()) * rasterScaleFactor

      # setup painter
      painter.save()
      painter.scale(invRasterScaleFactor, invRasterScaleFactor)
    
      rect = QRect(0, 0, width, height)
      textRect = painter.boundingRect(rect, Qt.AlignBottom | Qt.AlignRight, self.credit)
      bgRect = QRect(textRect.left() - 3, textRect.top() - 2, textRect.width() + 3, textRect.height()+2)
      painter.fillRect(bgRect, QColor(240, 240, 240, 150))
      painter.drawText(rect, Qt.AlignBottom | Qt.AlignRight, self.credit)
      painter.restore()
    
      return True

  def updateText(self):
      text, ok = QInputDialog.getText(None, 'Input Dialog', 'Enter credit:',0,self.credit)
      if ok:
        self.credit = text
        self.emit(SIGNAL("repaintRequested()"))

class MPLayerType:
    def __init__(self, plugin, base, name, title, icon, crs, abstract,access_constraints):
        self.__plugin = plugin
        self.base = base
        self.name = name
        self.title = title
        self.icon = icon
        self.crs = crs
        self.id = None
        self.credit = abstract
        self.access_constraints = access_constraints.replace('\n','<br>')#.replace(' ','<br>')

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
        
        QgsPluginLayerRegistry.instance().addPluginLayerType(MPCreditType())

    def unload(self):
        # Remove the plugin menu item and icon
        if hasattr(self, 'layerAddActions'):
            for action in self.layerAddActions:
                self.iface.removePluginMenu("MapProxy plugin", action)

        self.iface.removePluginMenu("MapProxy plugin", self.installAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.runAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.readmeAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.cacheAddAction)
        
        QgsPluginLayerRegistry.instance().removePluginLayerType(MPCredit.LAYER_TYPE)
        mapproxy_execute.kill()

    def stopMapproxy(self):
        if hasattr(self, 'layerAddActions'):
            for action in self.layerAddActions:
                self.iface.removePluginMenu("MapProxy plugin", action)
        mapproxy_execute.kill()

    def addLayer(self, layerType):
        QMessageBox.information(None, "Information:",layerType.access_constraints)

        #if possible, set mapproxy service epsg to qgis project epsg
        qgisepsg = str(self.iface.mapCanvas().mapSettings().destinationCrs().authid())
        epsg = layerType.crs[0]
        for crs in layerType.crs:
            if qgisepsg == crs:
                epsg = crs

        self.iface.addRasterLayer(
            "crs=" + epsg + "&layers=" + layerType.name + "&styles=&format=image/png&url=http://localhost:8080/" + layerType.base + "/service?",
            layerType.name, "wms")

        credit = MPCredit(layerType.credit)
        QgsMapLayerRegistry.instance().addMapLayer(credit)
        #if WMTS
        #self.iface.addRasterLayer("url=http://localhost:8080/" + layerType.base + "/service?service=wmts&version=1.0.0&tileMatrixSet=web&crs=EPSG:3857&layers=" + layerType.name + "&styles=&format=image/png",layerType.name,"wms")

    def run(self):
        self.stopMapproxy()
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
                                yd['services']['wms']['srs'],yd['services']['wms']['md']['abstract'],yd['services']['wms']['md']['access_constraints']))
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
