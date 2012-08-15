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

from CommandPool import *
from DataSourceList import *
from ComponentList import *

__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        compDockWidget = QDockWidget("&Components:",self)
        compDockWidget.setObjectName("CompDockWidget")
        compDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |  Qt.RightDockWidgetArea)

#        self.sourceFrame = QFrame(self)   
#        self.sourceFrame.setFrameShape(QFrame.NoFrame)
#        self.sourceLabel = QLabel("&DataSources:")
#        self.sourceListWidget = QListWidget()

        self.sourceList = DataSourceList(self)
        ds1 = LabeledObject("dataSource1", None)
        self.sourceList.datasources[id(ds1)] =  ds1
        ds2 = LabeledObject("dataSource2", None)
        self.sourceList.datasources[id(ds2)] =  ds2
        self.sourceList.createGUI()

#        self.sourceLayout = QVBoxLayout(self.sourceFrame)
#        self.sourceLayout.addWidget(self.sourceLabel)
#        self.sourceLayout.addWidget(self.sourceListWidget)
#        self.sourceLabel.setBuddy(self.sourceListWidget)

#        self.sourceLayout.setContentsMargins(0, 0, 0, 6)


        self.componentList = ComponentList(self)
        self.componentList.components={"component1":"Test run 1", "component2":"2012-1"}
        self.componentList.createGUI()

#        self.compListWidget = QListWidget()
        self.dockSplitter = QSplitter(Qt.Vertical)
        self.dockSplitter.addWidget(self.componentList)
#        self.dockSplitter.addWidget(self.compListWidget)
 #       self.dockSplitter.addWidget(self.sourceFrame)
        self.dockSplitter.addWidget(self.sourceList)
        self.dockSplitter.setStretchFactor(0,3)
        self.dockSplitter.setStretchFactor(1,1)
        compDockWidget.setWidget(self.dockSplitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, compDockWidget)

        self.mdi = QWorkspace()
        self.mdi.setScrollBarsEnabled(True)        
        self.setCentralWidget(self.mdi)


        self.pool = CommandPool(self)
        self.cmdStack = CommandStack()


        commandArgs = {'receiver':self}

        dsourceNewAction = self.pool.createAction("&New DataSource", "dsourceNew",  commandArgs, 
                                                  DataSourceNew,"Ctrl+D", "filenew", 
                                                  "Create a data source") 

        dsourceRemoveAction = self.pool.createAction("&Remove DataSource", "dsourceRemove",  commandArgs, 
                                                  DataSourceRemove,"Ctrl+R", "filequit", 
                                                  "Remove the data source")
       
        self.pool.createTask("dsourceChanged",commandArgs, DataSourceListChanged,
                             self.sourceList.sourceListWidget, "itemChanged(QListWidgetItem*)")


        fileNewAction = self.pool.createAction("&New", "fileNew",  commandArgs, FileNewCommand,
                               QKeySequence.New, "filenew", "Create a text file")

        fileQuitAction = self.pool.createAction("&Quit", "closeApp", commandArgs, CloseApplication,
                               "Ctrl+Q", "filequit", "Close the application")

        undoAction = self.pool.createAction("&Undo", "undo",  commandArgs, UndoCommand,
                               "Ctrl+Z", "icon", "Undo the loast command")
        reundoAction = self.pool.createAction("&Re-undo", "reundo",  commandArgs, ReundoCommand,
                               "Ctrl+Y", "icon", "Re-undo the loast command")

        undoAction.setDisabled(True)
        reundoAction.setDisabled(True)



#        fileNewAction = self.createAction("&New", "fileNew", self.fileNew,
#                                          QKeySequence.New, "filenew", "Create a text file")
#        fileQuitAction = self.createAction("&Quit", "close", self.close,
#                                           "Ctrl+Q", "filequit", "Close the application")


        fileMenu = self.menuBar().addMenu("&File")    
        self.addActions(fileMenu, ( fileNewAction,None,fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (undoAction,reundoAction))
        fileMenu = self.menuBar().addMenu("Data&Sources")    
        self.addActions(fileMenu, (dsourceNewAction,dsourceRemoveAction))
 
        self.windowMenu = self.menuBar().addMenu("&Window")

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolbar")

        self.addActions(fileToolbar, (fileNewAction, None,dsourceNewAction,dsourceRemoveAction, None, undoAction, reundoAction))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")


        settings = QSettings()



        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")


    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)



    def dsourceNew(self):
        cmd = self.pool.getCommand('dsourceNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   



    def dsourceRemove(self):
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   


    def dsourceChanged(self, item):
        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   


    def fileNew(self):
        cmd = self.pool.getCommand('fileNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   


    def undo(self):
        cmd = self.pool.getCommand('undo').clone()
        cmd.execute()

        ucmd = self.cmdStack.undo()
        if hasattr(ucmd,'unexecute'):
            ucmd.unexecute()
        else:
            
            print "Undo not possible"

        if self.cmdStack.isEmpty():
            self.pool.setDisabled("undo",True)
        self.pool.setDisabled("reundo",False)   


    def reundo(self):
        cmd = self.pool.getCommand('reundo').clone()
        cmd.execute()

        rucmd = self.cmdStack.reundo()
        if hasattr(rucmd,'execute'):
            rucmd.execute()
        else:
            print "Re-undo not possible"


        if self.cmdStack.isFinal():
            self.pool.setDisabled("reundo",True)
        self.pool.setDisabled("undo",False)   


    def closeApp(self):
        cmd = self.pool.getCommand('closeApp').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   




if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icon.png"))
    app.setOrganizationName("DESY")
    app.setOrganizationDomain("desy.de")
    app.setApplicationName("Component Designer")
    form = MainWindow()
    form.show()
    app.exec_()
    




