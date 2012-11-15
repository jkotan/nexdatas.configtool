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

from PyQt4.QtCore import (SIGNAL, SLOT, QSettings, Qt,  QSignalMapper, 
                          QVariant, QT_VERSION_STR, PYQT_VERSION_STR, QStringList )
from PyQt4.QtGui import (QMainWindow, QDockWidget, QSplitter, QWorkspace ,
                         QListWidgetItem, QAction, QKeySequence, QMessageBox, QIcon)

import platform

from qrc import qrc_resources

from CommandPool import (CommandPool,CommandStack)
from DataSourceList import DataSourceList
from ComponentList import ComponentList
from DataSourceDlg import DataSourceDlg
from ComponentDlg import ComponentDlg

from HelpForm import HelpForm

from Command import (
     ServerConnect,
     ServerFetchComponents,
     ServerStoreComponent,
     ServerDeleteComponent,
     ServerSetMandatoryComponent,
     ServerGetMandatoryComponents,
     ServerUnsetMandatoryComponent,
     ServerFetchDataSources,
     ServerStoreDataSource,
     ServerDeleteDataSource,
     ServerClose,
     ComponentNew,
     ComponentOpen,
     DataSourceOpen,
     ComponentRemove,
     ComponentEdit,
     ComponentSave,
     ComponentSaveAll,
     ComponentSaveAs,
     ComponentChangeDirectory,
     DataSourceCopy,
     DataSourceCut,
     DataSourcePaste,
     DataSourceApply,
     DataSourceSaveAll,
     DataSourceSave,
     DataSourceSaveAs,
     DataSourceChangeDirectory,
     ComponentReloadList,
     DataSourceReloadList,
     ComponentListChanged,
     DataSourceNew,
     DataSourceEdit,
     DataSourceRemove,
     DataSourceListChanged,
     CloseApplication,
     UndoCommand,
     RedoCommand,
     ComponentItemCommand,
     ComponentClear,
     ComponentLoadComponentItem,
     ComponentRemoveItem,
     ComponentCopyItem,
     ComponentPasteItem,
     CutItem,
     CopyItem,
     PasteItem,
     ComponentCollect,
     DataSourceCollect,
     ComponentMerge,
     ComponentNewItem,
     ComponentLoadDataSourceItem,
     ComponentAddDataSourceItem,
     ComponentTakeDataSources,
     ComponentApplyItem,
     ComponentMoveUpItem,
     ComponentMoveDownItem
     )

from ConfigurationServer import (ConfigurationServer, PYTANGO_AVAILABLE)
from ndtsconfigtool import __version__

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

        ## component tree menu under mouse cursor
        self.contextMenuActions = None

        ## component list menu under mouse cursor
        self.componentListMenuActions = None

        ## datasource list menu under mouse cursor
        self.dsourceListMenuActions = None

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

        ## dictionary with window actions
        self.windows = {}

        settings = QSettings()
        self.dsDirectory = unicode(settings.value("DataSources/directory").toString())
        self.cpDirectory = unicode(settings.value("Components/directory").toString())

        self.createGUI()

            

        self.createActions()

        if self.componentList:
            self.componentList.setActions(self.componentListMenuActions)

        if self.sourceList:
            self.sourceList.setActions(self.dsourceListMenuActions)

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
            port = str(settings.value("ConfigServer/port").toString())
            if port:
                self.configServer.port = int(port)
            

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        
        self.updateWindowMenu()
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")



    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.compDockWidget = QDockWidget(self)
        self.compDockWidget.setWindowTitle("Collections")
#        self.compDockWidget = QDockWidget("",self)
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



    ## creates actions
    # \brief It creates actions and sets the command pool and stack
    def createActions(self):
        self.pool = CommandPool(self)
        self.cmdStack = CommandStack(30)
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



        self.connect(self.sourceList.sourceListWidget, 
                     SIGNAL("itemClicked(QListWidgetItem*)"), 
                     self.dsourceEdit)

        self.connect(self.componentList.componentListWidget, 
                     SIGNAL("itemClicked(QListWidgetItem*)"), 
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
            QKeySequence.Save, "componentsave", "Write the component into a file")


        componentSaveAllAction = self.pool.createCommand(
            "Save All", "componentSaveAll", commandArgs, ComponentSaveAll,
            "", "componentsaveall", "Write all components into files")

        componentApplyItemAction = self.pool.createCommand(
            "&Apply Component Item", "componentApplyItem", commandArgs, ComponentApplyItem,
            "Ctrl+P", "componentsapplyitem", "Apply the component item")


        componentMoveUpItemAction = self.pool.createCommand(
            "&Move Up Component Item", "componentMoveUpItem", commandArgs, ComponentMoveUpItem,
            "Ctrl+[", "componentsmoveupitem", "Move up the component item")


        componentMoveDownItemAction = self.pool.createCommand(
            "&Move Down Component Item", "componentMoveDownItem", commandArgs, ComponentMoveDownItem,
            "Ctrl+]", "componentsmovedownitem", "Move down the component item")


        dsourceApplyAction = self.pool.createCommand(
            "Apply DataSource", "dsourceApply", commandArgs, DataSourceApply,
            "Ctrl+Shift+P", "dsourceapply", "Apply the data source")


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
            "", "componentnewitem", "Add a new component group item")

        componentNewStrategyAction = self.pool.createCommand(
            "New &Strategy Item", "componentNewStrategyItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component strategy item")


        componentNewFieldAction = self.pool.createCommand(
            "New &Field Item", "componentNewFieldItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component field item")

        componentNewAttributeAction = self.pool.createCommand(
            "New A&ttribute Item", "componentNewAttributeItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component attribute item")

        componentNewLinkAction = self.pool.createCommand(
            "New &Link Item", "componentNewLinkItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new  component link item")
        

        componentNewDataSourceAction = self.pool.createCommand(
            "New &DataSource Item", "componentNewDataSourceItem", commandArgs, ComponentNewItem,
            "", "componentnewitem", "Add a new component data source item")


        componentLoadComponentAction = self.pool.createCommand(
            "Load SubComponent Item...", "componentLoadComponentItem", commandArgs, ComponentLoadComponentItem,
            "", "componentloaditem", "Load an existing component part from the file")


        componentLoadDataSourceAction = self.pool.createCommand(
            "Load DataSource Item...", "componentLoadDataSourceItem", commandArgs, ComponentLoadDataSourceItem,
            "", "componentloaditem", "Load an existing data source from the file")


        componentAddDataSourceAction = self.pool.createCommand(
            "Add DataSource Item", "componentAddDataSourceItem", 
            commandArgs, ComponentAddDataSourceItem,
            QKeySequence(Qt.CTRL + + Qt.Key_Plus),
            "componentadditem", "Add the data source from the list")


        componentTakeDataSourcesAction = self.pool.createCommand(
            "Take DataSources " , "componentTakeDataSources", 
            commandArgs, ComponentTakeDataSources,
            "",
            "componenttakedatasource", "Take data sources from the component")


        componentMergeAction = self.pool.createCommand(
            "Merge", "componentMerge", commandArgs, ComponentMerge,
            "", "componentmerge", "Merge the component")
        

        componentChangeDirectoryAction = self.pool.createCommand(
            "Change Directory...", "componentChangeDirectory", commandArgs, 
            ComponentChangeDirectory,
            "", "componentrechangedirecotry", "Change the component list directory")



        dsourceChangeDirectoryAction = self.pool.createCommand(
            "Change DataSource Directory...", "dsourceChangeDirectory", commandArgs, 
            DataSourceChangeDirectory,
            "", "dsourcerechangedirecotry", "Change the data-source list directory")


        
        componentReloadListAction = self.pool.createCommand(
            "Reload List", "componentReloadList", commandArgs, ComponentReloadList,
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
            "&Store Component", "serverStoreComponent", commandArgs, ServerStoreComponent,
            "Ctrl+B", "serverstoredatasource", "Store datasource in the configuration server")

        serverStoreDataSourceAction = self.pool.createCommand(
            "&Store Datasource", "serverStoreDataSource", commandArgs, ServerStoreDataSource,
            "Ctrl+Shift+B", "serverstoredatasource", "Store datasource in the configuration server")

        serverDeleteComponentAction = self.pool.createCommand(
            "&Delete Component", "serverDeleteComponent", commandArgs, ServerDeleteComponent,
            "", "serverdeletedatasource", "Delete datalsource from the configuration server")

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



        self.windows["NextAction"] = self._createAction(
            "&Next", self.mdi.activateNextWindow, 
            QKeySequence.NextChild, tip = "Go to the next window")
        self.windows["PrevAction"] = self._createAction(
            "&Previous", self.mdi.activatePreviousWindow,
            QKeySequence.PreviousChild, tip = "Go to the previous window")
        self.windows["CascadeAction"] = self._createAction(
            "Casca&de", self.mdi.cascade, tip = "Cascade the windows")
        self.windows["TileAction"] = self._createAction(
            "&Tile", self.mdi.tile, tip = "Tile the windows")
        self.windows["RestoreAction"] = self._createAction(
            "&Restore All", self.windowRestoreAll, tip = "Restore the windows")
        self.windows["MinimizeAction"] = self._createAction(
            "&Iconize All", self.windowMinimizeAll, tip = "Minimize the windows")
        self.windows["ArrangeIconsAction"] = self._createAction(
            "&Arrange Icons", self.mdi.arrangeIcons, tip = "Arrange the icons")
        self.windows["CloseAction"] = self._createAction(
            "&Close", self.mdi.closeActiveWindow, QKeySequence.Close,
            tip = "Close the window" )
        self.windows["ComponentListAction"] = self._createAction(
            "&Component List", self.gotoComponentList, "Ctrl+<",
            tip = "Go to the component list" )
        self.windows["DataSourceListAction"] = self._createAction(
            "&DataSource List", self.gotoDataSourceList, "Ctrl+>",
            tip = "Go to the component list" )

        viewAllAttributesAction = self._createAction(
            "&All Attributes", self.viewAllAttributes, "",
            tip = "Go to the component list", checkable=True)





        viewDockAction = self.compDockWidget.toggleViewAction()
        viewDockAction.setToolTip("Show/Hide the dock lists")
        viewDockAction.setStatusTip("Show/Hide the dock lists")

        self.windows["Mapper"] = QSignalMapper(self)
        self.connect(self.windows["Mapper"], SIGNAL("mapped(QWidget*)"),
                     self.mdi, SLOT("setActiveWindow(QWidget*)"))

        helpAboutAction = self._createAction(
            "&About Component Designer",
            self.helpAbout, icon = "icon",tip = "About Component Designer")

        helpHelpAction = self._createAction(
            "Component Desigener &Help", self.helpHelp,
            QKeySequence.HelpContents, icon = "help", tip = "Detail help")

        fileMenu = self.menuBar().addMenu("&File")    
        self._addActions(fileMenu, (                 
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
        self._addActions(editMenu, (
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
                dsourceCutAction,
                dsourceCopyAction,
                dsourcePasteAction,
                None,
                dsourceApplyAction
                ))

        componentsMenu = self.menuBar().addMenu("C&omponent Items")    
        self._addActions(componentsMenu, ( 
                componentNewGroupAction, 
                componentNewFieldAction, 
                componentNewStrategyAction, 
                componentNewDataSourceAction,
                componentNewAttributeAction, 
                componentNewLinkAction,
                None, 
                componentLoadComponentAction, 
                componentLoadDataSourceAction,
                None,
                componentAddDataSourceAction,
                None,
                componentMoveUpItemAction,
                componentMoveDownItemAction,
                None,
                componentApplyItemAction,
                None,
                componentMergeAction,
                None,
                componentTakeDataSourcesAction,
                None,
                componentClearAction,
                ))

        self.mdi.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.contextMenuActions =  ( 
            componentNewGroupAction, 
            componentNewFieldAction,
            componentNewDataSourceAction, 
            componentNewStrategyAction, 
            componentNewAttributeAction, 
            componentNewLinkAction,
            None,
            componentLoadComponentAction, componentLoadDataSourceAction,
            None,
            componentAddDataSourceAction,
            componentRemoveItemAction, 
            componentCopyItemAction,
            componentPasteItemAction,
            None,
            componentMoveUpItemAction,
            componentMoveDownItemAction,
            None,
            componentApplyItemAction,
            None,
            componentMergeAction
            ) 
        

        self.componentListMenuActions =  ( 
            componentNewAction, 
            componentOpenAction, 
            componentEditAction, 
            None, 
            componentSaveAction, 
            componentSaveAsAction,
            componentSaveAllAction, 
            None,
            componentRemoveAction,
            None,
            serverFetchComponentsAction,
            serverStoreComponentAction,
            serverDeleteComponentAction,
            None,
            componentReloadListAction,
            componentChangeDirectoryAction,
            None,
            componentTakeDataSourcesAction
            ) 


        self.dsourceListMenuActions =  ( 
            dsourceNewAction,
            dsourceOpenAction, 
            dsourceEditAction, 
            None, 
            dsourceSaveAction,
            dsourceSaveAsAction,
            dsourceSaveAllAction,
            None,
            dsourceRemoveAction,
            None,
            serverFetchDataSourcesAction,
            serverStoreDataSourceAction,
            serverDeleteDataSourceAction,
            None,
            dsourceReloadListAction,
            dsourceChangeDirectoryAction
            ) 
        


        serverMenu = self.menuBar().addMenu("&Server") 
        self._addActions(serverMenu, (
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
        self._addActions(viewMenu, (viewDockAction, viewAllAttributesAction))

        self.windows["Menu"] = self.menuBar().addMenu("&Window")
        self.connect(self.windows["Menu"], SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)

        self.menuBar().addSeparator()

        helpMenu = self.menuBar().addMenu("&Help") 
        self._addActions(helpMenu, (helpHelpAction,helpAboutAction ))
        

        componentToolbar = self.addToolBar("Component")
        componentToolbar.setObjectName("ComponentToolbar")

        self._addActions(componentToolbar, (
                componentNewAction,
                componentOpenAction, 
                componentEditAction, 
                componentSaveAction,
                componentSaveAsAction,
                componentMergeAction,
                componentRemoveAction
                ))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")
        self._addActions(editToolbar, (
                cutItemAction, copyItemAction, pasteItemAction,
                None,
                undoAction, redoAction,
                ))


        dsourceToolbar = self.addToolBar("DataSource")
        dsourceToolbar.setObjectName("DataSourceToolbar")
        self._addActions(dsourceToolbar, (
                dsourceNewAction,
                dsourceOpenAction,
                dsourceEditAction,
                dsourceSaveAction,
                dsourceRemoveAction
                ))


        serverToolbar = self.addToolBar("ServerToolbar")
        serverToolbar.setObjectName("ServerToolbar")
        self._addActions(serverToolbar, (
                serverConnectAction,
                serverCloseAction
                ))

        helpToolbar = self.addToolBar("HelpToolbar")
        helpToolbar.setObjectName("HelpToolbar")
        self._addActions(helpToolbar, (
                helpHelpAction,
                ))
        

    ## stores the setting before finishing the application 
    # \param event Qt event   
    def closeEvent(self, event):
        failures = []
        for k in self.componentList.components.keys():
            cp = self.componentList.components[k]
            que = False
            if (hasattr(cp,"isDirty") and cp.isDirty()) or \
                    (hasattr(cp,"widget") and hasattr(cp.widget,"isDirty") and cp.widget.isDirty()):
                status= QMessageBox.question(self, "Component - Save",
                                             "Do you want to save the component: %s".encode() \
                                                 %  (cp.name),
                                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                             QMessageBox.Save)

                if status == QMessageBox.Yes:
                    try:
                        cp.widget.merge()
                        if not cp.widget.save():
                            event.ignore()
                            return
                            
                    except IOError, e:
                        failures.append(unicode(e))
                        
                elif status == QMessageBox.Cancel:
                    event.ignore()
                    return


        for k in self.sourceList.datasources.keys():
            ds = self.sourceList.datasources[k]
            que = False
            if (hasattr(ds,"isDirty") and ds.isDirty()) or \
                    (hasattr(ds,"widget") and hasattr(ds.widget,"isDirty") and ds.widget.isDirty()):
                status= QMessageBox.question(self, "DataSource - Save",
                                             "Do you want to save the datasource: %s".encode() \
                                                 %  (ds.name),
                                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                             QMessageBox.Save)

                if status == QMessageBox.Yes:
                    try:
                        if not ds.widget.save():
                            event.ignore()
                            return
                            
                    except IOError, e:
                        failures.append(unicode(e))
                        
                elif status == QMessageBox.Cancel:
                    event.ignore()
                    return


        if (failures and
            QMessageBox.warning(self, "NDTS Component Designer -- Save Error",
                                "Failed to save%s\nQuit anyway?"  % unicode("\n\t".join(failures)),
                                QMessageBox.Yes|QMessageBox.No) ==
            QMessageBox.No):
            event.ignore()
            return
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
            self.configServer.close()

#        files = QStringList()
#        for widget in self.mdi.windowList():
#            if not widget.filename.startsWith("Unnamed"):
#                files.append(widget.filename)
#        settings.setValue("CurrentFiles", QVariant(files))
        self.mdi.closeAllWindows()


    ## disables/enable the server actions
    # \param status True for disable
    def disableServer(self, status):
        self.pool.setDisabled("serverFetchComponents", status)
        self.pool.setDisabled("serverStoreComponent", status)
        self.pool.setDisabled("serverDeleteComponent", status)
        self.pool.setDisabled("serverGetMandatoryComponents", status)
        self.pool.setDisabled("serverSetMandatoryComponent", status)
        self.pool.setDisabled("serverUnsetMandatoryComponent", status)
        self.pool.setDisabled("serverFetchDataSources", status)
        self.pool.setDisabled("serverStoreDataSource", status)
        self.pool.setDisabled("serverDeleteDataSource", status)
        self.pool.setDisabled("serverClose", status)
        



    ## loads the datasource list
    # \brief It loads the datasource list from the default directory
    def loadDataSources(self):
        self.sourceList.loadList(self.dsourceCollect, self.dsourceApply)
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)


    ## sets the datasource list from dictionary
    # \param datasources dictionary with datasources, i.e. name:xml
    def setDataSources(self, datasources):
        self.sourceList.setList(datasources, self.dsourceCollect, self.dsourceApply)
        ids =  self.sourceList.datasources.itervalues().next().id \
            if len(self.sourceList.datasources) else None

        self.sourceList.populateDataSources(ids)
        


    ## sets the component list from the given dictionary
    # \param components dictionary with components, i.e. name:xml
    def setComponents(self, components):
        self.componentList.setList(
            components, 
            self.contextMenuActions,
            self.componentCollect,
            self.componentApplyItem
            )
        idc =  self.componentList.components.itervalues().next().id \
            if len(self.componentList.components) else None

        self.componentList.populateComponents(idc)



    ## loads the component list
    # \brief It loads the component list from the default directory
    def loadComponents(self):
#        self.componentList.components = {}
        self.componentList.loadList(
            self.contextMenuActions,
            self.componentCollect,
            self.componentApplyItem
            )
        idc =  self.componentList.components.itervalues().next().id \
            if len(self.componentList.components) else None

        self.componentList.populateComponents(idc)
        

    ## adds actions to target
    # \param target action target
    # \param actions actions to be added   
    def _addActions(self, target, actions):
        if not  hasattr(actions, '__iter__'):
            target.addAction(actions)
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    ## new datasource action
    # \brief It creates a new datasource      
    def dsourceNew(self):
        cmd = self.pool.getCommand('dsourceNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")   



    ## remove datasource action
    # \brief It removes the current datasource      
    def dsourceRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    ## edit component action
    # \brief It opens a dialog with the current component
    def componentEdit(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()

    ## clear component action
    # \brief It clears the current component      
    def componentClear(self):
        cmd = self.pool.getCommand('componentClear').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## save component action
    # \brief It saves the current component      
    def componentSave(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('componentSave').clone()
        cmd.execute()


    ## collect component action
    # \brief It stores in the configuration server or saves in the file the current component      
    def componentCollect(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('componentCollect').clone()
        cmd.execute()


    ## change component directory action
    # \brief It changes the default component directory
    def componentChangeDirectory(self):
        cmd = self.pool.getCommand('componentChangeDirectory').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## change datasource directory action
    # \brief It changes the default datasource directory
    def dsourceChangeDirectory(self):
        cmd = self.pool.getCommand('dsourceChangeDirectory').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## reload component list
    # \brief It changes the default component directory and reload components
    def componentReloadList(self):
        cmd = self.pool.getCommand('componentReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## apply component item action
    # \brief It applies the changes in the current component item 
    def componentApplyItem(self):
        cmd = self.pool.getCommand('componentApplyItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## move-up component item action
    # \brief It moves the current component item up
    def componentMoveUpItem(self):
        cmd = self.pool.getCommand('componentMoveUpItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## move-down component item action
    # \brief It moves the current component item down
    def componentMoveDownItem(self):
        cmd = self.pool.getCommand('componentMoveDownItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## reload datasource list
    # \brief It changes the default datasource directory and reload datasources
    def dsourceReloadList(self):
        cmd = self.pool.getCommand('dsourceReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## apply datasource item action
    # \brief It applies the changes in the current datasource item 
    def dsourceApply(self):
        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## save datasource item action
    # \brief It saves the changes in the current datasource item 
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



    ## collect datasource item action
    # \brief It collects the changes in the current datasource item  either in the configuration server or in the file
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


    ## save datasource item as action
    # \brief It saves the changes in the current datasource item with a new name
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
        cmd.name = cmdSA.name
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceSave').clone()
        cmd.execute()


    ## save all datasource item action
    # \brief It saves the changes in all datasources item
    def dsourceSaveAll(self):
        cmd = self.pool.getCommand('dsourceSaveAll').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## save component item as action
    # \brief It saves the changes in the current component item with a new name
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
        cmd.name = cmdSA.name
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


        cmd = self.pool.getCommand('componentSave').clone()
        cmd.execute()



    ## save all components item action
    # \brief It saves the changes in all components item
    def componentSaveAll(self):
        cmd = self.pool.getCommand('componentSaveAll').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## remove component item action
    # \brief It removes the current component item and copies it into the clipboard
    def componentRemoveItem(self):
        cmd = self.pool.getCommand('componentRemoveItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## paste component item action
    # \brief It pastes the component item from the clipboard
    def componentPasteItem(self):
        cmd = self.pool.getCommand('componentPasteItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        
    ## copy component item action
    # \brief It copies the  current component item into the clipboard
    def componentCopyItem(self):
        cmd = self.pool.getCommand('componentCopyItem').clone()
        cmd.execute()


    ## copy datasource item action
    # \brief It copies the  current datasource item into the clipboard
    def dsourceCopy(self):
        cmd = self.pool.getCommand('dsourceCopy').clone()
        cmd.execute()



    ## cuts datasource item action
    # \brief It removes the current datasources item and copies it into the clipboard
    def dsourceCut(self):
        cmd = self.pool.getCommand('dsourceCut').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## paste datasource item action
    # \brief It pastes the datasource item from the clipboard
    def dsourcePaste(self):
        cmd = self.pool.getCommand('dsourcePaste').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## copy item action
    # \brief It copies the current item into the clipboard
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



    ## cuts item action
    # \brief It removes the current item and copies it into the clipboard
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



    ## paste item action
    # \brief It pastes the item from the clipboard
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



    ## new group component item action
    # \brief It adds a new group component item
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


    ## new group component item action
    # \brief It adds a new group component item
    def componentNewStrategyItem(self):
        if isinstance(self.mdi.activeWindow(),ComponentDlg):
            cmd = self.pool.getCommand('componentNewStrategyItem').clone()
            cmd.itemName = 'strategy' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            
    

    ## new field component item action
    # \brief It adds a new field component item
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


    ## new attribute component item action
    # \brief It adds a new attribute component item 
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
            

    ## new link component item action
    # \brief It adds a new link component item
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



    ## new datasource component item action
    # \brief It adds a new datasource component item
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



    ## load sub-component item action
    # \brief It loads a sub-component item from a file
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



    ## load datasource component item action
    # \brief It loads a datasource component item from a file
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




    ## take datasources 
    # \brief It takes datasources from the current component
    def componentTakeDataSources(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentTakeDataSources').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## add datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentAddDataSourceItem(self):
        cmd = self.pool.getCommand('componentAddDataSourceItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## merge component action
    # \brief It merges the current component
    def componentMerge(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## remove component action
    # \brief It removes from the component list the current component
    def componentRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    ## edit datasource action
    # \brief It opens a dialog with the current datasource      
    def dsourceEdit(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## datasource change action
    # \param item new selected item ond the datasource list
    def dsourceChanged(self, item):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## connect server action
    # \brief It connects to configuration server
    def serverConnect(self):
        cmd = self.pool.getCommand('serverConnect').clone()
        cmd.execute()
        self.cmdStack.append(cmd)

#        self.pool.setDisabled("serverConnect", True)

        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## fetch server components action
    # \brief It fetches components from the configuration server
    def serverFetchComponents(self):
        cmd = self.pool.getCommand('serverFetchComponents').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## store server component action
    # \brief It stores the current component in the configuration server
    def serverStoreComponent(self):
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('serverStoreComponent').clone()
        cmd.execute()

    ## delete server component action
    # \brief It deletes the current component from the configuration server
    def serverDeleteComponent(self):
        cmd = self.pool.getCommand('serverDeleteComponent').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## set component mandatory action
    # \brief It sets the current component as mandatory
    def serverSetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverSetMandatoryComponent').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## get mandatory components action
    # \brief It fetches mandatory components
    def serverGetMandatoryComponents(self):
        cmd = self.pool.getCommand('serverGetMandatoryComponents').clone()
        cmd.execute()


    ## unset component mandatory action
    # \brief It unsets the current component as mandatory
    def serverUnsetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverUnsetMandatoryComponent').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## fetch server datasources action
    # \brief It fetches datasources from the configuration server
    def serverFetchDataSources(self):
        cmd = self.pool.getCommand('serverFetchDataSources').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## store server datasource action
    # \brief It stores the current datasource in the configuration server
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



    ## delete server datasource action
    # \brief It deletes the current datasource from the configuration server
    def serverDeleteDataSource(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('serverDeleteDataSource').clone()
        cmd.execute()
#        self.cmdStack.append(cmd)
#        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
#        self.pool.setDisabled("redo", True, "Can't Redo")      

#        self.cmdStack.clear()
#        self.pool.setDisabled("undo", True, "Can't Undo")   
#        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## close server action
    # \brief It closes the configuration server
    def serverClose(self):
        cmd = self.pool.getCommand('serverClose').clone()
        cmd.execute()
        self.cmdStack.append(cmd)


        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## activated window action, i.e. it changes the current position of the component and datasource lists 
    # \param widget selected widget window
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


    ## component change action
    # \param item new selected item on the component list
    def componentChanged(self, item): 
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## new component action
    # \brief It creates a new component
    def componentNew(self):
        cmd = self.pool.getCommand('componentNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## open component action
    # \brief It opens component from the file
    def componentOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    ## open datasource action
    # \brief It opens datasource from the file
    def dsourceOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('dsourceOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    ## undo action
    # \brief It unexecutes the last command
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

    ## redo action
    # \brief It reexecutes the last undexecuted command
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

    ## close application action
    # \brief It closes the main application
    def closeApp(self):
        cmd = self.pool.getCommand('closeApp').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## creates action
    # \param text string shown in menu
    # \param slot action slot 
    # \param shortcut key short-cut
    # \param icon qrc_resource icon name
    # \param tip text for status bar and text hint
    # \param checkable if command/action checkable
    # \param signal action signal   
    # \returns the action instance
    def _createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png"% unicode(icon).strip()))
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



    ## restores all windows
    # \brief It restores all windows in MDI
    def gotoComponentList(self):
        self.componentList.componentListWidget.setFocus()

  
  ## restores all windows
    # \brief It restores all windows in MDI
    def gotoDataSourceList(self):
        self.sourceList.sourceListWidget.setFocus()


    ## restores all windows
    # \brief It restores all windows in MDI
    def windowRestoreAll(self):
        for dialog in self.mdi.windowList():
            dialog.showNormal()


    ## minimizes all windows
    # \brief It minimizes all windows in MDI
    def windowMinimizeAll(self):
        for dialog in self.mdi.windowList():
            dialog.showMinimized()


    ## shows help about
    # \brief It shows message box with help about
    def helpAbout(self):
        QMessageBox.about(self, "About Component Designer",
                """<b>Component Designer</b> v %s
                <p>Copyright &copy; 2012 GNU GENERAL PUBLIC LICENSE
                <p>This application can be used to create
                XML configuration file for the Nexus Data Writer.
                <p>Python %s - Qt %s - PyQt %s on %s""" % (
                unicode(__version__), 
                unicode(platform.python_version()),
                unicode(QT_VERSION_STR), 
                unicode(PYQT_VERSION_STR),
                unicode(platform.system())))



    ## shows the detail help 
    # \brief It shows the detail help from help directory
    def helpHelp(self):
        form = HelpForm("index.html", self)
        form.show()


    ## shows all attributes in the tree
    # \brief switch between all attributes in the tree or only type attribute
    def viewAllAttributes(self):
        self.componentList.viewAttributes(not self.componentList.viewAttributes())
        
        
    ## updates the window menu
    # \brief It updates the window menu with the open windows
    def updateWindowMenu(self):
        self.windows["Menu"].clear()
        self._addActions(self.windows["Menu"], (self.windows["NextAction"],
                                                self.windows["PrevAction"], 
                                                self.windows["CascadeAction"],
                                                self.windows["TileAction"], 
                                                self.windows["RestoreAction"],
                                                self.windows["MinimizeAction"],
                                                self.windows["ArrangeIconsAction"], 
                                                None,
                                                self.windows["CloseAction"],
                                                None,
                                                self.windows["ComponentListAction"], 
                                                self.windows["DataSourceListAction"]
                                               ))
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
                accel = "&%s " % unicode(i)
            elif i < 36:
                accel = "&%s " % unicode(chr(i + ord("@") - 9))
            action = menu.addAction("%s%s" % (accel, title))
            self.connect(action, SIGNAL("triggered()"),
                         self.windows["Mapper"], SLOT("map()"))
            self.windows["Mapper"].setMapping(action, dialog)
            i += 1



