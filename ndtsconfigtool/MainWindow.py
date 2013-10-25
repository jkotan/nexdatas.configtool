#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

""" main window application dialog """

import os
import platform

from PyQt4.QtCore import (
    SIGNAL, SLOT, QSettings, Qt,  QSignalMapper, 
    QVariant, QT_VERSION_STR, PYQT_VERSION_STR)
from PyQt4.QtGui import (
    QMainWindow, QDockWidget, QSplitter, QMdiArea,
    QAction, QKeySequence, QMessageBox, QIcon, 
    QLabel, QFrame)

from .qrc import qrc_resources

from .CommandPool import (CommandPool, CommandStack)
from .DataSourceList import DataSourceList
from .ComponentList import ComponentList
from .DataSourceDlg import CommonDataSourceDlg
from .ComponentDlg import ComponentDlg

from .HelpForm import HelpForm

from .ServerCommands import (
    ServerConnect,
    ServerFetchComponents,
    ServerStoreComponent,
    ServerStoreAllComponents,
    ServerDeleteComponent,
    ServerSetMandatoryComponent,
    ServerGetMandatoryComponents,
    ServerUnsetMandatoryComponent,
    ServerFetchDataSources,
    ServerStoreDataSource,
    ServerStoreAllDataSources,
    ServerDeleteDataSource,
    ServerClose)

from .FileCommands import (
    ComponentOpen,
    DataSourceOpen,
    ComponentSave,
    ComponentSaveAll,
    ComponentSaveAs,
    ComponentChangeDirectory,
    DataSourceSaveAll,
    DataSourceSave,
    DataSourceSaveAs,
    ComponentReloadList,
    DataSourceReloadList,
    DataSourceChangeDirectory
    )

from .ListCommands import (
    ComponentNew,
    ComponentRemove,
    ComponentListChanged,
    DataSourceNew,
    DataSourceRemove,
    DataSourceListChanged,
    CloseApplication
    )

from .EditCommands import (
    ComponentEdit,
    DataSourceCopy,
    DataSourceCut,
    DataSourcePaste,
    DataSourceApply,
    DataSourceEdit,
    UndoCommand,
    RedoCommand,
    ComponentTakeDataSources,
    ComponentTakeDataSource
    )

from .ItemCommands import (
    ComponentClear,
    ComponentLoadComponentItem,
    ComponentRemoveItem,
    ComponentCopyItem,
    ComponentPasteItem,
    CutItem,
    CopyItem,
    PasteItem,
    ComponentMerge,
    ComponentNewItem,
    ComponentLoadDataSourceItem,
    ComponentAddDataSourceItem,
    ComponentLinkDataSourceItem,
    ComponentApplyItem,
    ComponentMoveUpItem,
    ComponentMoveDownItem
    )

from .ConfigurationServer import (ConfigurationServer, PYTANGO_AVAILABLE)
from . import __version__

## main window class
class MainWindow(QMainWindow):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)


        ## component tree menu under mouse cursor
        self.contextMenuActions = None


        ## slots for DataSource widget buttons
        self.externalDSActions = {}
        ## datasource list menu under mouse cursor
        self.dsourceListMenuActions = None
        ## datasource directory
        self.dsDirectory = ""
        ## list of datasources
        self.sourceList =  None
        ## datasource directory label
        self.dsDirLabel = None


        ## slots for Component widget buttons
        self.externalCPActions = {}
        ## component list menu under mouse cursor
        self.componentListMenuActions = None
        ## component directory
        self.cpDirectory = ""
        ## list of components
        self.componentList =    None
        ## component directory label
        self.cpDirLabel = None


        ## dock with components and datasources
        self.compDockWidget = None

        ## receiver main application
        self.main = self
        
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

        self.dsDirectory = self.setDirectory(
            settings, "DataSources/directory", "datasources")    
        self.cpDirectory = self.setDirectory(
            settings, "Components/directory", "components")    


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
            self.setupServer(settings)

        status = self.createStatusBar()        
        self.updateWindowMenu()
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")



    ## setups direcconfiguration server
    # \param settings application QSettings object
    # \param name setting variable name
    # \param default defualt value    
    # \returns set directory    
    @classmethod    
    def setDirectory(cls, settings, name, default):
        directory = ""
        dsdir = unicode(settings.value(name).toString())
        if dsdir:
            directory = os.path.abspath(dsdir)
        else:
            if os.path.exists(os.path.join(os.getcwd(), default)):
                directory = os.path.abspath(
                    os.path.join(os.getcwd(), default))
            else:
                directory = os.getcwd()
        return directory        
            


    ## setups configuration server
    # \param settings application QSettings object
    def setupServer(self, settings):
        self.configServer = ConfigurationServer()
        self.configServer.device = unicode(
            settings.value("ConfigServer/device").toString())
        self.configServer.host = unicode(
            settings.value("ConfigServer/host").toString())
        port = str(settings.value("ConfigServer/port").toString())
        if port:
            self.configServer.port = int(port)


    ## updates directories in status bar
    def updateStatusBar(self):
        self.cpDirLabel.setText("CP: %s" % (self.cpDirectory))
        self.dsDirLabel.setText("DS: %s" % (self.dsDirectory))

    ## creates status bar    
    # \returns status bar    
    def createStatusBar(self):    
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        self.cpDirLabel = QLabel("CP: %s" % (self.cpDirectory))
        self.cpDirLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.dsDirLabel = QLabel("DS: %s" % (self.dsDirectory))
        self.dsDirLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        status.addWidget(QLabel(""), 4)
        status.addWidget(self.cpDirLabel, 4)
        status.addWidget(self.dsDirLabel, 4)
        return status

    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.compDockWidget = QDockWidget(self)
        self.compDockWidget.setWindowTitle("Collections")
#        self.compDockWidget = QDockWidget("",self)
        self.compDockWidget.setObjectName("CompDockWidget")
        self.compDockWidget.setAllowedAreas(
            Qt.LeftDockWidgetArea |  Qt.RightDockWidgetArea)

        self.sourceList = DataSourceList(self.dsDirectory, self)
        self.sourceList.createGUI()

        self.componentList = ComponentList(self.cpDirectory, self)
        self.componentList.createGUI()

        dockSplitter = QSplitter(Qt.Vertical)
        dockSplitter.addWidget(self.componentList)
        dockSplitter.addWidget(self.sourceList)
        dockSplitter.setStretchFactor(0, 2)
        dockSplitter.setStretchFactor(1, 1)
        self.compDockWidget.setWidget(dockSplitter)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.compDockWidget)

        self.mdi = QMdiArea()


        self.mdi.setOption(QMdiArea.DontMaximizeSubWindowOnActivation)
        self.mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded ) 
        self.mdi.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded ) 

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
            DataSourceNew,"Ctrl+Shift+N", "dsourceadd", 
            "Create a new data source") 

        dsourceRemoveAction = self.pool.createCommand(
            "&Remove DataSource", "dsourceRemove",  commandArgs, 
            DataSourceRemove,"Ctrl+Shift+P", "dsourceremove", 
            "Close the data source")

        dsourceEditAction =  self.pool.createCommand(
            "&Edit DataSource", "dsourceEdit",  commandArgs, 
            DataSourceEdit,
            "Ctrl+Shift+E", 
            "dsourceedit", "Edit the data source")

       
        self.pool.createTask(
            "dsourceChanged", commandArgs, DataSourceListChanged,
            self.sourceList.ui.elementListWidget, 
            "itemChanged(QListWidgetItem*)")
        
        self.pool.createTask(
            "componentChanged", commandArgs, ComponentListChanged,
            self.componentList.ui.elementListWidget, 
            "itemChanged(QListWidgetItem*)")


        self.connect(
            self.mdi, SIGNAL("subWindowActivated(QMdiSubWindow*)"), 
            self.mdiWindowActivated)


#        self.connect(self.sourceList.ui.elementListWidget, 
#                     SIGNAL("itemClicked(QListWidgetItem*)"), 
#                     self.dsourceEdit)

#        self.connect(self.componentList.ui.elementListWidget, 
#                     SIGNAL("itemClicked(QListWidgetItem*)"), 
#                     self.componentEdit)


        self.connect(self.componentList.ui.elementListWidget, 
                     SIGNAL("itemDoubleClicked(QListWidgetItem*)"), 
                     self.componentEdit)


        self.connect(self.sourceList.ui.elementListWidget, 
                     SIGNAL("itemDoubleClicked(QListWidgetItem*)"), 
                     self.dsourceEdit)


        

        componentNewAction = self.pool.createCommand(
            "&New", "componentNew", commandArgs, ComponentNew,
            QKeySequence.New, "componentnew", "Create a new component")

        componentEditAction = self.pool.createCommand(
            "&Edit Component", "componentEdit", commandArgs, ComponentEdit,
            "Ctrl+E", "componentedit", "Edit the component")

        componentClearAction = self.pool.createCommand(
            "Clear Component Items", "componentClear", commandArgs, 
            ComponentClear,
            "", "componentclear", "Removes all component items")


        componentSaveAsAction = self.pool.createCommand(
            "Save &As...", "componentSaveAs", commandArgs, 
            ComponentSaveAs,
            "", "componentsaveas", "Write the component into a file as ...")



        componentSaveAction = self.pool.createCommand(
            "&Save", "componentSave", commandArgs, ComponentSave,
            QKeySequence.Save, "componentsave", 
            "Write the component into a file")


        componentSaveAllAction = self.pool.createCommand(
            "Save All", "componentSaveAll", commandArgs, ComponentSaveAll,
            "", "componentsaveall", "Write all components into files")

        componentApplyItemAction = self.pool.createCommand(
            "&Apply Component Item", "componentApplyItem", commandArgs, 
            ComponentApplyItem,
            "Ctrl+R", "componentsapplyitem", "Apply the component item")

        componentMoveUpItemAction = self.pool.createCommand(
            "&Move Up Component Item", "componentMoveUpItem", commandArgs, 
            ComponentMoveUpItem,
            "Ctrl+[", "componentsmoveupitem", "Move up the component item")


        componentMoveDownItemAction = self.pool.createCommand(
            "&Move Down Component Item", "componentMoveDownItem", commandArgs, 
            ComponentMoveDownItem,
            "Ctrl+]", "componentsmovedownitem", "Move down the component item")


        dsourceApplyAction = self.pool.createCommand(
            "Apply DataSource", "dsourceApply", commandArgs, DataSourceApply,
            "Ctrl+Shift+R", "dsourceapply", "Apply the data source")


        dsourceSaveAction = self.pool.createCommand(
            "&Save DataSource", "dsourceSave", commandArgs, DataSourceSave,
            "Ctrl+Shift+S", "dsourcesave", "Write the data source into a file")



        dsourceSaveAsAction = self.pool.createCommand(
            "Save DataSource &As...", "dsourceSaveAs", commandArgs, 
            DataSourceSaveAs,
            "", "dsourcesaveas", 
            "Write the data source  in a file as ...")

        dsourceSaveAllAction = self.pool.createCommand(
            "Save All DataSources", "dsourceSaveAll", commandArgs, 
            DataSourceSaveAll,
            "", "dsourcessaveall", "Write all data sources in files")


        dsourceCopyAction = self.pool.createCommand(
            "Copy DataSource", "dsourceCopy", 
            commandArgs, DataSourceCopy,
            "", "copy", "Copy the data source")


        dsourceCutAction = self.pool.createCommand(
            "Cut DataSource", "dsourceCut", 
            commandArgs, DataSourceCut,
            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Delete),
#            "", 
            "cut", "Cut the data source")


        dsourcePasteAction = self.pool.createCommand(
            "Paste DataSource", "dsourcePaste", 
            commandArgs, DataSourcePaste,
            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Insert),
#            "", 
            "paste", "Paste the data source")
        

        componentRemoveItemAction = self.pool.createCommand(
            "Cut Component Item", "componentRemoveItem", commandArgs, 
            ComponentRemoveItem,
#            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_X),
#            "Ctrl+X",
            QKeySequence(Qt.CTRL + Qt.Key_Delete),
            "cut", "Remove the component item")


        componentCopyItemAction = self.pool.createCommand(
            "Copy Component Item", "componentCopyItem", commandArgs, 
            ComponentCopyItem,
#            QKeySequence(Qt.CTRL + Qt.SHIFT  + Qt.Key_C),
#            "Ctrl+C", 
            "" ,
            "copy", "Copy the component item")


        componentPasteItemAction = self.pool.createCommand(
            "Paste Component Item", "componentPasteItem", commandArgs, 
            ComponentPasteItem,
#            QKeySequence(Qt.CTRL +  Qt.SHIFT  + Qt.Key_V),
#            "Ctrl+V", 
            QKeySequence(Qt.CTRL + Qt.Key_Insert),
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
            "New &Group Item", "componentNewGroupItem", commandArgs, 
            ComponentNewItem,
            "", "componentnewitem", "Add a new component group item")

        componentNewStrategyAction = self.pool.createCommand(
            "New &Strategy Item", "componentNewStrategyItem", commandArgs, 
            ComponentNewItem,
            "", "componentnewitem", "Add a new component strategy item")


        componentNewFieldAction = self.pool.createCommand(
            "New &Field Item", "componentNewFieldItem", commandArgs, 
            ComponentNewItem,
            "", "componentnewitem", "Add a new  component field item")

        componentNewAttributeAction = self.pool.createCommand(
            "New A&ttribute Item", "componentNewAttributeItem", commandArgs, 
            ComponentNewItem,
            "", "componentnewitem", "Add a new component attribute item")

        componentNewLinkAction = self.pool.createCommand(
            "New &Link Item", "componentNewLinkItem", commandArgs, 
            ComponentNewItem,
            "", "componentnewitem", "Add a new  component link item")
        

        componentNewDataSourceAction = self.pool.createCommand(
            "New &DataSource Item", "componentNewDataSourceItem", commandArgs,
            ComponentNewItem,
            "", "componentnewitem", "Add a new component data source item")


        componentLoadComponentAction = self.pool.createCommand(
            "Load SubComponent Item...", "componentLoadComponentItem", 
            commandArgs, ComponentLoadComponentItem,
            "", "componentloaditem", 
            "Load an existing component part from the file")


        componentLoadDataSourceAction = self.pool.createCommand(
            "Load DataSource Item...", "componentLoadDataSourceItem", 
            commandArgs, ComponentLoadDataSourceItem,
            "", "componentloaditem", 
            "Load an existing data source from the file")


        componentAddDataSourceAction = self.pool.createCommand(
            "Add DataSource Item", "componentAddDataSourceItem", 
            commandArgs, ComponentAddDataSourceItem,
            QKeySequence(Qt.CTRL +  Qt.Key_Plus),
            "componentadditem", "Add the data source from the list")


        componentLinkDataSourceAction = self.pool.createCommand(
            "Link DataSource Item", "componentLinkDataSourceItem", 
            commandArgs, ComponentLinkDataSourceItem,
            "Ctrl+L",
            "componentlinkitem", "Link the data source from the list")


        componentTakeDataSourceAction = self.pool.createCommand(
            "Take DataSource Item " , "componentTakeDataSource", 
            commandArgs, ComponentTakeDataSource,
            "Ctrl+G",
            "componenttakedatasource", 
            "Take the currnet data sources from the component")




        componentTakeDataSourcesAction = self.pool.createCommand(
            "Take DataSources " , "componentTakeDataSources", 
            commandArgs, ComponentTakeDataSources,
            "",
            "componenttakedatasource", 
            "Take data sources from the component")


        componentMergeAction = self.pool.createCommand(
            "Merge Component Items", "componentMerge", commandArgs, 
            ComponentMerge,
            "Ctrl+M", "componentmerge", "Merge the component items")
        

        componentChangeDirectoryAction = self.pool.createCommand(
            "Change Directory...", "componentChangeDirectory", commandArgs, 
            ComponentChangeDirectory,
            "", "componentrechangedirectory", 
            "Change the component list directory")



        dsourceChangeDirectoryAction = self.pool.createCommand(
            "Change DataSource Directory...", "dsourceChangeDirectory", 
            commandArgs, DataSourceChangeDirectory,
            "", "dsourcerechangedirectory", 
            "Change the data-source list directory")


        
        componentReloadListAction = self.pool.createCommand(
            "Reload List", "componentReloadList", 
            commandArgs, ComponentReloadList,
            "", "componentreloadlist", "Reload the component list")


        dsourceReloadListAction = self.pool.createCommand(
            "Reload DataSource List", "dsourceReloadList", 
            commandArgs, DataSourceReloadList,
            "", "dsourcereloadlist", "Reload the data-source list")

        dsourceOpenAction = self.pool.createCommand(
            "&Load DataSource...", "dsourceOpen", commandArgs, DataSourceOpen,
            "Ctrl+Shift+O", "dsourceopen", "Load an existing data source")


        componentOpenAction = self.pool.createCommand(
            "&Load...", "componentOpen", commandArgs, ComponentOpen,
            QKeySequence.Open, "componentopen", "Load an existing component")
        
        componentRemoveAction = self.pool.createCommand(
            "&Remove", "componentRemove", commandArgs, ComponentRemove,
            "Ctrl+P", "componentremove", "Close the component")





        serverConnectAction = self.pool.createCommand(
            "&Connect ...", "serverConnect", commandArgs, ServerConnect,
            "Ctrl+T", "serverconnect", 
            "Connect to the configuration server")

        serverFetchComponentsAction = self.pool.createCommand(
            "&Fetch Components", "serverFetchComponents", 
            commandArgs, ServerFetchComponents,
            "Ctrl+F", "serverfetchdatasources", 
            "Fetch datasources from the configuration server")

        serverFetchDataSourcesAction = self.pool.createCommand(
            "&Fetch DataSources", "serverFetchDataSources", 
            commandArgs, ServerFetchDataSources,
            "Ctrl+Shift+F", "serverfetchdatasources", 
            "Fetch datasources from the configuration server")

        serverStoreComponentAction = self.pool.createCommand(
            "&Store Component", "serverStoreComponent", 
            commandArgs, ServerStoreComponent,
            "Ctrl+B", "serverstorecomponent", 
            "Store component in the configuration server")

        serverStoreAllComponentsAction = self.pool.createCommand(
            "&Store All Components", "serverStoreAllComponents", 
            commandArgs, ServerStoreAllComponents,
            "", "serverstoreallcomponents", 
            "Store all components in the configuration server")

        serverStoreDataSourceAction = self.pool.createCommand(
            "&Store Datasource", "serverStoreDataSource", 
            commandArgs, ServerStoreDataSource,
            "Ctrl+Shift+B", "serverstoredatasource", 
            "Store datasource in the configuration server")

        serverStoreAllDataSourcesAction = self.pool.createCommand(
            "&Store All Datasources", "serverStoreAllDataSources", 
            commandArgs, ServerStoreAllDataSources,
            "", "serverstorealldatasources", 
            "Store all datasources in the configuration server")

        serverDeleteComponentAction = self.pool.createCommand(
            "&Delete Component", "serverDeleteComponent", commandArgs, 
            ServerDeleteComponent,
            "", "serverdeletedatasource", 
            "Delete datalsource from the configuration server")

        serverDeleteDataSourceAction = self.pool.createCommand(
            "&Delete Datasource", "serverDeleteDataSource", 
            commandArgs, ServerDeleteDataSource,
            "", "serverdeletedatasource", 
            "Delete datasource from the configuration server")

        serverSetMandatoryComponentAction = self.pool.createCommand(
            "Set Component Mandatory", "serverSetMandatoryComponent", 
            commandArgs, ServerSetMandatoryComponent,
            "", "serversetmandatory", 
            "Set the component as mandatory  on the configuration server")

        serverGetMandatoryComponentsAction = self.pool.createCommand(
            "Get Mandatory Components", "serverGetMandatoryComponents", 
            commandArgs, ServerGetMandatoryComponents,
            "", "servergetmandatory", 
            "Get mandatory components  from the configuration server")

        serverUnsetMandatoryComponentAction = self.pool.createCommand(
            "Unset Component Mandatory", "serverUnsetMandatoryComponent", 
            commandArgs, ServerUnsetMandatoryComponent,
            "", "serverunsetmandatory", 
            "Unset the component as mandatory on the configuration server")

        serverCloseAction = self.pool.createCommand(
            "C&lose", "serverClose", commandArgs, ServerClose,
            "Ctrl+L", "serverclose", 
            "Close connection to the configuration server")

        
        if not PYTANGO_AVAILABLE:
            serverConnectAction.setDisabled(True)

        serverFetchComponentsAction.setDisabled(True)
        serverStoreComponentAction.setDisabled(True)
        serverStoreAllComponentsAction.setDisabled(True)
        serverDeleteComponentAction.setDisabled(True)
        serverGetMandatoryComponentsAction.setDisabled(True)
        serverSetMandatoryComponentAction.setDisabled(True)
        serverUnsetMandatoryComponentAction.setDisabled(True)
        serverFetchDataSourcesAction.setDisabled(True)
        serverStoreDataSourceAction.setDisabled(True)
        serverStoreAllDataSourcesAction.setDisabled(True)
        serverDeleteDataSourceAction.setDisabled(True)
        serverCloseAction.setDisabled(True)



        fileQuitAction = self.pool.createCommand(
            "&Quit", "closeApp", commandArgs, CloseApplication, 
            "Ctrl+Q", "filequit", "Close the application")

        undoAction = self.pool.createCommand(
            "&Undo", "undo",  commandArgs, UndoCommand, 
            "Ctrl+Z", "undo", "Can't Undo")
        redoAction = self.pool.createCommand(
            "&Redo", "redo",  commandArgs, RedoCommand,
            "Ctrl+Y", "redo", "Can't Redo")

        undoAction.setDisabled(True)
        redoAction.setDisabled(True)



        self.windows["NextAction"] = self._createAction(
            "&Next", self.mdi.activateNextSubWindow, 
            QKeySequence.NextChild, tip = "Go to the next window")
        self.windows["PrevAction"] = self._createAction(
            "&Previous", self.mdi.activatePreviousSubWindow,
            QKeySequence.PreviousChild, tip = "Go to the previous window")
        self.windows["CascadeAction"] = self._createAction(
            "Casca&de", self.mdi.cascadeSubWindows , 
            tip = "Cascade the windows")
        self.windows["TileAction"] = self._createAction(
            "&Tile", self.mdi.tileSubWindows, tip = "Tile the windows")
        self.windows["RestoreAction"] = self._createAction(
            "&Restore All", self.windowRestoreAll, 
            tip = "Restore the windows")
        self.windows["CloseAllAction"] = self._createAction(
            "&Close All", self.mdi.closeAllSubWindows, 
            tip = "Close the windows")
        self.windows["MinimizeAction"] = self._createAction(
            "&Iconize All", self.windowMinimizeAll, 
            tip = "Minimize the windows")
        self.windows["CloseAction"] = self._createAction(
            "&Close", self.mdi.closeActiveSubWindow, 
            QKeySequence(Qt.Key_Escape),
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
                     self.mdi, SLOT("setActiveWindow(QMdiSubWindow*)"))

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
                componentEditAction, 
                componentTakeDataSourceAction,
                componentTakeDataSourcesAction,
                None,
                dsourceEditAction, 
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
                componentLinkDataSourceAction,
                None,
                componentMoveUpItemAction,
                componentMoveDownItemAction,
                None,
                componentMergeAction,
                componentApplyItemAction,
                None,
                componentClearAction
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
            componentLoadComponentAction, 
            componentLoadDataSourceAction,
            None,
            componentAddDataSourceAction,
            componentLinkDataSourceAction,
            None,
            componentRemoveItemAction, 
            componentCopyItemAction,
            componentPasteItemAction,
            componentTakeDataSourceAction,
            None,
            componentMoveUpItemAction,
            componentMoveDownItemAction,
            None,
            componentApplyItemAction,
            componentMergeAction,
            None,
            componentClearAction
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
            serverStoreAllComponentsAction,
            serverDeleteComponentAction,
            serverGetMandatoryComponentsAction,
            serverSetMandatoryComponentAction,
            serverUnsetMandatoryComponentAction,
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
            serverStoreAllDataSourcesAction,
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
                serverStoreAllComponentsAction,
                serverDeleteComponentAction,
                None,
                serverFetchDataSourcesAction,
                serverStoreDataSourceAction,
                serverStoreAllDataSourcesAction,
                serverDeleteDataSourceAction,
                None,
                serverGetMandatoryComponentsAction,
                serverSetMandatoryComponentAction,
                serverUnsetMandatoryComponentAction,
                None,
                serverCloseAction
                ))


        viewMenu = self.menuBar().addMenu("&View")
        self._addActions(viewMenu, 
                         (viewDockAction, viewAllAttributesAction))

        self.windows["Menu"] = self.menuBar().addMenu("&Window")
        self.connect(self.windows["Menu"], SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)

        self.menuBar().addSeparator()

        helpMenu = self.menuBar().addMenu("&Help") 
        self._addActions(helpMenu, (helpHelpAction, helpAboutAction ))
        

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
        

        self.externalDSActions = {
            "externalSave":self.dsourceSaveButton, 
            "externalApply":self.dsourceApplyButton, 
            "externalClose":self.dsourceClose, 
            "externalStore":self.serverStoreDataSourceButton}    


        self.externalCPActions = {
            "externalSave":self.componentSaveButton,
            "externalStore":self.serverStoreComponentButton,
            "externalApply":self.componentApplyItemButton,
            "externalClose":self.componentClose,
            "externalDSLink":self.componentLinkDataSourceItemButton}

    

    ## stores the setting before finishing the application 
    # \param event Qt event   
    def closeEvent(self, event):
        failures = []
        status = None
        for k in self.componentList.elements.keys():
            cp = self.componentList.elements[k]
            if (hasattr(cp,"isDirty") and cp.isDirty()) or \
                    (hasattr(cp,"instance") \
                         and hasattr(cp.instance,"isDirty") \
                         and cp.instance.isDirty()):
                if status != QMessageBox.YesToAll \
                        and status != QMessageBox.NoToAll :
                    status = QMessageBox.question(
                        self, "Component - Save",
                        "Do you want to save the component: %s".encode() \
                            %  (cp.name),
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel \
                            | QMessageBox.YesToAll| QMessageBox.NoToAll,
                        QMessageBox.Yes)
                    
                if status == QMessageBox.Yes or status == QMessageBox.YesToAll:
                    try:
                        cid = self.componentList.currentListElement()
                        self.componentList.populateElements(cp.id)
                        self.componentEdit()
                        cp.instance.merge()
                        if not cp.instance.save():
                            self.componentList.populateElements(cid)
                            event.ignore()
                            return
                        self.componentList.populateElements(cid)
                        
                    except IOError, e:
                        failures.append(unicode(e))
                        
                elif status == QMessageBox.Cancel:
                    event.ignore()
                    return


        status = None
        for k in self.sourceList.elements.keys():
            ds = self.sourceList.elements[k]
            if (hasattr(ds,"isDirty") and ds.isDirty()) or \
                    (hasattr(ds,"instance") \
                         and hasattr(ds.instance,"isDirty") \
                         and ds.instance.isDirty()):
                if status != QMessageBox.YesToAll \
                        and status != QMessageBox.NoToAll:
                    status = QMessageBox.question(
                        self, "DataSource - Save",
                        "Do you want to save the datasource: %s".encode() \
                            %  (ds.name),
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel \
                            | QMessageBox.YesToAll |  QMessageBox.NoToAll,
                        QMessageBox.Yes)
                
                if status == QMessageBox.Yes or status == QMessageBox.YesToAll:
                    try:
                        sid = self.sourceList.currentListElement()
                        self.sourceList.populateElements(ds.id)
                        self.dsourceEdit()
                        if not ds.instance.save():
                            self.sourceList.populateElements(sid)
                            event.ignore()
                            return
                        self.sourceList.populateElements(sid)



                    except IOError, e:
                        failures.append(unicode(e))
                        
                elif status == QMessageBox.Cancel:
                    event.ignore()
                    return


        if (failures and
            QMessageBox.warning(
                self, "NDTS Component Designer -- Save Error",
                "Failed to save%s\nQuit anyway?"  \
                    % unicode("\n\t".join(failures)),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
            event.ignore()
            return
        settings = QSettings()
        settings.setValue("MainWindow/Geometry",
                          QVariant(self.saveGeometry()))
        settings.setValue("MainWindow/State",
                          QVariant(self.saveState()))
        settings.setValue("DataSources/directory",
                          QVariant(os.path.abspath(self.dsDirectory)))
        settings.setValue("Components/directory",
                          QVariant(os.path.abspath(self.cpDirectory)))

        if self.configServer:
            settings.setValue("ConfigServer/device",
                              QVariant(self.configServer.device))
            settings.setValue("ConfigServer/host",
                              QVariant(self.configServer.host))
            settings.setValue("ConfigServer/port",
                              QVariant(self.configServer.port))
            self.configServer.close()

        self.mdi.closeAllSubWindows()



    ## disables/enable the server actions
    # \param status True for disable
    def disableServer(self, status):
        self.pool.setDisabled("serverFetchComponents", status)
        self.pool.setDisabled("serverStoreComponent", status)
        self.pool.setDisabled("serverStoreAllComponents", status)
        self.pool.setDisabled("serverDeleteComponent", status)
        self.pool.setDisabled("serverGetMandatoryComponents", status)
        self.pool.setDisabled("serverSetMandatoryComponent", status)
        self.pool.setDisabled("serverUnsetMandatoryComponent", status)
        self.pool.setDisabled("serverFetchDataSources", status)
        self.pool.setDisabled("serverStoreDataSource", status)
        self.pool.setDisabled("serverStoreAllDataSources", status)
        self.pool.setDisabled("serverDeleteDataSource", status)
        self.pool.setDisabled("serverClose", status)
        

        if self.configServer and self.configServer.device:
            dev = "%s:%s/%s" % ( 
                self.configServer.host \
                    if self.configServer.host else "localhost", 
                str(self.configServer.port) \
                    if self.configServer.port else "10000",
                self.configServer.device
                )
        else :
            dev = "None"
            
        if status:
            self.setWindowTitle("NDTS Component Designer -||- [%s]" % dev)
        else:
            self.setWindowTitle("NDTS Component Designer <-> [%s]" % dev)
            
            


    ## loads the datasource list
    # \brief It loads the datasource list from the default directory
    def loadDataSources(self):
        self.sourceList.loadList(self.externalDSActions)
        ide =  self.sourceList.elements.itervalues().next().id \
            if len(self.sourceList.elements) else None

        self.sourceList.populateElements(ide)


    ## sets the datasource list from dictionary
    # \param datasources dictionary with datasources, i.e. name:xml
    # \param new logical variable set to True if objects are not saved    
    def setDataSources(self, datasources, new = False):
        last = self.sourceList.setList(
            datasources, 
            self.externalDSActions, 
            None, 
            new)
        ide =  self.sourceList.elements.itervalues().next().id \
            if len(self.sourceList.elements) else None

        self.sourceList.populateElements(ide)
        return last
        
    

    ## sets the component list from the given dictionary
    # \param components dictionary with components, i.e. name:xml
    def setComponents(self, components):
        self.componentList.setList(
            components, 
            self.externalCPActions, 
            self.contextMenuActions
           )
        ide =  self.componentList.elements.itervalues().next().id \
            if len(self.componentList.elements) else None

        self.componentList.populateElements(ide)



    ## loads the component list
    # \brief It loads the component list from the default directory
    def loadComponents(self):
#        self.componentList.elements = {}
        print "COMPONENT"
        self.componentList.loadList(
            self.externalCPActions, 
            self.contextMenuActions
            )
        ide =  self.componentList.elements.itervalues().next().id \
            if len(self.componentList.elements) else None

        self.componentList.populateElements(ide)
        

    ## adds actions to target
    # \param target action target
    # \param actions actions to be added   
    @classmethod    
    def _addActions(cls, target, actions):
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
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")   



    ## remove datasource action
    # \brief It removes the current datasource      
    def dsourceRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
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
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## save component action
    # \brief It saves the current component      
    def componentSave(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('componentSave').clone()
        cmd.execute()


    ## save component action executed by button
    # \brief It saves the current component executed by button   
    def componentSaveButton(self):
        if self.updateComponentListItem():
            self.componentSave()


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
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## apply component item action executed by button
    # \brief It applies the changes in the current component item 
    #        executed by button
    def componentApplyItemButton(self):
        if self.updateComponentListItem():
            self.componentApplyItem()

    ## move-up component item action
    # \brief It moves the current component item up
    def componentMoveUpItem(self):
        cmd = self.pool.getCommand('componentMoveUpItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## move-down component item action
    # \brief It moves the current component item down
    def componentMoveDownItem(self):
        cmd = self.pool.getCommand('componentMoveDownItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## reload datasource list
    # \brief It changes the default datasource directory and reload datasources
    def dsourceReloadList(self):
        cmd = self.pool.getCommand('dsourceReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## update datasource list item according to open window
    # \returns True if windows is open
    def updateDataSourceListItem(self):
        status = False
        if self.mdi.activeSubWindow() \
                and isinstance(self.mdi.activeSubWindow().widget(),
                               CommonDataSourceDlg):
            widget  = self.mdi.activeSubWindow().widget()
            self.pooling = False
            if isinstance(widget, CommonDataSourceDlg):
                if widget.datasource.id is not None:
                    if hasattr(self.sourceList.currentListElement(), "id"):
                        if self.sourceList.currentListElement().id \
                                != widget.datasource.id: 
                            self.sourceList.populateElements(
                                widget.datasource.id)
                    status = True        
            self.pooling = True
        return status        



    ## apply datasource item action executed by button
    # \brief It applies the changes in the current datasource item  
    #        executed by button
    def dsourceApplyButton(self):
        if self.updateDataSourceListItem():
            self.dsourceApply()


    ## apply datasource item action
    # \brief It applies the changes in the current datasource item 
    def dsourceApply(self):
        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## save datasource item action
    # \brief It saves the changes in the current datasource item 
    def dsourceSave(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceSave').clone()
        cmd.execute()


    ## save datasource item action executed by button
    # \brief It saves the changes in the current datasource item executed 
    #        by button
    def dsourceSaveButton(self):
        if self.updateDataSourceListItem():
            self.dsourceSave()





    ## save datasource item as action
    # \brief It saves the changes in the current datasource item with 
    #        a new name
    def dsourceSaveAs(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmdSA = self.pool.getCommand('dsourceSaveAs').clone()
        cmdSA.execute()

        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.directory = cmdSA.directory
        cmd.name = cmdSA.name
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
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
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmdSA = self.pool.getCommand('componentSaveAs').clone()
        cmdSA.execute()

        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.directory = cmdSA.directory
        cmd.name = cmdSA.name
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
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
    # \brief It removes the current component item and copies it 
    #        into the clipboard
    def componentRemoveItem(self):
        cmd = self.pool.getCommand('componentRemoveItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## paste component item action
    # \brief It pastes the component item from the clipboard
    def componentPasteItem(self):
        cmd = self.pool.getCommand('componentPasteItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
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
    # \brief It removes the current datasources item and copies it 
    #        into the clipboard
    def dsourceCut(self):
        cmd = self.pool.getCommand('dsourceCut').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## paste datasource item action
    # \brief It pastes the datasource item from the clipboard
    def dsourcePaste(self):
        cmd = self.pool.getCommand('dsourcePaste').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## copy item action
    # \brief It copies the current item into the clipboard
    def copyItem(self):
        cmd = self.pool.getCommand('copyItem').clone()
        if self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None
            return
        cmd.execute()



    ## cuts item action
    # \brief It removes the current item and copies it into the clipboard
    def cutItem(self):
        cmd = self.pool.getCommand('cutItem').clone()
        if self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None

            return
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## paste item action
    # \brief It pastes the item from the clipboard
    def pasteItem(self):
        cmd = self.pool.getCommand('pasteItem').clone()
        if self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None
            return
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## new group component item action
    # \brief It adds a new group component item
    def componentNewGroupItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewGroupItem').clone()
            cmd.itemName = 'group' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            


    ## new group component item action
    # \brief It adds a new group component item
    def componentNewStrategyItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewStrategyItem').clone()
            cmd.itemName = 'strategy' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            
    

    ## new field component item action
    # \brief It adds a new field component item
    def componentNewFieldItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewFieldItem').clone()
            cmd.itemName = 'field' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            


    ## new attribute component item action
    # \brief It adds a new attribute component item 
    def componentNewAttributeItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewAttributeItem').clone()
            cmd.itemName = 'attribute' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            
            

    ## new link component item action
    # \brief It adds a new link component item
    def componentNewLinkItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewLinkItem').clone()
            cmd.itemName = 'link' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



                

    ## new datasource component item action
    # \brief It adds a new datasource component item
    def componentNewDataSourceItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(),
                      ComponentDlg):
            cmd = self.pool.getCommand('componentNewDataSourceItem').clone()
            cmd.itemName = 'datasource' 
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



    ## load sub-component item action
    # \brief It loads a sub-component item from a file
    def componentLoadComponentItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentLoadComponentItem').clone()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



    ## load datasource component item action
    # \brief It loads a datasource component item from a file
    def componentLoadDataSourceItem(self):
        if isinstance(self.mdi.activeSubWindow().widget(),
                      ComponentDlg):
            cmd = self.pool.getCommand('componentLoadDataSourceItem').clone()
            cmd.execute()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
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
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## take datasources 
    # \brief It takes datasources from the current component
    def componentTakeDataSource(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentTakeDataSource').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
#        cmd = self.pool.getCommand('dsourceEdit').clone()
#        cmd.execute()

#        cmd = self.pool.getCommand('dsourceApply').clone()
#        cmd.execute()
#        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## add datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentAddDataSourceItem(self):
#        cmd = self.pool.getCommand('dsourceEdit').clone()
#        cmd.execute()
        cmd = self.pool.getCommand('componentAddDataSourceItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## link datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentLinkDataSourceItem(self):
        cmd = self.pool.getCommand('componentLinkDataSourceItem').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


        
    ## update component list item according to open window
    # \returns True if windows is open
    def updateComponentListItem(self):
        status = False
        if self.mdi.activeSubWindow() and isinstance(
            self.mdi.activeSubWindow().widget(), ComponentDlg):
            widget  = self.mdi.activeSubWindow().widget()
            self.pooling = False
            if isinstance(widget, ComponentDlg):
                if widget.component.id is not None:

                    if hasattr(self.componentList.currentListElement(),"id"):
                        if self.componentList.currentListElement().id \
                                != widget.component.id:
                            self.componentList.populateElements(
                                widget.component.id)
                    status = True        
            self.pooling = True
        return status        
            

    ## link datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentLinkDataSourceItemButton(self):
        if self.updateComponentListItem():
            self.componentLinkDataSourceItem()




    ## merge component action
    # \brief It merges the current component
    def componentMerge(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## remove component action
    # \brief It removes from the component list the current component
    def componentRemove(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    ## edit datasource action
    # \brief It opens a dialog with the current datasource      
    def dsourceEdit(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()


    ## datasource change action
    # \param item new selected item ond the datasource list
    def dsourceChanged(self, item):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.item = item
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## connect server action
    # \brief It connects to configuration server
    def serverConnect(self):
        cmd = self.pool.getCommand('serverConnect').clone()
        cmd.execute()
        self.cmdStack.append(cmd)

        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## fetch server components action
    # \brief It fetches components from the configuration server
    def serverFetchComponents(self):
        cmd = self.pool.getCommand('serverFetchComponents').clone()
        cmd.execute()

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## store server component action executed by button
    # \brief It stores the current component 
    #        in the configuration server executed by button
    def serverStoreComponentButton(self):
        if self.updateComponentListItem():
            self.serverStoreComponent()


    ## store server component action
    # \brief It stores the current component in the configuration server
    def serverStoreComponent(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('serverStoreComponent').clone()
        cmd.execute()


    ## store server all components action
    # \brief It stores all components in the configuration server
    def serverStoreAllComponents(self):
        cmd = self.pool.getCommand('serverStoreAllComponents').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## delete server component action
    # \brief It deletes the current component from the configuration server
    def serverDeleteComponent(self):
        cmd = self.pool.getCommand('serverDeleteComponent').clone()
        cmd.execute()


    ## set component mandatory action
    # \brief It sets the current component as mandatory
    def serverSetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverSetMandatoryComponent').clone()
        cmd.execute()


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

    ## fetch server datasources action
    # \brief It fetches datasources from the configuration server
    def serverFetchDataSources(self):
        cmd = self.pool.getCommand('serverFetchDataSources').clone()
        cmd.execute()

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
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('serverStoreDataSource').clone()
        cmd.execute()



    ## store server datasource action executed by button
    # \brief It stores the current datasource in 
    #        the configuration server executed by button
    def serverStoreDataSourceButton(self):
        if self.updateDataSourceListItem():
            self.serverStoreDataSource()

    ## store server all datasources action
    # \brief It stores all components in the configuration server
    def serverStoreAllDataSources(self):
        cmd = self.pool.getCommand('serverStoreAllDataSources').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## delete server datasource action
    # \brief It deletes the current datasource from the configuration server
    def serverDeleteDataSource(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('serverDeleteDataSource').clone()
        cmd.execute()


    ## close server action
    # \brief It closes the configuration server
    def serverClose(self):
        cmd = self.pool.getCommand('serverClose').clone()
        cmd.execute()
        self.cmdStack.append(cmd)


        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## activated window action, i.e. it changes the current position 
    #  of the component and datasource lists 
    # \param subwindow selected subwindow
    def mdiWindowActivated(self, subwindow):
        widget = subwindow.widget() if hasattr(subwindow, "widget") else None
        self.pooling = False
        if isinstance(widget, CommonDataSourceDlg):
            if widget.datasource.id is not None:
                if hasattr(self.sourceList.currentListElement(),"id"):
                    if self.sourceList.currentListElement().id \
                            != widget.datasource.id: 
                        self.sourceList.populateElements(
                            widget.datasource.id)
        elif isinstance(widget, ComponentDlg):
            if widget.component.id is not None:
                if hasattr(self.componentList.currentListElement(),"id"):
                    if self.componentList.currentListElement().id \
                            != widget.component.id:
                        self.componentList.populateElements(
                            widget.component.id)
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
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## new component action
    # \brief It creates a new component
    def componentNew(self):
        cmd = self.pool.getCommand('componentNew').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## open component action
    # \brief It opens component from the file
    def componentOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('componentOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        self.pooling = True


    ## open datasource action
    # \brief It opens datasource from the file
    def dsourceOpen(self):
        self.pooling = False
        cmd = self.pool.getCommand('dsourceOpen').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
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
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )   
        self.pool.setDisabled("redo", False, "Redo: ", 
                              self.cmdStack.getRedoName() )   

        self.pooling = True

    ## redo action
    # \brief It reexecutes the last undexecuted command
    def redo(self):
        self.pooling = False
        cmd = self.pool.getCommand('redo').clone()
        cmd.execute()

        rucmd = self.cmdStack.redo()
        if hasattr(rucmd,'reexecute'):
            rucmd.reexecute()
        else:
            print "Redo not possible"

        if self.cmdStack.isFinal():
            self.pool.setDisabled("redo", True, "Can't Redo")   
        else:
            self.pool.setDisabled("redo", False, "Redo: ", 
                                  self.cmdStack.getRedoName() )    
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )   
        self.pooling = True

    ## close application action
    # \brief It closes the main application
    def closeApp(self):
        cmd = self.pool.getCommand('closeApp').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
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
        self.componentList.ui.elementListWidget.setFocus()

  
  ## restores all windows
    # \brief It restores all windows in MDI
    def gotoDataSourceList(self):
        self.sourceList.ui.elementListWidget.setFocus()


    ## restores all windows
    # \brief It restores all windows in MDI
    def windowRestoreAll(self):
        for dialog in self.mdi.subWindowList():
            dialog.showNormal()


    ## minimizes all windows
    # \brief It minimizes all windows in MDI
    def windowMinimizeAll(self):
        for dialog in self.mdi.subWindowList():
            dialog.showMinimized()


    ## shows help about
    # \brief It shows message box with help about
    def helpAbout(self):
        QMessageBox.about(self, "About Component Designer",
                """<b>Component Designer</b> v %s
                <p>Copyright &copy; 2012-2013 DESY, GNU GENERAL PUBLIC LICENSE
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
        self.componentList.viewAttributes(
            not self.componentList.viewAttributes())
        
    ## provides subwindow defined by instance
    # \param instance given instance
    # \param subwindows list of subwindows
    # \returns required subwindow
    @classmethod    
    def subWindow(cls, instance, subwindows):
        swin = None
        for sw in subwindows:
            if hasattr(sw,"widget"):
                if hasattr(sw.widget(),"component")\
                        and  sw.widget().component == instance:
                    swin = sw
                    break
                elif hasattr(sw.widget(),"datasource")\
                        and  sw.widget().datasource == instance:
                    swin = sw
                    break
        return swin


    ## provides subwindow defined by widget
    # \param widget given widget
    # \param subwindows list of subwindows
    # \returns required subwindow
    @classmethod    
    def widgetSubWindow(cls, widget, subwindows):
        swin = None
        for sw in subwindows:
            if hasattr(sw,"widget") and sw.widget() == widget:
                swin = sw
                break
        return swin
        

    ## closes the current window
    # \brief Is closes the current datasource window
    def dsourceClose(self):
        print "datasource close"
        subwindow = self.mdi.activeSubWindow()
        if subwindow and isinstance(subwindow.widget(), CommonDataSourceDlg) \
                and subwindow.widget().datasource:
            
            ds = subwindow.widget().datasource

            ds.updateForm()
            if ds.dialog:
                ds.dialog.reject()

            self.mdi.setActiveSubWindow(subwindow)
            self.mdi.closeActiveSubWindow()


    ## closes the current window
    # \brief Is closes the current component window
    def componentClose(self):
        print "component close"
        subwindow = self.mdi.activeSubWindow()
        if subwindow and isinstance(subwindow.widget(), ComponentDlg) \
                and subwindow.widget().component:
            cp = subwindow.widget().component

            if cp.dialog:
                cp.dialog.reject()


            self.mdi.setActiveSubWindow(subwindow)
            self.mdi.closeActiveSubWindow()
        
    ## updates the window menu
    # \brief It updates the window menu with the open windows
    def updateWindowMenu(self):
        self.windows["Menu"].clear()
        self._addActions(self.windows["Menu"], 
                         (self.windows["NextAction"],
                          self.windows["PrevAction"], 
                          self.windows["CascadeAction"],
                          self.windows["TileAction"], 
                          self.windows["RestoreAction"],
                          self.windows["MinimizeAction"],
                          None,
                          self.windows["CloseAction"],
                          self.windows["CloseAllAction"],
                          None,
                          self.windows["ComponentListAction"], 
                          self.windows["DataSourceListAction"]
                          ))
        dialogs = self.mdi.subWindowList()
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



