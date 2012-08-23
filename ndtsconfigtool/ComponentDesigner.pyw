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

        self.dsDirectory = "./datasources"
        self.cpDirectory = "./components"

        self.sourceList = DataSourceList(self.dsDirectory)
#        ds1 = LabeledObject("dataSource1", None)
#        self.sourceList.datasources[id(ds1)] =  ds1
#        ds2 = LabeledObject("dataSource2", None)
#        self.sourceList.datasources[id(ds2)] =  ds2
        self.sourceList.createGUI()

        self.componentList = ComponentList(self.cpDirectory)
        cp1 = LabeledObject("component1", None)
        self.componentList.components[id(cp1)] =  cp1
        cp2 = LabeledObject("component2", None)
        self.componentList.components[id(cp2)] =  cp2
        self.componentList.createGUI()

        self.dockSplitter = QSplitter(Qt.Vertical)
        self.dockSplitter.addWidget(self.componentList)
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
        self.pooling = True


        commandArgs = {'receiver':self}

        dsourceNewAction = self.pool.createAction("&New DataSource", "dsourceNew",  commandArgs, 
                                                  DataSourceNew,"Ctrl+D", "dsourceadd", 
                                                  "Create the new data source") 

        dsourceRemoveAction = self.pool.createAction("&Close DataSource", "dsourceRemove",  commandArgs, 
                                                  DataSourceRemove,"Ctrl+R", "dsourceremove", 
                                                  "Close the data source")


        dsourceEditAction = self.pool.createAction("&Edit DataSource", "dsourceEdit",  commandArgs, 
                                                  DataSourceEdit,"Ctrl+E", "dsourceedit", 
                                                  "Edit the data source")

       
        self.pool.createTask("dsourceChanged",commandArgs, DataSourceListChanged,
                             self.sourceList.sourceListWidget, 
                             "itemChanged(QListWidgetItem*)")

        self.pool.createTask("componentChanged",commandArgs, ComponentListChanged,
                             self.componentList.componentListWidget, 
                             "itemChanged(QListWidgetItem*)")


        self.pool.createTask("dsourceCurrentItemChanged",commandArgs, DataSourceCurrentItemChanged,
                             self.sourceList.sourceListWidget, 
                             "currentItemChanged(QListWidgetItem*,QListWidgetItem*)")

        self.pool.createTask("componentCurrentItemChanged",commandArgs, ComponentCurrentItemChanged,
                             self.componentList.componentListWidget, 
                             "currentItemChanged(QListWidgetItem*,QListWidgetItem*)")


#        self.pool.createTask("componentClicked",commandArgs, ComponentClicked,
#                             self.componentList.componentListWidget, 
#                             "clicked(QModelIndex)")


        self.connect(self.mdi, SIGNAL("windowActivated(QWidget*)"), self.mdiWindowActivated)

        

        componentNewAction = self.pool.createAction("&New", "componentNew",  commandArgs, ComponentNew,
                               QKeySequence.New, "componentnew", "Create the new component")


        componentOpenAction = self.pool.createAction("&Open", "componentOpen",  commandArgs, ComponentOpen,
                               QKeySequence.Open, "componentopen", "Open the component")

        componentRemoveAction = self.pool.createAction("&Close", "componentRemove",  commandArgs, 
                                                  ComponentRemove,"Ctrl+R", "componentremove", 
                                                  "Close the component")

        fileQuitAction = self.pool.createAction("&Quit", "closeApp", commandArgs, CloseApplication,
                               "Ctrl+Q", "filequit", "Close the application")

        undoAction = self.pool.createAction("&Undo", "undo",  commandArgs, UndoCommand,
                               "Ctrl+Z", "undo", "Undo the last command")
        reundoAction = self.pool.createAction("&Re-undo", "reundo",  commandArgs, ReundoCommand,
                               "Ctrl+Y", "redo", "Re-undo the last command")

        undoAction.setDisabled(True)
        reundoAction.setDisabled(True)




        fileMenu = self.menuBar().addMenu("&File")    
        self.addActions(fileMenu, ( componentNewAction, componentOpenAction,
                                    componentRemoveAction, None, fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (undoAction,reundoAction))
        fileMenu = self.menuBar().addMenu("Data&Sources")    
        self.addActions(fileMenu, (dsourceNewAction,dsourceEditAction,dsourceRemoveAction))
 
        self.windowMenu = self.menuBar().addMenu("&View")
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.windowMenu = self.menuBar().addMenu("&Help")

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolbar")

        self.addActions(fileToolbar, (componentNewAction,componentOpenAction, 
                                      componentRemoveAction, None,
                                      dsourceNewAction,dsourceEditAction,dsourceRemoveAction, None, 
                                      undoAction, reundoAction))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")


        settings = QSettings()

        self.loadDataSources()

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")


    def loadDataSources(self):
        self.sourceList.loadList()
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)
        


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
        self.pooling = False
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   
        self.pooling = True


    def componentRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   
        self.pooling = True


    def dsourceEdit(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
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


    def mdiWindowActivated(self, widget):
        self.pooling = False
        if isinstance(widget, DataSourceDlg):
            if widget.ids is not None:
                if hasattr(self.sourceList.currentListDataSource(),"id"):
                    if self.sourceList.currentListDataSource().id != widget.ids: 
                        self.sourceList.populateDataSources(widget.ids)
        self.pooling = True


    def componentClicked(self, index):
        if self.pooling:
            cmd = self.pool.getCommand('componentClicked').clone()
            cmd.index = index
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo",False)
            self.pool.setDisabled("reundo",True)   





    def dsourceCurrentItemChanged(self, item ,previousItem):
#        print "curr: " , item.text() if hasattr(item, "text") else item
#        print "prev: " , previousItem.text() if hasattr(previousItem, "text") else previousItem
        if self.pooling:
#            if item == previousItem  :
#                return
            if previousItem is None:
                return
            cmd = self.pool.getCommand('dsourceCurrentItemChanged').clone()
            cmd.item = item
            cmd.previousItem = previousItem
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo",False)
            self.pool.setDisabled("reundo",True)   


    def componentChanged(self, item):
        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   



    def componentCurrentItemChanged(self, item ,previousItem):
        print "curr: " , item.text() if hasattr(item, "text") else item
        print "prev: " , previousItem.text() if hasattr(previousItem, "text") else previousItem
        if self.pooling:
#            if item == previousItem  :
#                return
            if previousItem is None or item is None :
                return
            cmd = self.pool.getCommand('componentCurrentItemChanged').clone()
            cmd.item = item
            cmd.previousItem = previousItem
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo",False)
            self.pool.setDisabled("reundo",True)   


    def componentNew(self):
        cmd = self.pool.getCommand('componentNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   

    def componentOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   
        self.pooling = True


    def undo(self):
        self.pooling = False
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

        self.pooling = True

    def reundo(self):
        self.pooling = False
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
        self.pooling = True

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
    


