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

        self.contextMenuActions = None


        settings = QSettings()
        self.dsDirectory = unicode(settings.value("DataSources/directory").toString())
        self.cpDirectory = unicode(settings.value("Components/directory").toString())


        self.createGUI()

        self.createActions()


        self.loadDataSources()

        self.loadComponents()

        self.restoreGeometry(
                settings.value("MainWindow/Geometry").toByteArray())
        self.restoreState(
                settings.value("MainWindow/State").toByteArray())


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
        self.cmdStack = CommandStack(20)
        self.pooling = True


        commandArgs = {'receiver':self}

        dsourceNewAction = self.pool.createCommand(
            "&New DataSource", "dsourceNew",  commandArgs, 
            DataSourceNew,"Ctrl+S", "dsourceadd", "Create the new data source") 

        dsourceRemoveAction = self.pool.createCommand(
            "&Close DataSource", "dsourceRemove",  commandArgs, 
            DataSourceRemove,"Ctrl+R", "dsourceremove", "Close the data source")

        dsourceEditAction =  self.pool.createCommand(
            "&Edit DataSource", "dsourceEdit",  commandArgs, 
            DataSourceEdit,"Ctrl+E", "dsourceedit", "Edit the data source")

       
        self.pool.createTask("dsourceChanged",commandArgs, DataSourceListChanged,
                             self.sourceList.sourceListWidget, 
                             "itemChanged(QListWidgetItem*)")
        
        self.pool.createTask("componentChanged",commandArgs, ComponentListChanged,
                             self.componentList.componentListWidget, 
                             "itemChanged(QListWidgetItem*)")


        self.connect(self.mdi, SIGNAL("windowActivated(QWidget*)"), self.mdiWindowActivated)

        self.connect(self.sourceList.sourceListWidget, SIGNAL("itemClicked(QListWidgetItem*)"), 
                     self.dsourceEdit)

        self.connect(self.componentList.componentListWidget, SIGNAL("itemClicked(QListWidgetItem*)"), 
                     self.componentEdit)

        

        componentNewAction = self.pool.createCommand(
            "&New", "componentNew", commandArgs, ComponentNew,
            QKeySequence.New, "componentnew", "Create the new component")

        componentEditAction = self.pool.createCommand(
            "&Edit", "componentEdit", commandArgs, ComponentEdit,
            "Ctrl+E", "componentedit", "Edit the component")

        componentClearAction = self.pool.createCommand(
            "Clear", "componentClear", commandArgs, ComponentClear,
            "", "componentedit", "Clear the component")


        componentSaveAsAction = self.pool.createCommand(
            "Save &As...", "componentSaveAs", commandArgs, ComponentSaveAs,
            "", "componentsaveas", "Save the component as ...")


        componentSaveAction = self.pool.createCommand(
            "&Save", "componentSave", commandArgs, ComponentSave,
            "", "componentsave", "Save the component")

        componentSaveAllAction = self.pool.createCommand(
            "Save All", "componentSaveAll", commandArgs, ComponentSaveAll,
            "", "componentsaveall", "Save the all components")

        componentApplyItemAction = self.pool.createCommand(
            "&Apply Item", "componentApplyItem", commandArgs, ComponentApplyItem,
            "", "componentsapplyitem", "Apply the component item")


        dsourceApplyAction = self.pool.createCommand(
            "Apply DataSource", "dsourceApply", commandArgs, DataSourceApply,
            "", "datasourceapply", "Apply the datasource")


        dsourceSaveAction = self.pool.createCommand(
            "Save DataSource", "dsourceSave", commandArgs, DataSourceSave,
            "", "datasourcesave", "Save the datasource")


        dsourceSaveAsAction = self.pool.createCommand(
            "Save DataSource As...", "dsourceSaveAs", commandArgs, DataSourceSaveAs,
            "", "datasourcesaveas", "Save the datasource as ...")

        dsourceSaveAllAction = self.pool.createCommand(
            "Save All DataSources", "dsourceSaveAll", commandArgs, DataSourceSaveAll,
            "", "dsourcessaveall", "Save the all datasources")


        dsourceCopyAction = self.pool.createCommand(
            "Copy DataSource", "dsourceCopy", 
            commandArgs, DataSourceCopy,
            "", "dsourcecopy", "copy datasouce")


        dsourceCutAction = self.pool.createCommand(
            "Cut DataSource", "dsourceCut", 
            commandArgs, DataSourceCut,
            "", "dsourcecut", "cut datasouce")


        dsourcePasteAction = self.pool.createCommand(
            "Paste DataSource", "dsourcePaste", 
            commandArgs, DataSourcePaste,
            "", "dsourcepaste", "paste datasouce")
        

        componentRemoveItemAction = self.pool.createCommand(
            "C&ut Component Item", "componentRemoveItem", commandArgs, ComponentRemoveItem,
#            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_X),
#            "Ctrl+X",
            "" ,
            "componentremoveitem", "Remove the component item")


        componentCopyItemAction = self.pool.createCommand(
            "&Copy Component Item", "componentCopyItem", commandArgs, ComponentCopyItem,
#            QKeySequence(Qt.CTRL + Qt.SHIFT  + Qt.Key_C),
#            "Ctrl+C", 
            "" ,
            "componentcopyitem", "Copy the component item")


        componentPasteItemAction = self.pool.createCommand(
            "&Paste Component Item", "componentPasteItem", commandArgs, ComponentPasteItem,
#            QKeySequence(Qt.CTRL +  Qt.SHIFT  + Qt.Key_V),
#            "Ctrl+V", 
            "" ,
            "componentpasteitem", "Paste the component item")




        cutItemAction = self.pool.createCommand(
            "C&ut Item", "cutItem", commandArgs, CutItem,
            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_X),
#            "Ctrl+X",
            "cut", "Cut the item")


        copyItemAction = self.pool.createCommand(
            "&Copy Item", "copyItem", commandArgs, CopyItem,
            QKeySequence(Qt.CTRL + Qt.SHIFT  + Qt.Key_C),
#            "Ctrl+C", 
            "copy", "Copy the item")


        pasteItemAction = self.pool.createCommand(
            "&Paste Item", "pasteItem", commandArgs, PasteItem,
            QKeySequence(Qt.CTRL +  Qt.SHIFT  + Qt.Key_V),
#            "Ctrl+V", 
            "paste", "Paste the item")
        

        componentNewGroupAction = self.pool.createCommand(
            "New Group Item", "componentNewGroupItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component group")


        componentNewFieldAction = self.pool.createCommand(
            "New Field Item", "componentNewFieldItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component field")

        componentNewAttributeAction = self.pool.createCommand(
            "New Attribute Item", "componentNewAttributeItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component attribute")

        componentNewLinkAction = self.pool.createCommand(
            "New Link Item", "componentNewLinkItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component link")
        

        componentNewDataSourceAction = self.pool.createCommand(
            "New DataSource Item", "componentNewDataSourceItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component datasource")


        componentLoadComponentAction = self.pool.createCommand(
            "Load SubComponent Item...", "componentLoadComponentItem", commandArgs, ComponentLoadComponentItem,
            "", "componentloaditem", "Load a component part from the file")


        componentLoadDataSourceAction = self.pool.createCommand(
            "Load DataSource Item...", "componentLoadDataSourceItem", commandArgs, ComponentLoadDataSourceItem,
            "", "componentloaditem", "Load datasouce from the file")


        componentAddDataSourceAction = self.pool.createCommand(
            "Add DataSource Item", "componentAddDataSourceItem", 
            commandArgs, ComponentAddDataSourceItem,
            "", "componentadditem", "add datasouce from the file")


        componentMergeAction = self.pool.createCommand(
            "Merge component Items", "componentMerge", commandArgs, ComponentMerge,
            "", "componentmerge", "Merge the component items")
        

        componentChangeDirectoryAction = self.pool.createCommand(
            "Change Component Directory...", "componentChangeDirectory", commandArgs, 
            ComponentChangeDirectory,
            "", "componentrechangedirecotry", "Change the component list directory")



        dsourceChangeDirectoryAction = self.pool.createCommand(
            "Change DataSource Directory...", "dsourceChangeDirectory", commandArgs, 
            DataSourceChangeDirectory,
            "", "dsourcerechangedirecotry", "Change the datasource list directory")


        
        componentReloadListAction = self.pool.createCommand(
            "Reload Component List", "componentReloadList", commandArgs, ComponentReloadList,
            "", "componentreloadlist", "Reload the component list")


        dsourceReloadListAction = self.pool.createCommand(
            "Reload DataSource List", "dsourceReloadList", commandArgs, DataSourceReloadList,
            "", "dsourcereloadlist", "Reload the datasource list")

        dsourceOpenAction = self.pool.createCommand(
            "&Open DataSource...", "dsourceOpen", commandArgs, DataSourceOpen,
            "", "componentdatasource", "Open the datasource")


        componentOpenAction = self.pool.createCommand(
            "&Open...", "componentOpen", commandArgs, ComponentOpen,
            QKeySequence.Open, "componentopen", "Open the component")
        
        componentRemoveAction = self.pool.createCommand(
            "&Close", "componentRemove", commandArgs, ComponentRemove,
            QKeySequence.Close, "componentremove", "Close the component")

        fileQuitAction = self.pool.createCommand(
            "&Quit", "closeApp", commandArgs, CloseApplication, "Ctrl+Q", "filequit", 
            "Close the application")

        undoAction = self.pool.createCommand("&Undo", "undo",  commandArgs, UndoCommand, 
                                             "Ctrl+Z", "undo", "Can't Undo")
        redoAction = self.pool.createCommand("&Redo", "redo",  commandArgs, RedoCommand,
                                               "Ctrl+Y", "redo", "Can't Redo")

        undoAction.setDisabled(True)
        redoAction.setDisabled(True)

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
        self.addActions(fileMenu, (                 
                componentNewAction, componentOpenAction, componentEditAction, None, 
                componentSaveAction, componentSaveAsAction,
                componentSaveAllAction, None, 
                componentClearAction,componentRemoveAction,
                None,
                componentReloadListAction,
                dsourceReloadListAction,
                componentChangeDirectoryAction,
                dsourceChangeDirectoryAction,
                None, 
                fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (
                undoAction,redoAction,
                None,
                cutItemAction, 
                copyItemAction,
                pasteItemAction,
                ))
        componentsMenu = self.menuBar().addMenu("C&omponents")    
        self.addActions(componentsMenu, ( 
                componentNewGroupAction, componentNewFieldAction, 
                componentNewAttributeAction, componentNewLinkAction,
                componentNewDataSourceAction,None, 
                componentApplyItemAction, None,
                componentLoadComponentAction, componentLoadDataSourceAction,
                None,
                componentRemoveItemAction, 
                componentCopyItemAction,
                componentPasteItemAction,
                None,
                componentAddDataSourceAction,
                None,
                componentMergeAction
                ))

        self.mdi.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.contextMenuActions =  ( 
            componentNewGroupAction, componentNewFieldAction,
            componentNewAttributeAction, componentNewLinkAction,
            componentNewDataSourceAction, None,
            componentLoadComponentAction, componentLoadDataSourceAction,
            None,
            componentAddDataSourceAction,
            None,
            componentRemoveItemAction, 
            componentCopyItemAction,
            componentPasteItemAction,
            None,
            componentMergeAction
            ) 
        

        datasourcesMenu = self.menuBar().addMenu("Data&Sources")    
        self.addActions(datasourcesMenu, (dsourceNewAction, dsourceOpenAction, 
                                          dsourceEditAction, None, 
                                          dsourceSaveAction,
                                          dsourceSaveAsAction,
                                          dsourceSaveAllAction, None,
                                          dsourceCutAction,
                                          dsourceCopyAction,
                                          dsourcePasteAction,
                                          None,
                                          dsourceRemoveAction))
 

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
                                      componentRemoveAction, 
                                      None,
                                      cutItemAction, copyItemAction, pasteItemAction,
                                      None,
                                      undoAction, redoAction,
                                      None, 
                                      dsourceNewAction,dsourceEditAction,dsourceRemoveAction
                                      ))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")
        

    def closeEvent(self, event):
#        failures = []
#        for widget in self.mdi.windowList():
#            if widget.isModified():
#                try:
#                    widget.save()
#                except IOError, e:
#                    failures.append(unicode(e))
#        if (failures and
#            QMessageBox.warning(self, "Text Editor -- Save Error",
#                    "Failed to save%s\nQuit anyway?"  % str(
#                    "\n\t".join(failures)),
#                    QMessageBox.Yes|QMessageBox.No) ==
#                    QMessageBox.No):
#            event.ignore()
#            return
        settings = QSettings()
        settings.setValue("MainWindow/Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("MainWindow/State",
                          QVariant(self.saveState()))
        settings.setValue("DataSources/directory",
                          QVariant(self.dsDirectory))
        settings.setValue("Components/directory",
                          QVariant(self.cpDirectory))
        files = QStringList()
#        for widget in self.mdi.windowList():
#            if not widget.filename.startsWith("Unnamed"):
#                files.append(widget.filename)
#        settings.setValue("CurrentFiles", QVariant(files))
        self.mdi.closeAllWindows()


    def loadDataSources(self):
#        self.sourceList.datasources = {}
        self.sourceList.loadList(self.dsourceSave, self.dsourceApply)
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)
        



    def loadComponents(self):
#        self.componentList.components = {}
        self.componentList.loadList(self.contextMenuActions,
                                    self.componentSave,
                                    self.componentApplyItem
                                    )
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
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")   



    def dsourceRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True

    def componentEdit(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

    def componentClear(self):
        cmd = self.pool.getCommand('componentClear').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    def componentSave(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('componentSave').clone()
        cmd.execute()
#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

    def componentChangeDirectory(self):
        cmd = self.pool.getCommand('componentChangeDirectory').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def dsourceChangeDirectory(self):
        cmd = self.pool.getCommand('dsourceChangeDirectory').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentReloadList(self):
        cmd = self.pool.getCommand('componentReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentApplyItem(self):
        cmd = self.pool.getCommand('componentApplyItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    def dsourceReloadList(self):
        cmd = self.pool.getCommand('dsourceReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      

    def dsourceApply(self):
        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def dsourceSave(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceSave').clone()
        cmd.execute()

    def dsourceSaveAs(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmdSA = self.pool.getCommand('dsourceSaveAs').clone()
        cmdSA.execute()

        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.directory = cmdSA.directory
        cmd.newName = cmdSA.newName
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceSave').clone()
        cmd.execute()


    def dsourceSaveAll(self):
        cmd = self.pool.getCommand('dsourceSaveAll').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentSaveAs(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmdSA = self.pool.getCommand('componentSaveAs').clone()
        cmdSA.execute()

        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.directory = cmdSA.directory
        cmd.newName = cmdSA.newName
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


        cmd = self.pool.getCommand('componentSave').clone()
        cmd.execute()


#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True)   
#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentSaveAll(self):
        cmd = self.pool.getCommand('componentSaveAll').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def componentRemoveItem(self):
        cmd = self.pool.getCommand('componentRemoveItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentPasteItem(self):
        cmd = self.pool.getCommand('componentPasteItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        
    def componentCopyItem(self):
        cmd = self.pool.getCommand('componentCopyItem').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def dsourceCopy(self):
        cmd = self.pool.getCommand('dsourceCopy').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      



    def dsourceCut(self):
        cmd = self.pool.getCommand('dsourceCut').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def dsourcePaste(self):
        cmd = self.pool.getCommand('dsourcePaste').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def copyItem(self):
        cmd = self.pool.getCommand('copyItem').clone()
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd.type = "component"
        elif isinstance(self.mdi.activeWindow(),DataSourceDlg):
            cmd.type = "datasource"
        else:
            cmd.type = None
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      



    def cutItem(self):
        cmd = self.pool.getCommand('cutItem').clone()
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd.type = "component"
        elif isinstance(self.mdi.activeWindow(),DataSourceDlg):
            cmd.type = "datasource"
        else:
            cmd.type = None

        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def pasteItem(self):
        cmd = self.pool.getCommand('pasteItem').clone()
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd.type = "component"
        elif isinstance(self.mdi.activeWindow(),DataSourceDlg):
            cmd.type = "datasource"
        else:
            cmd.type = None
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def componentNewGroupItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewGroupItem').clone()
            cmd.itemName = 'group' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentNewFieldItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewFieldItem').clone()
            cmd.itemName = 'field' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentNewAttributeItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewAttributeItem').clone()
            cmd.itemName = 'attribute' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
            

    def componentNewLinkItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewLinkItem').clone()
            cmd.itemName = 'link' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      



    def componentNewDataSourceItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewDataSourceItem').clone()
            cmd.itemName = 'datasource' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      



    def componentLoadComponentItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentLoadComponentItem').clone()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      



    def componentLoadDataSourceItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentLoadDataSourceItem').clone()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      




    def componentAddDataSourceItem(self):
        cmd = self.pool.getCommand('componentAddDataSourceItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def componentMerge(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    def componentRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    def dsourceEdit(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def dsourceChanged(self, item):
        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


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


    def componentChanged(self, item):
        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def componentNew(self):
        cmd = self.pool.getCommand('componentNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    def componentOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    def dsourceOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('dsourceOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
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
            self.pool.setDisabled("undo", True, "Can't Undo")   
        else:
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )   
        self.pool.setDisabled("redo", False, "Redo: ", self.cmdStack.getRedoName() )   

        self.pooling = True

    def redo(self):
        self.pooling = False
        cmd = self.pool.getCommand('redo').clone()
        cmd.execute()

        rucmd = self.cmdStack.redo()
        if hasattr(rucmd,'execute'):
            rucmd.execute()
        else:
            print "Redo not possible"

        if self.cmdStack.isFinal():
            self.pool.setDisabled("redo", True, "Can't Redo")   
        else:
            self.pool.setDisabled("redo", False, "Redo: ", self.cmdStack.getRedoName() )    
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )   
        self.pooling = True

    def closeApp(self):
        cmd = self.pool.getCommand('closeApp').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png"% str(icon).strip()))
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
                """<b>Component Designer</b> v %s
                <p>Copyright &copy; 2012 GNU GENERAL PUBLIC LICENSE
                <p>This application can be used to create
                XML configuration file for the Nexus Data Writer.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (
                str(__version__), 
                str(platform.python_version()),
                str(QT_VERSION_STR), 
                str(PYQT_VERSION_STR),
                str(platform.system())))


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
                accel = "&%s " % str(i)
            elif i < 36:
                accel = "&%s " % str(chr(i + ord("@") - 9))
            action = menu.addAction("%s%s" % (accel, title))
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
    


