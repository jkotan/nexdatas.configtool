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

import platform
import qrc_resources

from CommandPool import *
from DataSourceList import *
from ComponentList import *

#__version__ = "1.0.0"
__version__ = "0.0.1"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.dsDirectory = "./datasources"
        self.cpDirectory = "./components"

        self.createGUI()

        self.createActions()

        settings = QSettings()

        self.loadDataSources()

        self.loadComponents()

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")



    def createGUI(self):
        self.compDockWidget = QDockWidget("&Components",self)
        self.compDockWidget.setObjectName("CompDockWidget")
        self.compDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |  Qt.RightDockWidgetArea)

        self.sourceList = DataSourceList(self.dsDirectory)
#        ds1 = LabeledObject("dataSource1", None)
#        self.sourceList.datasources[id(ds1)] =  ds1
#        ds2 = LabeledObject("dataSource2", None)
#        self.sourceList.datasources[id(ds2)] =  ds2
        self.sourceList.createGUI()

        self.componentList = ComponentList(self.cpDirectory)
#        cp1 = LabeledObject("component1", None)
#        self.componentList.components[id(cp1)] =  cp1
#        cp2 = LabeledObject("component2", None)
#        self.componentList.components[id(cp2)] =  cp2
        self.componentList.createGUI()

        self.dockSplitter = QSplitter(Qt.Vertical)
        self.dockSplitter.addWidget(self.componentList)
        self.dockSplitter.addWidget(self.sourceList)
        self.dockSplitter.setStretchFactor(0,3)
        self.dockSplitter.setStretchFactor(1,1)
        self.compDockWidget.setWidget(self.dockSplitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.compDockWidget)

        self.mdi = QWorkspace()
        self.mdi.setScrollBarsEnabled(True)        
        self.setCentralWidget(self.mdi)

        
    def createActions(self):
        self.pool = CommandPool(self)
        self.cmdStack = CommandStack()
        self.pooling = True


        commandArgs = {'receiver':self}

        dsourceNewAction = self.pool.createCommand("&New DataSource", "dsourceNew",  commandArgs, 
                                                  DataSourceNew,"Ctrl+D", "dsourceadd", 
                                                  "Create the new data source") 

        dsourceRemoveAction = self.pool.createCommand("&Close DataSource", "dsourceRemove",  commandArgs, 
                                                  DataSourceRemove,"Ctrl+R", "dsourceremove", 
                                                  "Close the data source")

        dsourceEditAction = self.pool.createCommand("&Edit DataSource", "dsourceEdit",  commandArgs, 
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

        self.connect(self.sourceList.sourceListWidget, SIGNAL("itemClicked(QListWidgetItem*)"), 
                     self.dsourceEdit)

        self.connect(self.componentList.componentListWidget, SIGNAL("itemClicked(QListWidgetItem*)"), 
                     self.componentEdit)

        

        componentNewAction = self.pool.createCommand("&New", "componentNew",  
                                                     commandArgs, ComponentNew,
                                                     QKeySequence.New, "componentnew", 
                                                     "Create the new component")

        componentEditAction = self.pool.createCommand("&Edit", "componentEdit",  
                                                     commandArgs, ComponentEdit,
                                                     "Ctrl+E", "componentedit", 
                                                     "Edit the component")


        componentRemoveItemAction = self.pool.createCommand("&Remove Item", "componentRemoveItem",  
                                                     commandArgs, ComponentRemoveItem,
                                                     "Ctrl+R", "componentremoveItem", 
                                                     "Remove the component item")



        componentOpenAction = self.pool.createCommand("&Open", "componentOpen",  
                                                      commandArgs, ComponentOpen,
                                                      QKeySequence.Open, "componentopen", 
                                                      "Open the component")

        componentRemoveAction = self.pool.createCommand("&Close", "componentRemove",  
                                                        commandArgs, ComponentRemove,
                                                        QKeySequence.Close, "componentremove", 
                                                        "Close the component")

        fileQuitAction = self.pool.createCommand("&Quit", "closeApp", commandArgs, 
                                                 CloseApplication, "Ctrl+Q", "filequit", 
                                                 "Close the application")

        undoAction = self.pool.createCommand("&Undo", "undo",  commandArgs, UndoCommand,
                                             "Ctrl+Z", "undo", "Undo the last command")
        reundoAction = self.pool.createCommand("&Re-undo", "reundo",  commandArgs, ReundoCommand,
                                               "Ctrl+Y", "redo", "Re-undo the last command")

        undoAction.setDisabled(True)
        reundoAction.setDisabled(True)

        self.windowNextAction = self.createAction(
            "&Next", self.mdi.activateNextWindow, 
            QKeySequence.NextChild, tip = "Go to the next window")
        self.windowPrevAction = self.createAction(
            "&Previous", self.mdi.activatePreviousWindow,
            QKeySequence.PreviousChild, tip = "Go to the previous window")
        self.windowCascadeAction = self.createAction(
            "Casca&de", self.mdi.cascade, tip = "Cascade the windows")
        self.windowTileAction = self.createAction(
            "&Tile", self.mdi.tile, tip = "Tile the windows")
        self.windowRestoreAction = self.createAction(
            "&Restore All", self.windowRestoreAll, tip = "Restore the windows")
        self.windowMinimizeAction = self.createAction(
            "&Iconize All", self.windowMinimizeAll, tip = "Minimize the windows")
        self.windowArrangeIconsAction = self.createAction(
            "&Arrange Icons", self.mdi.arrangeIcons, tip = "Arrange the icons")
        self.windowCloseAction = self.createAction(
            "&Close", self.mdi.closeActiveWindow, QKeySequence.Close,
            tip = "Close the window" )

        viewDockAction = self.compDockWidget.toggleViewAction()
        viewDockAction.setToolTip("Show/Hide the dock lists")
        viewDockAction.setStatusTip("Show/Hide the dock lists")

        self.windowMapper = QSignalMapper(self)
        self.connect(self.windowMapper, SIGNAL("mapped(QWidget*)"),
                     self.mdi, SLOT("setActiveWindow(QWidget*)"))

        helpAboutAction = self.createAction("&About Component Designer",
                self.helpAbout, tip = "About Component Designer")



        fileMenu = self.menuBar().addMenu("&File")    
        self.addActions(fileMenu, ( componentOpenAction, None, fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (undoAction,reundoAction))
        componentsMenu = self.menuBar().addMenu("&Components")    
        self.addActions(componentsMenu, ( componentNewAction, componentEditAction,componentRemoveAction, 
                                          componentRemoveItemAction))
        
        componentsAddMenu = componentsMenu.addMenu("&Add ...")
        
        datasourcesMenu = self.menuBar().addMenu("Data&Sources")    
        self.addActions(datasourcesMenu, (dsourceNewAction,dsourceEditAction,dsourceRemoveAction))
 
        viewMenu = self.menuBar().addMenu("&View")
        self.addActions(viewMenu, (viewDockAction,))


        self.windowMenu = self.menuBar().addMenu("&Window")
        self.connect(self.windowMenu, SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)

        self.menuBar().addSeparator()

        helpMenu = self.menuBar().addMenu("&Help") 
        self.addActions(helpMenu, (helpAboutAction, ))
        

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolbar")

        self.addActions(fileToolbar, (componentOpenAction, componentNewAction,componentEditAction, 
                                      componentRemoveAction, None,
                                      dsourceNewAction,dsourceEditAction,dsourceRemoveAction, None, 
                                      undoAction, reundoAction))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")
        


    def loadDataSources(self):
        self.sourceList.loadList()
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)
        



    def loadComponents(self):
        self.componentList.loadList()
        idc =  self.componentList.components.itervalues().next().id \
            if len(self.componentList.components) else None

        self.componentList.populateComponents(idc)
        


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

    def componentEdit(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   

    def componentRemoveItem(self):
        cmd = self.pool.getCommand('componentRemoveItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo",False)
        self.pool.setDisabled("reundo",True)   



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
        elif isinstance(widget, ComponentDlg):
            if widget.idc is not None:
                if hasattr(self.componentList.currentListComponent(),"id"):
                    if self.componentList.currentListComponent().id != widget.idc:
                        self.componentList.populateComponents(widget.idc)
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
        return
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
        return
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




    def windowRestoreAll(self):
        for dialog in self.mdi.windowList():
            dialog.showNormal()


    def windowMinimizeAll(self):
        for dialog in self.mdi.windowList():
            dialog.showMinimized()

    def helpAbout(self):
        QMessageBox.about(self, "About Component Designer",
                """<b>Component Designer</b> v {0}
                <p>Copyright &copy; 2012 GNU GENERAL PUBLIC LICENSE
                <p>This application can be used to create
                XML configuration file for the Nexus Data Writer.
                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR,
                platform.system()))


    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.addActions(self.windowMenu, (self.windowNextAction,
                self.windowPrevAction, self.windowCascadeAction,
                self.windowTileAction, self.windowRestoreAction,
                self.windowMinimizeAction,
                self.windowArrangeIconsAction, None,
                self.windowCloseAction))
        dialogs = self.mdi.windowList()
        if not dialogs:
            return
        self.windowMenu.addSeparator()
        i = 1
        menu = self.windowMenu
        for dialog in dialogs:
            title = dialog.windowTitle()
            if i == 10:
                self.windowMenu.addSeparator()
                menu = menu.addMenu("&More")
            accel = ""
            if i < 10:
                accel = "&{0} ".format(i)
            elif i < 36:
                accel = "&{0} ".format(chr(i + ord("@") - 9))
            action = menu.addAction("{0}{1}".format(accel, title))
            self.connect(action, SIGNAL("triggered()"),
                         self.windowMapper, SLOT("map()"))
            self.windowMapper.setMapping(action, dialog)
            i += 1



if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icon.png"))
    app.setOrganizationName("DESY")
    app.setOrganizationDomain("desy.de")
    app.setApplicationName("Component Designer")
    form = MainWindow()
    form.show()
    app.exec_()
    


