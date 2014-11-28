# -*- coding: utf-8 -*-

#import os

from PyQt4 import QtCore,QtGui
from landsat8_ui import *

class landsat8Dialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(landsat8Dialog, self).__init__(parent)
        self.setupUi(self)

