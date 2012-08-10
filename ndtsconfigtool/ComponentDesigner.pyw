#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package ndtsconfigtool nexdatas
## \file ComponentDesigner.pyw
# GUI toi creates the XML components 

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import qrc_resources

    

__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)


        compDockWidget = QDockWidget("&Components:",self)
        compDockWidget.setObjectName("CompDockWidget")
        compDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |  Qt.RightDockWidgetArea)

        self.sourceFrame = QFrame(self)   
        self.sourceFrame.setFrameShape(QFrame.NoFrame)
        self.sourceLabel = QLabel("&DataSources:")
        self.sourceListWidget = QListWidget()
        self.sourceLayout = QVBoxLayout(self.sourceFrame)
        self.sourceLayout.addWidget(self.sourceLabel)
        self.sourceLayout.addWidget(self.sourceListWidget)
        self.sourceLabel.setBuddy(self.sourceListWidget)

        self.sourceLayout.setContentsMargins(0, 0, 0, 6)

        self.compListWidget = QListWidget()
        self.dockSplitter = QSplitter(Qt.Vertical)
        self.dockSplitter.addWidget(self.compListWidget)
        self.dockSplitter.addWidget(self.sourceFrame)
        self.dockSplitter.setStretchFactor(0,2)
        self.dockSplitter.setStretchFactor(1,1)
        compDockWidget.setWidget(self.dockSplitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, compDockWidget)
        


        self.mdi = QWorkspace()
        self.setCentralWidget(self.mdi)

        fileNewAction = self.createAction("&New", self.fileNew,
                                          QKeySequence.New, "filenew", "Create a text file")
        fileQuitAction = self.createAction("&Quit", self.close,
                                           "Ctrl+Q", "filequit", "Close the application")


        fileMenu = self.menuBar().addMenu("&File")    
        self.addActions(fileMenu, (fileNewAction,None,fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")

        self.windowMenu = self.menuBar().addMenu("&Window")

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolbar")

        self.addActions(fileToolbar, (fileNewAction, None))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")


        settings = QSettings()



        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    def fileNew(self):
        textEdit = QTextEdit()
        self.mdi.addWindow(textEdit)
        textEdit.show()



if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icon.png"))
    app.setOrganizationName("DESY")
    app.setOrganizationDomain("desy.de")
    app.setApplicationName("Component Designer")
    form = MainWindow()
    form.show()
    app.exec_()
    






