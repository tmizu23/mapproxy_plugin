#import time
from PyQt4.QtCore import *

 
class TimeGoesBy(QObject):
   
    def __init__(self,plugin,wmslayers):
        QObject.__init__(self)
        self.i=0
        self.plugin=plugin
        self.legend = plugin.iface.legendInterface()
        self.layers = wmslayers
        steps = len(self.layers)*2
        
        period_time = 3000
        duration = steps * period_time
        for layer in self.legend.layers():
            self.legend.setLayerVisible(layer, False)
        self.legend.setLayerVisible(self.layers[0], True)
        self._state = 0
        self.anim = QPropertyAnimation(self, "state")
        self.anim.setStartValue(0)
        self.anim.setEndValue(steps)
        self.anim.setDuration(duration)
        self.anim.valueChanged.connect(self.nextStep)

    @pyqtProperty(int)
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
       
       
    def nextStep(self):
        self.anim.pause()
        self.legend.setLayerVisible(self.layers[self.i-1], False)
        self.legend.setLayerVisible(self.layers[self.i], True)
        
        self.plugin.iface.mapCanvas().refresh()
        self.i=self.i+1
        if self.i==len(self.layers):
            self.i=0
        self.anim.resume()
   
    def runanim(self):
        self.anim.start()
        