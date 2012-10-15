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
## \file MainWindow.py
# Main window of the application

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import platform
from qrc import qrc_resources

from CommandPool import *
from DataSourceList import *
from ComponentList import *


from ConfigurationServer import *

#__version__ = "1.0.0"
## version of the application
__version__ = "0.0.1"

## main window class
class MainWindow(QMainWindow):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        ## datasource directory
        self.dsDirectory = "./datasources"
        ## component directory
        self.cpDirectory = "./components"

        ## component menu under mouse cursor
        self.contextMenuActions = None

        ## dock with components and datasources
        self.compDockWidget = None

        ## list of datasources
        self.sourceList =  None
        ## list of components
        self.componentList =    None
        
        ## multi window workspace
        self.mdi = None
        ## pool with commands
        self.pool = None
        ## stack with used commands
        self.cmdStack = None

        ## configuration server
        self.configServer = None
        
        ## if pooling applicable
        self.pooling = True

        # dictionary with window actions
        self.windows = {}

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


        if PYTANGO_AVAILABLE:
            self.configServer = ConfigurationServer()
            self.configServer.device = unicode(settings.value("ConfigServer/device").toString())
            self.configServer.host = unicode(settings.value("ConfigServer/host").toString())
            port = unicode(settings.value("ConfigServer/port").toString())
            if port:
                self.configServer.port = int(port)
            

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")



    def createGUI(self):
        self.compDockWidget = QDockWidget("&Components",self)
        self.compDockWidget.setObjectName("CompDockWidget")
        self.compDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |  Qt.RightDockWidgetArea)

        self.sourceList = DataSourceList(self.dsDirectory)
        self.sourceList.createGUI()

        self.componentList = ComponentList(self.cpDirectory)
        self.componentList.createGUI()

        dockSplitter = QSplitter(Qt.Vertical)
        dockSplitter.addWidget(self.componentList)
        dockSplitter.addWidget(self.sourceList)
        dockSplitter.setStretchFactor(0,2)
        dockSplitter.setStretchFactor(1,1)
        self.compDockWidget.setWidget(dockSplitter)
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
            DataSourceNew,"Ctrl+Shift+N", "dsourceadd", "Create a new data source") 

        dsourceRemoveAction = self.pool.createCommand(
            "&Close DataSource", "dsourceRemove",  commandArgs, 
            DataSourceRemove,"Ctrl+Shift+R", "dsourceremove", "Close the data source")

        dsourceEditAction =  self.pool.createCommand(
            "&Edit DataSource", "dsourceEdit",  commandArgs, 
            DataSourceEdit,
            "Ctrl+Shift+E", 
            "dsourceedit", "Edit the data source")

       
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
            QKeySequence.New, "componentnew", "Create a new component")

        componentEditAction = self.pool.createCommand(
            "&Edit", "componentEdit", commandArgs, ComponentEdit,
            "Ctrl+E", "componentedit", "Edit the component")

        componentClearAction = self.pool.createCommand(
            "Clear", "componentClear", commandArgs, ComponentClear,
            "", "componentclear", "Clear the component")


        componentSaveAsAction = self.pool.createCommand(
            "Save &As...", "componentSaveAs", commandArgs, ComponentSaveAs,
            "", "componentsaveas", "Write the component into a file as ...")


        componentCollectAction = self.pool.createCommand(
            "&Save", "componentCollect", commandArgs, ComponentCollect,
            "", "componentcollect", "Save the component in a file or in the configuration server")

        componentSaveAction = self.pool.createCommand(
            "&Save", "componentSave", commandArgs, ComponentSave,
            "Ctrl+S", "componentsave", "Write the component into a file")



        componentSaveAllAction = self.pool.createCommand(
            "Save All", "componentSaveAll", commandArgs, ComponentSaveAll,
            "", "componentsaveall", "Write all components into files")

        componentApplyItemAction = self.pool.createCommand(
            "&Apply Component Item", "componentApplyItem", commandArgs, ComponentApplyItem,
            "Ctrl+A", "componentsapplyitem", "Apply the component item")


        dsourceApplyAction = self.pool.createCommand(
            "Apply DataSource", "dsourceApply", commandArgs, DataSourceApply,
            "Ctrl+Shift+A", "dsourceapply", "Apply the data source")


        dsourceSaveAction = self.pool.createCommand(
            "&Save DataSource", "dsourceSave", commandArgs, DataSourceSave,
            "Ctrl+Shift+S", "dsourcesave", "Write the data source into a file")

        dsourceCollectAction = self.pool.createCommand(
            "&Save DataSource", "dsourceCollect", commandArgs, DataSourceCollect,
            "", "dsourcesave", "Save the data source in a file or in the configuration server")


        dsourceSaveAsAction = self.pool.createCommand(
            "Save DataSource &As...", "dsourceSaveAs", commandArgs, DataSourceSaveAs,
            "", "dsourcesaveas", "Write the data source  in a file as ...")

        dsourceSaveAllAction = self.pool.createCommand(
            "Save All DataSources", "dsourceSaveAll", commandArgs, DataSourceSaveAll,
            "", "dsourcessaveall", "Write all data sources in files")


        dsourceCopyAction = self.pool.createCommand(
            "Copy DataSource", "dsourceCopy", 
            commandArgs, DataSourceCopy,
            "", "copy", "Copy the data source")


        dsourceCutAction = self.pool.createCommand(
            "Cut DataSource", "dsourceCut", 
            commandArgs, DataSourceCut,
            "", "cut", "Cut the data source")


        dsourcePasteAction = self.pool.createCommand(
            "Paste DataSource", "dsourcePaste", 
            commandArgs, DataSourcePaste,
            "", "paste", "Paste the data source")
        

        componentRemoveItemAction = self.pool.createCommand(
            "Cut Component Item", "componentRemoveItem", commandArgs, ComponentRemoveItem,
#            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_X),
#            "Ctrl+X",
            "" ,
            "cut", "Remove the component item")


        componentCopyItemAction = self.pool.createCommand(
            "Copy Component Item", "componentCopyItem", commandArgs, ComponentCopyItem,
#            QKeySequence(Qt.CTRL + Qt.SHIFT  + Qt.Key_C),
#            "Ctrl+C", 
            "" ,
            "copy", "Copy the component item")


        componentPasteItemAction = self.pool.createCommand(
            "Paste Component Item", "componentPasteItem", commandArgs, ComponentPasteItem,
#            QKeySequence(Qt.CTRL +  Qt.SHIFT  + Qt.Key_V),
#            "Ctrl+V", 
            "" ,
            "paste", "Paste the component item")




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
            "New &Group Item", "componentNewGroupItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component group")


        componentNewFieldAction = self.pool.createCommand(
            "New &Field Item", "componentNewFieldItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component field")

        componentNewAttributeAction = self.pool.createCommand(
            "New A&ttribute Item", "componentNewAttributeItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component attribute")

        componentNewLinkAction = self.pool.createCommand(
            "New &Link Item", "componentNewLinkItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component link")
        

        componentNewDataSourceAction = self.pool.createCommand(
            "New &DataSource Item", "componentNewDataSourceItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component data source")


        componentLoadComponentAction = self.pool.createCommand(
            "Load SubComponent Item...", "componentLoadComponentItem", commandArgs, ComponentLoadComponentItem,
            "", "componentloaditem", "Load an existing component part from the file")


        componentLoadDataSourceAction = self.pool.createCommand(
            "Load DataSource Item...", "componentLoadDataSourceItem", commandArgs, ComponentLoadDataSourceItem,
            "", "componentloaditem", "Load an existing data source from the file")


        componentAddDataSourceAction = self.pool.createCommand(
            "Add DataSource Item", "componentAddDataSourceItem", 
            commandArgs, ComponentAddDataSourceItem,
            "", "componentadditem", "Add the data source from the file")


        componentMergeAction = self.pool.createCommand(
            "Merge Component", "componentMerge", commandArgs, ComponentMerge,
            "", "componentmerge", "Merge the component")
        

        componentChangeDirectoryAction = self.pool.createCommand(
            "Change Component Directory...", "componentChangeDirectory", commandArgs, 
            ComponentChangeDirectory,
            "", "componentrechangedirecotry", "Change the component list directory")



        dsourceChangeDirectoryAction = self.pool.createCommand(
            "Change DataSource Directory...", "dsourceChangeDirectory", commandArgs, 
            DataSourceChangeDirectory,
            "", "dsourcerechangedirecotry", "Change the data-source list directory")


        
        componentReloadListAction = self.pool.createCommand(
            "Reload Component List", "componentReloadList", commandArgs, ComponentReloadList,
            "", "componentreloadlist", "Reload the component list")


        dsourceReloadListAction = self.pool.createCommand(
            "Reload DataSource List", "dsourceReloadList", commandArgs, DataSourceReloadList,
            "", "dsourcereloadlist", "Reload the data-source list")

        dsourceOpenAction = self.pool.createCommand(
            "&Open DataSource...", "dsourceOpen", commandArgs, DataSourceOpen,
            "Ctrl+Shift+O", "dsourceopen", "Open an existing data source")


        componentOpenAction = self.pool.createCommand(
            "&Open...", "componentOpen", commandArgs, ComponentOpen,
            QKeySequence.Open, "componentopen", "Open an existing component")
        
        componentRemoveAction = self.pool.createCommand(
            "&Close", "componentRemove", commandArgs, ComponentRemove,
            "Ctrl+R", "componentremove", "Close the component")





        serverConnectAction = self.pool.createCommand(
            "&Connect ...", "serverConnect", commandArgs, ServerConnect,
            "Ctrl+T", "serverconnect", "Connect to the configuration server")

        serverFetchComponentsAction = self.pool.createCommand(
            "&Fetch Components", "serverFetchComponents", commandArgs, ServerFetchComponents,
            "Ctrl+F", "serverfetchdatasources", "Fetch datasources from the configuration server")

        serverFetchDataSourcesAction = self.pool.createCommand(
            "&Fetch DataSources", "serverFetchDataSources", commandArgs, ServerFetchDataSources,
            "Ctrl+Shift+F", "serverfetchdatasources", "Fetch datasources from the configuration server")

        serverStoreComponentAction = self.pool.createCommand(
            "&Save Component", "serverStoreComponent", commandArgs, ServerStoreComponent,
            "Ctrl+B", "serverstoredatasource", "Store datasource in the configuration server")

        serverStoreDataSourceAction = self.pool.createCommand(
            "&Save Datasource", "serverStoreDataSource", commandArgs, ServerStoreDataSource,
            "Ctrl+Shift+B", "serverstoredatasource", "Store datasource in the configuration server")

        serverDeleteComponentAction = self.pool.createCommand(
            "&Delete Component", "serverDeleteComponent", commandArgs, ServerDeleteComponent,
            "", "serverdeletedatasource", "Delete datasource from the configuration server")

        serverDeleteDataSourceAction = self.pool.createCommand(
            "&Delete Datasource", "serverDeleteDataSource", commandArgs, ServerDeleteDataSource,
            "", "serverdeletedatasource", "Delete datasource from the configuration server")

        serverSetMandatoryComponentAction = self.pool.createCommand(
            "Set Component Mandatory", "serverSetMandatoryComponent", 
            commandArgs, ServerSetMandatoryComponent,
            "", "serversetmandatory", "Set the component as mandatory  on the configuration server")

        serverGetMandatoryComponentsAction = self.pool.createCommand(
            "Get Mandatory Components", "serverGetMandatoryComponents", 
            commandArgs, ServerGetMandatoryComponents,
            "", "servergetmandatory", "Get mandatory components  from the configuration server")

        serverUnsetMandatoryComponentAction = self.pool.createCommand(
            "Unset Component Mandatory", "serverUnsetMandatoryComponent", 
            commandArgs, ServerUnsetMandatoryComponent,
            "", "serverunsetmandatory", "Unset the component as mandatory on the configuration server")

        serverCloseAction = self.pool.createCommand(
            "C&lose", "serverClose", commandArgs, ServerClose,
            "Ctrl+L", "serverclose", "Close connection to the configuration server")

        
        if not PYTANGO_AVAILABLE:
            serverConnectAction.setDisabled(True)

        serverFetchComponentsAction.setDisabled(True)
        serverStoreComponentAction.setDisabled(True)
        serverDeleteComponentAction.setDisabled(True)
        serverGetMandatoryComponentsAction.setDisabled(True)
        serverSetMandatoryComponentAction.setDisabled(True)
        serverUnsetMandatoryComponentAction.setDisabled(True)
        serverFetchDataSourcesAction.setDisabled(True)
        serverStoreDataSourceAction.setDisabled(True)
        serverDeleteDataSourceAction.setDisabled(True)
        serverCloseAction.setDisabled(True)



        fileQuitAction = self.pool.createCommand(
            "&Quit", "closeApp", commandArgs, CloseApplication, "Ctrl+Q", "filequit", 
            "Close the application")

        undoAction = self.pool.createCommand("&Undo", "undo",  commandArgs, UndoCommand, 
                                             "Ctrl+Z", "undo", "Can't Undo")
        redoAction = self.pool.createCommand("&Redo", "redo",  commandArgs, RedoCommand,
                                               "Ctrl+Y", "redo", "Can't Redo")

        undoAction.setDisabled(True)
        redoAction.setDisabled(True)



        self.windows["NextAction"] = self.createAction(
            "&Next", self.mdi.activateNextWindow, 
            QKeySequence.NextChild, tip = "Go to the next window")
        self.windows["PrevAction"] = self.createAction(
            "&Previous", self.mdi.activatePreviousWindow,
            QKeySequence.PreviousChild, tip = "Go to the previous window")
        self.windows["CascadeAction"] = self.createAction(
            "Casca&de", self.mdi.cascade, tip = "Cascade the windows")
        self.windows["TileAction"] = self.createAction(
            "&Tile", self.mdi.tile, tip = "Tile the windows")
        self.windows["RestoreAction"] = self.createAction(
            "&Restore All", self.windowRestoreAll, tip = "Restore the windows")
        self.windows["MinimizeAction"] = self.createAction(
            "&Iconize All", self.windowMinimizeAll, tip = "Minimize the windows")
        self.windows["ArrangeIconsAction"] = self.createAction(
            "&Arrange Icons", self.mdi.arrangeIcons, tip = "Arrange the icons")
        self.windows["CloseAction"] = self.createAction(
            "&Close", self.mdi.closeActiveWindow, QKeySequence.Close,
            tip = "Close the window" )

        viewDockAction = self.compDockWidget.toggleViewAction()
        viewDockAction.setToolTip("Show/Hide the dock lists")
        viewDockAction.setStatusTip("Show/Hide the dock lists")

        self.windows["Mapper"] = QSignalMapper(self)
        self.connect(self.windows["Mapper"], SIGNAL("mapped(QWidget*)"),
                     self.mdi, SLOT("setActiveWindow(QWidget*)"))

        helpAboutAction = self.createAction("&About Component Designer",
                self.helpAbout, tip = "About Component Designer")



        fileMenu = self.menuBar().addMenu("&File")    
        self.addActions(fileMenu, (                 
                componentNewAction, 
                dsourceNewAction,
                componentOpenAction, 
                dsourceOpenAction, 
                componentEditAction, 
                dsourceEditAction, 
                None, 
                componentSaveAction, 
                dsourceSaveAction,
                componentSaveAsAction,
                dsourceSaveAsAction,
                componentSaveAllAction, 
                dsourceSaveAllAction,
                None,
                componentMergeAction,
                None, 
                componentClearAction,
                componentRemoveAction,
                dsourceRemoveAction,
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
                None,
                componentRemoveItemAction, 
                componentCopyItemAction,
                componentPasteItemAction, 
                None,
                componentApplyItemAction,
                None,
                dsourceCutAction,
                dsourceCopyAction,
                dsourcePasteAction,
                None,
                dsourceApplyAction
                ))

        componentsMenu = self.menuBar().addMenu("C&omponents")    
        self.addActions(componentsMenu, ( 
                componentNewGroupAction, componentNewFieldAction, 
                componentNewAttributeAction, componentNewLinkAction,
                componentNewDataSourceAction,None, 
                componentLoadComponentAction, componentLoadDataSourceAction,
                None,
                componentAddDataSourceAction
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
        


        serverMenu = self.menuBar().addMenu("&Server") 
        self.addActions(serverMenu, (
                serverConnectAction,None,
                serverFetchComponentsAction,
                serverStoreComponentAction,
                serverDeleteComponentAction,
                None,
                serverFetchDataSourcesAction,
                serverStoreDataSourceAction,
                serverDeleteDataSourceAction,
                None,
                serverGetMandatoryComponentsAction,
                serverSetMandatoryComponentAction,
                serverUnsetMandatoryComponentAction,
                None,
                serverCloseAction
                ))


        viewMenu = self.menuBar().addMenu("&View")
        self.addActions(viewMenu, (viewDockAction,))

        self.windows["Menu"] = self.menuBar().addMenu("&Window")
        self.connect(self.windows["Menu"], SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)

        self.menuBar().addSeparator()

        helpMenu = self.menuBar().addMenu("&Help") 
        self.addActions(helpMenu, (helpAboutAction, ))
        

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolbar")

        self.addActions(fileToolbar, (
                componentNewAction,
                componentOpenAction, 
                componentEditAction, 
                componentSaveAction,
                componentSaveAsAction,
                componentMergeAction,
                componentRemoveAction, 
                None,
                cutItemAction, copyItemAction, pasteItemAction,
                None,
                undoAction, redoAction,
                None, 
                dsourceNewAction,
                dsourceOpenAction,
                dsourceEditAction,
                dsourceSaveAction,
                dsourceRemoveAction,
                None, 
                serverConnectAction,
                serverCloseAction
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

        if self.configServer:
            settings.setValue("ConfigServer/device",
                              QVariant(self.configServer.device))
            settings.setValue("ConfigServer/host",
                              QVariant(self.configServer.host))
            settings.setValue("ConfigServer/port",
                              QVariant(self.configServer.port))
        files = QStringList()
#        for widget in self.mdi.windowList():
#            if not widget.filename.startsWith("Unnamed"):
#                files.append(widget.filename)
#        settings.setValue("CurrentFiles", QVariant(files))
        self.mdi.closeAllWindows()


    def loadDataSources(self):
        self.sourceList.loadList(self.dsourceCollect, self.dsourceApply)
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)


    def setDataSources(self, datasources):
        self.sourceList.setList(datasources, self.dsourceCollect, self.dsourceApply)
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)
        


    def setComponents(self, components):
        self.componentList.setList(components, self.contextMenuActions,
                                    self.componentCollect,
                                    self.componentApplyItem
                                    )
        idc =  self.componentList.components.itervalues().next().id \
            if len(self.componentList.components) else None

        self.componentList.populateComponents(idc)



    def loadComponents(self):
#        self.componentList.components = {}
        self.componentList.loadList(self.contextMenuActions,
                                    self.componentCollect,
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


    def componentCollect(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('componentCollect').clone()
        cmd.execute()

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



    def dsourceCollect(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceCollect').clone()
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


    def dsourceCopy(self):
        cmd = self.pool.getCommand('dsourceCopy').clone()
        cmd.execute()



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
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None
        cmd.execute()



    def cutItem(self):
        cmd = self.pool.getCommand('cutItem').clone()
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd.type = "component"
        elif isinstance(self.mdi.activeWindow(),DataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
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
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
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
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            
    

    def componentNewFieldItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewFieldItem').clone()
            cmd.itemName = 'field' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            


    def componentNewAttributeItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewAttributeItem').clone()
            cmd.itemName = 'attribute' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            
            

    def componentNewLinkItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewLinkItem').clone()
            cmd.itemName = 'link' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



    def componentNewDataSourceItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewDataSourceItem').clone()
            cmd.itemName = 'datasource' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



    def componentLoadComponentItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentLoadComponentItem').clone()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



    def componentLoadDataSourceItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentLoadDataSourceItem').clone()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            




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


    def serverConnect(self):
        cmd = self.pool.getCommand('serverConnect').clone()
        cmd.execute()
        self.cmdStack.append(cmd)

#        self.pool.setDisabled("serverConnect", True)
        self.pool.setDisabled("serverFetchComponents", False)
        self.pool.setDisabled("serverStoreComponent", False)
        self.pool.setDisabled("serverDeleteComponent", False)
        self.pool.setDisabled("serverGetMandatoryComponents", False)
        self.pool.setDisabled("serverSetMandatoryComponent", False)
        self.pool.setDisabled("serverUnsetMandatoryComponent", False)
        self.pool.setDisabled("serverFetchDataSources", False)
        self.pool.setDisabled("serverStoreDataSource", False)
        self.pool.setDisabled("serverDeleteDataSource", False)
        self.pool.setDisabled("serverClose", False)

        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def serverFetchComponents(self):
        cmd = self.pool.getCommand('serverFetchComponents').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def serverStoreComponent(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('serverStoreComponent').clone()
        cmd.execute()

    def serverDeleteComponent(self):
        cmd = self.pool.getCommand('serverDeleteComponent').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def serverSetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverSetMandatoryComponent').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def serverGetMandatoryComponents(self):
        cmd = self.pool.getCommand('serverGetMandatoryComponents').clone()
        cmd.execute()

    def serverUnsetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverUnsetMandatoryComponent').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      

    def serverFetchDataSources(self):
        cmd = self.pool.getCommand('serverFetchDataSources').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    def serverStoreDataSource(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('serverStoreDataSource').clone()
        cmd.execute()



    def serverDeleteDataSource(self):
        cmd = self.pool.getCommand('serverDeleteDataSource').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    def serverClose(self):
        cmd = self.pool.getCommand('serverClose').clone()
        cmd.execute()
        self.cmdStack.append(cmd)

        self.pool.setDisabled("serverConnect", False)
        self.pool.setDisabled("serverFetchComponents", True)
        self.pool.setDisabled("serverStoreComponent", True)
        self.pool.setDisabled("serverDeleteComponent", True)
        self.pool.setDisabled("serverGetMandatoryComponents", True)
        self.pool.setDisabled("serverSetMandatoryComponent", True)
        self.pool.setDisabled("serverUnsetMandatoryComponent", True)
        self.pool.setDisabled("serverFetchDataSources", True)
        self.pool.setDisabled("serverStoreDataSource", True)
        self.pool.setDisabled("serverDeleteDataSource", True)
        self.pool.setDisabled("serverClose", True)

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
        self.windows["Menu"].clear()
        self.addActions(self.windows["Menu"], (self.windows["NextAction"],
                                               self.windows["PrevAction"], self.windows["CascadeAction"],
                                               self.windows["TileAction"], self.windows["RestoreAction"],
                                               self.windows["MinimizeAction"],
                                               self.windows["ArrangeIconsAction"], None,
                                               self.windows["CloseAction"]))
        dialogs = self.mdi.windowList()
        if not dialogs:
            return
        self.windows["Menu"].addSeparator()
        i = 1
        menu = self.windows["Menu"]
        for dialog in dialogs:
            title = dialog.windowTitle()
            if i == 10:
                self.windows["Menu"].addSeparator()
                menu = menu.addMenu("&More")
            accel = ""
            if i < 10:
                accel = "&%s " % str(i)
            elif i < 36:
                accel = "&%s " % str(chr(i + ord("@") - 9))
            action = menu.addAction("%s%s" % (accel, title))
            self.connect(action, SIGNAL("triggered()"),
                         self.windows["Mapper"], SLOT("map()"))
            self.windows["Mapper"].setMapping(action, dialog)
            i += 1



