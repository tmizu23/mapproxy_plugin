# -*- coding: utf-8 -*-
import sys, os, glob, shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.gui import QgsMessageBar
from qgis.core import *
from landsat8_dialog import landsat8Dialog
from time_goes_by import *
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/bin')
import mapproxy_execute
import landsat8_util


translator = QTranslator()
translator.load(
    os.path.dirname(os.path.abspath(__file__)) + "/i18n/mapproxyplugin_" + QLocale.system().name()[0:2] + ".qm")
QApplication.installTranslator(translator)


## about credit drawing
## reference:
## https://github.com/sourcepole/qgis-watermark-plugin
## https://github.com/minorua/TileLayerPlugin

class MPCreditType(QgsPluginLayerType):

  def __init__(self,plugin):
    QgsPluginLayerType.__init__(self, MPCredit.LAYER_TYPE)
    self.plugin = plugin

  def createLayer(self):
    return MPCredit(self.plugin,"","","")

  def showLayerProperties(self, layer):
    layer.updateText()

    # indicate that we have shown the properties dialog
    return True

class MPCredit(QgsPluginLayer):

  LAYER_TYPE="MPCredit"

  def __init__(self,plugin,qgisepsg,layername,credit):
     QgsPluginLayer.__init__(self, MPCredit.LAYER_TYPE, layername + "_credit")
     self.plugin=plugin
     self.credit=credit
     self.setCustomProperty("credit", credit)
     self.epsg = qgisepsg
     if self.epsg=="":
        self.epsg = self.plugin.iface.mapCanvas().mapSettings().destinationCrs().authid()
     self.setCrs(QgsCoordinateReferenceSystem(self.epsg))
     self.setValid(True)
     QObject.connect(self, SIGNAL("showBarMessage(QString, QString, int, int)"), self.showBarMessageSlot)
     #animation
     self.santa = False
     self.posX = 139.748806
     self.posY = 35.648167
     self._state = 0
     period_time = 500
     steps = 2
     duration = steps * period_time
     self.anim = QPropertyAnimation(self, "state")
     self.anim.setStartValue(0)
     self.anim.setEndValue(steps)
     self.anim.setDuration(duration)
     self.anim.setLoopCount(-1)
     self.anim.valueChanged.connect(self.value_changed)
     self.plugin.iface.mapCanvas().renderComplete.connect(self.after_render)
     self.plugin.iface.mapCanvas().renderStarting.connect(self.anim.pause)
     self.anim.start()
     
  def after_render(self):
     if self.santa:
        self.anim.resume()

  def value_changed(self,value):
     rnd1 = random.uniform(1, 10)/10000 - 0.0005
     rnd2 = random.uniform(1, 10)/10000 - 0.0005
     self.posX = self.posX + rnd1
     self.posY = self.posY + rnd2
     self.triggerRepaint()

  @pyqtProperty(int)
  def state(self):
        return self._state

  @state.setter
  def state(self, value):
        self._state = value

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
      
      ### joke
      p = QgsPoint(self.posX, self.posY)
      extent = QgsGeometry.fromWkt(self.plugin.iface.mapCanvas().extent().asWktPolygon()) 
      extent.transform(QgsCoordinateTransform(self.plugin.iface.mapCanvas().mapSettings().destinationCrs(),QgsCoordinateReferenceSystem(4326)))
      if self.plugin.iface.mapCanvas().scale() < 50000 and (extent.boundingBox().xMinimum() < p.x() < extent.boundingBox().xMaximum()) and (extent.boundingBox().yMinimum() < p.y() < extent.boundingBox().yMaximum()):
           self.santa = True
           self.px = -32 + painter.viewport().width() * (p.x()-extent.boundingBox().xMinimum())/(extent.boundingBox().xMaximum()-extent.boundingBox().xMinimum())
           self.py = -64 + painter.viewport().height() - painter.viewport().height() * (p.y()-extent.boundingBox().yMinimum())/(extent.boundingBox().yMaximum()-extent.boundingBox().yMinimum())         
           painter.drawImage(self.px, self.py, QImage(self.plugin.pathPlugin + os.sep + "santa.png"))
           #self.showBarMessage("Debug:", QgsMessageBar.INFO,1,str(self.posX))
      else:
           self.santa = False
      painter.restore()

      #if self.plugin.iface.mapCanvas().scale() > 10000000:
      #   self.showBarMessage("Please zoom in more", QgsMessageBar.INFO,2,"Mapproxy Plugin:")
      

      return True



  def updateText(self):
      text, ok = QInputDialog.getText(None, 'Input Dialog', 'Enter credit:',0,self.credit)
      if ok:
        self.credit = text
        self.emit(SIGNAL("repaintRequested()"))

  def readXml(self, node):
    self.readCustomProperties(node)
    self.credit = self.customProperty("credit", "")
    return True

  def writeXml(self, node, doc):
    element = node.toElement();
    element.setAttribute("type", "plugin")
    element.setAttribute("name", MPCredit.LAYER_TYPE)
    return True

  def showBarMessage(self, text, level=QgsMessageBar.INFO, duration=0, title=None):
    self.emit(SIGNAL("showBarMessage(QString, QString, int, int)"), title, text, level, duration)

  def showBarMessageSlot(self, title, text, level, duration):
    self.plugin.iface.messageBar().pushMessage(title, text, level, duration)
  

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
        self.layers ={}
        self.pathPlugin = os.path.dirname(__file__)
        QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerRemoved(QString)"), self.layerRemoved)

    def initGui(self):
        self.lsat8dlg = landsat8Dialog()
        self.readmeAddAction = QAction(QIcon(self.pathPlugin + os.sep + "readme.png"), "ReadMe", self.iface.mainWindow())
        QObject.connect(self.readmeAddAction, SIGNAL("triggered()"), self.readme)
        self.iface.addPluginToMenu("MapProxy plugin", self.readmeAddAction)
        self.installAddAction = QAction(QIcon(self.pathPlugin + os.sep + "mapproxy.png"), "Install MapProxy", self.iface.mainWindow())
        QObject.connect(self.installAddAction, SIGNAL("triggered()"), self.install)
        self.iface.addPluginToMenu("MapProxy plugin", self.installAddAction)
        self.runAddAction = QAction(QIcon(self.pathPlugin + os.sep + "mapproxy_run.png"), "Run MapProxy", self.iface.mainWindow())
        QObject.connect(self.runAddAction, SIGNAL("triggered()"), self.run)
        self.iface.addPluginToMenu("MapProxy plugin", self.runAddAction)
        self.cacheAddAction = QAction(QIcon(self.pathPlugin + os.sep + "cache.png"), "Remove Cache", self.iface.mainWindow())
        QObject.connect(self.cacheAddAction, SIGNAL("triggered()"), self.cache)
        self.iface.addPluginToMenu("MapProxy plugin", self.cacheAddAction)
        
        self.mpCreditType = MPCreditType(self)
        QgsPluginLayerRegistry.instance().addPluginLayerType(self.mpCreditType)
        #if mapproxy has installed, and autorun 
        if os.path.isdir(self.pathPlugin + os.sep + "bin" + os.sep + "mypython") and os.path.isfile(self.pathPlugin + os.sep + "bin" + os.sep + "autorun.ini"):
           self.run("auto")

    def unload(self):
        # Remove the plugin menu item and icon
        if hasattr(self, 'layerAddActions'):
            for action in self.layerAddActions:
                self.iface.removePluginMenu("MapProxy plugin", action)

        self.iface.removePluginMenu("MapProxy plugin", self.installAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.runAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.readmeAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.cacheAddAction)
        self.iface.removePluginMenu("MapProxy plugin", self.landsat8MapGeneratorAction)
        self.iface.removePluginMenu("MapProxy plugin", self.landsat8GetDataAction)
        QgsPluginLayerRegistry.instance().removePluginLayerType(MPCredit.LAYER_TYPE)
        QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerRemoved(QString)"), self.layerRemoved)

        mapproxy_execute.kill()

    def layerRemoved(self, layerId):
        if layerId in self.layers:
           del self.layers[layerId]

    def stopMapproxy(self):
        if hasattr(self, 'landsat8MapGeneratorAction'):
           self.iface.removePluginMenu("MapProxy plugin", self.landsat8MapGeneratorAction)
           self.iface.removePluginMenu("MapProxy plugin", self.landsat8GetDataAction)

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
        #if qgisepsg == "":
        #   self.iface.mapCanvas().mapSettings().setDestinationCrs(QgsCoordinateReferenceSystem(epsg))

        self.iface.addRasterLayer(
            "crs=" + epsg + "&layers=" + layerType.name + "&styles=&format=image/png&oppai=true&url=http://localhost:8080/" + layerType.base + "/service?",
            layerType.title, "wms")
        credit = MPCredit(self,qgisepsg,layerType.title,layerType.credit)
        QgsMapLayerRegistry.instance().addMapLayer(credit)
        self.layers[credit.id()]=credit

        #if WMTS
        #self.iface.addRasterLayer("url=http://localhost:8080/" + layerType.base + "/service?service=wmts&version=1.0.0&tileMatrixSet=web&crs=EPSG:3857&layers=" + layerType.name + "&styles=&format=image/png",layerType.name,"wms")

    def run(self,opt="manual"):
        #if mapproxy has not installed
        if not os.path.isdir(self.pathPlugin + os.sep + "bin" + os.sep + "mypython"):
           QMessageBox.information(None, "Information:",QCoreApplication.translate("message", "You need to install mapproxy first"))
           return
        if opt=="manual":
           rep = QMessageBox.question(None, "Info:", QCoreApplication.translate("message","Will you set autostart option? Mapproxy will run when you open the qgis. You can confirm the state on http://localhost:8080"),QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
           if rep == QMessageBox.Yes:
              f = open(self.pathPlugin + os.sep + "bin" + os.sep + "autorun.ini", "w")
              f.write("1")
              f.close()
           elif os.path.exists(self.pathPlugin + os.sep + "bin" + os.sep + "autorun.ini"):
              os.remove(self.pathPlugin + os.sep + "bin" + os.sep + "autorun.ini")


        self.stopMapproxy()

        #add Landsat8 Menu
        self.landsat8MapGeneratorAction = QAction(QIcon(self.pathPlugin + os.sep + "satellite.png"), "Landsat8 MapGenerator", self.iface.mainWindow())
        QObject.connect(self.landsat8MapGeneratorAction, SIGNAL("triggered()"), self.landsat8mapgenerator)
        self.iface.addPluginToMenu("MapProxy plugin", self.landsat8MapGeneratorAction)
        self.landsat8GetDataAction = QAction(QIcon(self.pathPlugin + os.sep + "satellite.png"), "Landsat8 GetData", self.iface.mainWindow())
        QObject.connect(self.landsat8GetDataAction, SIGNAL("triggered()"), self.landsat8getdata)
        self.iface.addPluginToMenu("MapProxy plugin", self.landsat8GetDataAction)

        
        projectdir = self.pathPlugin + os.sep + "project"
        mapproxy_execute.run("\"" + projectdir + "\"")
        
        #Layers
        files = glob.glob(projectdir + os.sep + "*.yaml")
        self.mpLayerTypeRegistry = MPLayerTypeRegistry()
        self.layerAddActions = []

        for filename in files:
            filebase = os.path.splitext(os.path.basename("\"" + filename + "\""))[0]
            yd = mapproxy_execute.layers("\"" + filename + "\"")

            for layer in yd['layers']:
                self.mpLayerTypeRegistry.add(
                    MPLayerType(self, filebase, layer['name'], layer['title'], filebase.split('_')[0] + '.png',
                                yd['services']['wms']['srs'],yd['services']['wms']['md']['abstract'],yd['services']['wms']['md']['access_constraints']))
        for layerType in self.mpLayerTypeRegistry.types():
            action = QAction(QIcon(self.pathPlugin + os.sep + layerType.icon), layerType.title, self.iface.mainWindow())
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
            shutil.rmtree(self.pathPlugin + os.sep + "project" + os.sep + "cache_data", True)

    def readme(self):
        projectdir = self.pathPlugin + os.sep + "project"
        #QtLinguist can't translate html. so use dummy string
        #readmestr = QCoreApplication.translate("message", "<h1>MapProxy Plugin</h1>"
        #                                                                              "<ol>"
        #                                                                              "<li>Install mapproxy</li>"
        #                                                                              "<li>Run mapproxy. If success, layers are added in the menu</li>"
        #                                                                              "<li>Select layer</li>"
        #                                                                              "</ol>"
        #                                                                              "<p>you can set layers by configuring yaml mapproxy file in this dirctory.<br>"
        #                                                                              "<a href='file:///" + projectdir + "'>" + projectdir + "</a></p>")
        QMessageBox.information(None, "ReadMe", QCoreApplication.translate("message","dummy"))

    def landsat8getdata(self):
        self.arealayer = self.iface.addVectorLayer(self.pathPlugin + os.sep + 'shp' + os.sep + 'landsat8area.shp','LANDSAT8 AREA','ogr')
        QMessageBox.information(None, "Usage",  QCoreApplication.translate("message", "Information Toolbar-->Select Area --> Run 'Action' (Landsat8 GetData)"))


    def landsat8mapgenerator(self,pos=""):
        if pos=="":
           _fromUtf8 = lambda s: s
           self.lsat8dlg.setWindowTitle("Landsat8 MapGenerator")
           icon = QIcon()
           icon.addPixmap(QPixmap(_fromUtf8(":/icon images/sun.png")), QIcon.Normal, QIcon.Off)
           self.lsat8dlg.pushButton.setIcon(icon)
           self.lsat8dlg.pushButton.setText("I'm Feeling Lucky")
           icon = QIcon()
           icon.addPixmap(QPixmap(_fromUtf8(":/icon images/cloud.png")), QIcon.Normal, QIcon.Off)
           self.lsat8dlg.pushButton_2.setIcon(icon)
           self.lsat8dlg.pushButton_2.setText("I'm Feeling Unlucky")


           self.lsat8dlg.pushButton.clicked.connect(self.feeling_fine)
           self.lsat8dlg.pushButton_2.clicked.connect(self.feeling_cloudy)
           self.lsat8dlg.show()
           result = self.lsat8dlg.exec_()
           if result:
              pass
           self.lsat8dlg.pushButton.clicked.disconnect(self.feeling_fine)
           self.lsat8dlg.pushButton_2.clicked.disconnect(self.feeling_cloudy)
        else:
           self.path = pos.split('_')[0]
           self.row = pos.split('_')[1]
           self.lsat8dlg.setWindowTitle("Landsat8 GetData [path:" + self.path + " row:" + self.row + "]")
           self.lsat8dlg.pushButton.setIcon(QIcon())
           self.lsat8dlg.pushButton.setText("GetWMS (all dates)")
           self.lsat8dlg.pushButton_2.setIcon(QIcon())
           self.lsat8dlg.pushButton_2.setText("GetWCS (most fine date)")

           self.lsat8dlg.pushButton.clicked.connect(self.getWMS)
           self.lsat8dlg.pushButton_2.clicked.connect(self.getWCS)
           self.lsat8dlg.show()
           result = self.lsat8dlg.exec_()
           if result:
              pass
           self.lsat8dlg.pushButton.clicked.disconnect(self.getWMS)
           self.lsat8dlg.pushButton_2.clicked.disconnect(self.getWCS)

       
    def feeling_fine(self):
         type = "fine"
         date_start = self.lsat8dlg.dateEdit.date().toString("yyyy-MM-dd")
         date_end = self.lsat8dlg.dateEdit_2.date().toString("yyyy-MM-dd")
         cloud_start = str(self.lsat8dlg.horizontalSlider.lowerValue)
         cloud_end = str(self.lsat8dlg.horizontalSlider.upperValue)
         name = "landsat8_" + date_start +"_"+ date_end +"_"+cloud_start+"_"+cloud_end+"_"+"fine"
         output = self.pathPlugin + os.sep + "project" + os.sep + name + ".yaml"
         data = landsat8_util.search_and_generate(type,date_start,date_end,cloud_start,cloud_end,output)
         if len(data)==0:
            QMessageBox.information(None, "Information:", QCoreApplication.translate("message", "No Search Result Found"))
            return
         self.run("auto")
         self.lsat8dlg.accept()
         for layerType in self.mpLayerTypeRegistry.types():
           if layerType.name == name:
              self.addLayer(layerType)


    def feeling_cloudy(self):
         type = "cloudy"
         date_start = self.lsat8dlg.dateEdit.date().toString("yyyy-MM-dd")
         date_end = self.lsat8dlg.dateEdit_2.date().toString("yyyy-MM-dd")
         cloud_start = str(self.lsat8dlg.horizontalSlider.lowerValue)
         cloud_end = str(self.lsat8dlg.horizontalSlider.upperValue)
         name = "landsat8_" + date_start +"_"+ date_end +"_"+cloud_start+"_"+cloud_end+"_"+"cloudy"
         output = self.pathPlugin + os.sep + "project" + os.sep + name + ".yaml"
         data = landsat8_util.search_and_generate(type,date_start,date_end,cloud_start,cloud_end,output)
         if len(data)==0:
            QMessageBox.information(None, "Information:", QCoreApplication.translate("message", "No Search Result Found"))
            return
         self.run("auto")
         self.lsat8dlg.accept()
         for layerType in self.mpLayerTypeRegistry.types():
           if layerType.name == name:
              self.addLayer(layerType)
 
    def getWMS(self):      
         path_start = self.path
         path_end = self.path
         row_start = self.row
         row_end = self.row
         type = "fine"
         date_start = self.lsat8dlg.dateEdit.date().toString("yyyy-MM-dd")
         date_end = self.lsat8dlg.dateEdit_2.date().toString("yyyy-MM-dd")
         cloud_start = str(self.lsat8dlg.horizontalSlider.lowerValue)
         cloud_end = str(self.lsat8dlg.horizontalSlider.upperValue)
         data = landsat8_util.search(type,date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end)
         if len(data)==0:
           QMessageBox.information(None, "Information:", QCoreApplication.translate("message", "No Search Result Found"))
           return
         self.lsat8dlg.accept()
         # output sorted 'id' by 'date'
         dd = {}
         for d in data:
             dd[d['id']]=d['date']
         sorted_data = [[key,value] for key, value in sorted(dd.items(),key=lambda x:x[1],reverse=False)]

         groupLayerID = self.iface.legendInterface().addGroup("landsat8wms[path:" + self.path + " row:" + self.row + "]")
         wmslayers=[]
         for d in sorted_data:
            wmslayer = self.iface.addRasterLayer("crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers=PANSHARPENED&styles=&url=http://ows.geogrid.org/land8wms/" + d[0] + "?",d[0] +"("+ d[1]+")", "wms")
            wmslayers.append(wmslayer)
            self.iface.legendInterface().moveLayer(wmslayer, groupLayerID)
         
         return wmslayers
     
    def getWCS(self):      
         path_start = self.path
         path_end = self.path
         row_start = self.row
         row_end = self.row
         type = "fine"
         date_start = self.lsat8dlg.dateEdit.date().toString("yyyy-MM-dd")
         date_end = self.lsat8dlg.dateEdit_2.date().toString("yyyy-MM-dd")
         cloud_start = str(self.lsat8dlg.horizontalSlider.lowerValue)
         cloud_end = str(self.lsat8dlg.horizontalSlider.upperValue)
         data = landsat8_util.search(type,date_start,date_end,cloud_start,cloud_end,path_start,path_end,row_start,row_end)
         if len(data)==0:
           QMessageBox.information(None, "Information:", QCoreApplication.translate("message", "No Search Result Found"))
           return
         self.lsat8dlg.accept()
         # output sorted 'id' by 'date'. and wcs use only most fine date.

         for d in data:
             if d['use']=='yes':
                dd=d

         groupLayerID = self.iface.legendInterface().addGroup("landsat8wcs[path:" + self.path + " row:" + self.row + " date:"+ dd['date'] + " id:" + dd['id'] +"]")
         
         for band in ["BANDQA","PANSHARPENED","BAND1","BAND2","BAND3","BAND4","BAND5","BAND6","BAND7","BAND8","BAND9","BAND10","BAND11"]:
              wcslayer = QgsRasterLayer("cache=PreferNetwork&crs=&format=GTiff&identifier="+ band + "&url=http://ows.geogrid.org/land8wcs/" + dd['id'],band, "wcs")
              if wcslayer.isValid():
                 # writeout to geotiff, but large data and slow. so now comment out
                 #file_name = "C://data/" + band + '.tif'
                 #file_writer = QgsRasterFileWriter(file_name)               
                 #pipe = QgsRasterPipe()
                 #provider = wcslayer.dataProvider()
                 #QgsMessageLog.logMessage(str(provider.xSize()) +" "+ str(provider.ySize()) + " " + str(provider.extent()))
                 #pipe.set(provider.clone())
                 #file_writer.writeRaster(pipe,provider.xSize(),provider.ySize(),provider.extent(),provider.crs())
                 QgsMapLayerRegistry.instance().addMapLayer(wcslayer)
                 self.iface.legendInterface().moveLayer(wcslayer, groupLayerID)


# This is joke but no use. 
#    def time_goes_by(self):
#         legend = self.iface.legendInterface().setLayerVisible(self.arealayer, False)
#         wmslayers = self.getWMS()
#         #self.iface.mapCanvas().setExtent(wmslayers[0].extent())
#         global g
#         g = TimeGoesBy(self,wmslayers)
#         g.runanim()
#         web = QWebView(self.iface.mapCanvas())
#         web.setGeometry(QRect(0,0,256,256))
#         web.settings().setAttribute(QWebSettings.PluginsEnabled, True)
#         web.load(QUrl("http://www.youtube.com/v/nKIu9yen5nc"))
#         web.show()
         