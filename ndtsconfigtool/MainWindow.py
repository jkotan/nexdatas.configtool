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

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant)
from PyQt4.QtGui import (
    QMainWindow, 
    QMessageBox, QIcon, 
    QLabel, QFrame,
    QUndoGroup, QUndoStack)

from .ui.ui_mainwindow import Ui_MainWindow

from .DataSourceList import DataSourceList
from .ComponentList import ComponentList
from .DataSourceDlg import CommonDataSourceDlg
from .ComponentDlg import ComponentDlg

from .FileSlots import FileSlots
from .ListSlots import ListSlots
from .EditSlots import EditSlots
from .ItemSlots import ItemSlots
from .ServerSlots import ServerSlots
from .HelpSlots import HelpSlots
from .WindowsSlots import WindowsSlots


import logging
logger = logging.getLogger(__name__)


from .ConfigurationServer import (ConfigurationServer, PYTANGO_AVAILABLE)

## main window class
class MainWindow(QMainWindow):

    ## constructor
    # \param parent parent widget
    def __init__(self, components=None, datasources=None, 
                 server=None, parent=None):
        super(MainWindow, self).__init__(parent)
        logger.debug("PARAMETERS: %s %s %s %s", 
                     components, datasources, server, parent)

        ## component tree menu under mouse cursor
        self.contextMenuActions = None

        ## slots for DataSource widget buttons
        self.externalDSActions = {}
        ## datasource list menu under mouse cursor
        self.dsourceListMenuActions = None
        ## list of datasources
        self.sourceList = None
        ## datasource directory label
        self.dsDirLabel = None

        ## slots for Component widget buttons
        self.externalCPActions = {}
        ## component list menu under mouse cursor
        self.componentListMenuActions = None
        ## list of components
        self.componentList = None
        ## component directory label
        self.cpDirLabel = None


        ## stack with used commands
        self.undoStack = None
        ## group of command stacks
        self.undoGroup = None

        ## user interface
        self.ui = Ui_MainWindow()

        ## configuration server
        self.configServer = None
        
        ## action slots
        self.slots = {}

        settings = QSettings()
        dsDirectory = self.__setDirectory(
            settings, "DataSources/directory", "datasources", 
            datasources)    
        cpDirectory = self.__setDirectory(
            settings, "Components/directory", "components", 
            components)    


        self.createGUI(dsDirectory, cpDirectory)            
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
            self.setupServer(settings, server)

        status = self.createStatusBar()        
        status.showMessage("Ready", 5000)

        self.setWindowTitle("NDTS Component Designer")

    ##  creates GUI
    # \brief It create dialogs for the main window application
    # \param dsDirectory datasource directory    
    # \param cpDirectory component directory    
    def createGUI(self, dsDirectory, cpDirectory):
        self.ui.setupUi(self)

        self.sourceList = DataSourceList(dsDirectory, self)
        self.sourceList.createGUI()

        self.componentList = ComponentList(cpDirectory, self)
        self.componentList.createGUI()

        self.ui.dockSplitter.addWidget(self.componentList)
        self.ui.dockSplitter.addWidget(self.sourceList)
        self.ui.dockSplitter.setStretchFactor(0, 2)
        self.ui.dockSplitter.setStretchFactor(1, 1)



    ## setups direcconfiguration server
    # \param settings application QSettings object
    # \param name setting variable name
    # \param default defualt value    
    # \param directory user's directory
    # \returns set directory    
    @classmethod    
    def __setDirectory(cls, settings, name, default, directory = None):
        if directory and os.path.exists(directory):
            return os.path.abspath(directory)
        ldir = ""
        dsdir = unicode(settings.value(name).toString())
        if dsdir:
            ldir = os.path.abspath(dsdir)
        else:
            if os.path.exists(os.path.join(os.getcwd(), default)):
                ldir = os.path.abspath(
                    os.path.join(os.getcwd(), default))
            else:
                ldir = os.getcwd()
        return ldir        
            

    ## setups configuration server
    # \param settings application QSettings object
    # \param server user's server
    def setupServer(self, settings, server = None):
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
        self.cpDirLabel.setText("CP: %s" % (self.componentList.directory))
        self.dsDirLabel.setText("DS: %s" % (self.sourceList.directory))


    ## creates status bar    
    # \returns status bar    
    def createStatusBar(self):    
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        self.cpDirLabel = QLabel("CP: %s" % (self.componentList.directory))
        self.cpDirLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.dsDirLabel = QLabel("DS: %s" % (self.sourceList.directory))
        self.dsDirLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        status.addWidget(QLabel(""), 4)
        status.addWidget(self.cpDirLabel, 4)
        status.addWidget(self.dsDirLabel, 4)
        return status



    ## creates action
    # \param action the action instance
    # \param text string shown in menu
    # \param slot action slot 
    # \param shortcut key short-cut
    # \param icon qrc_resource icon name
    # \param tip text for status bar and text hint
    # \param checkable if command/action checkable
    # \param signal action signal   
    def __setAction(self, action, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
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


    def __setActions(self, slots):
        for ac, pars in slots.actions.items():
            action = getattr(self.ui, ac)
            self.__setAction(
                action, pars[0],
                getattr(slots,pars[1]),
                pars[2],pars[3],pars[4])


    def __setTasks(self, slots):
        if hasattr(slots, "tasks"):
            for pars in slots.tasks:
                self.connect(pars[1], SIGNAL(pars[2]), 
                             getattr(slots, pars[0]))

    def __createUndoRedoActions(self):
        self.undoGroup.addStack(self.undoStack)
        self.undoGroup.setActiveStack(self.undoStack)
        actionUndo = self.undoGroup.createUndoAction(self)
        actionUndo.setIcon(QIcon(":/undo.png"))
        actionRedo = self.undoGroup.createRedoAction(self)
        actionRedo.setIcon(QIcon(":/redo.png"))

        actionUndo.setToolTip("Undo")
        actionUndo.setStatusTip("Undo")
        actionRedo.setToolTip("Redo")
        actionRedo.setStatusTip("Redo")

        self.ui.menuEdit.insertAction(self.ui.menuEdit.actions()[0],
                                      actionUndo)
        self.ui.menuEdit.insertAction(actionUndo, actionRedo)
        self.ui.editToolBar.addAction(actionUndo)
        self.ui.editToolBar.addAction(actionRedo)
           

    ## creates actions
    # \brief It creates actions and sets the command pool and stack
    def createActions(self):
        self.undoGroup = QUndoGroup(self)
        self.undoStack = QUndoStack(self)

        self.__createUndoRedoActions()
        
        self.slots["File"] = FileSlots(self)
        self.slots["List"] = ListSlots(self)
        self.slots["Edit"] = EditSlots(self)
        self.slots["Item"] = ItemSlots(self)
        self.slots["Server"] = ServerSlots(self)
        self.slots["Help"] = HelpSlots(self)
        self.slots["Windows"] = WindowsSlots(self)

        for sl in self.slots.values():
            self.__setActions(sl)
            self.__setTasks(sl)

        self.slots["Windows"].updateWindowMenu()

        if not PYTANGO_AVAILABLE:
            self.ui.actionConnectServer.setDisabled(True)
        self.disableServer(True)


        viewDockAction = self.ui.compDockWidget.toggleViewAction()
        viewDockAction.setToolTip("Show/Hide the dock lists")
        viewDockAction.setStatusTip("Show/Hide the dock lists")

        self.ui.menuView.insertAction(
            self.ui.menuView.actions()[0],
            viewDockAction)

        self.__setAction(
            self.ui.actionAllAttributesView,
            "&All Attributes", self.viewAllAttributes, "",
            tip = "Go to the component list", checkable=True)


        # Signals
        self.connect(self.componentList.ui.elementListWidget, 
                     SIGNAL("itemDoubleClicked(QListWidgetItem*)"), 
                     self.slots["Edit"].componentEdit)

        self.connect(self.sourceList.ui.elementListWidget, 
                     SIGNAL("itemDoubleClicked(QListWidgetItem*)"), 
                     self.slots["Edit"].dsourceEdit)

        ## Component context menu

        self.ui.mdi.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.contextMenuActions =  ( 
            self.ui.actionNewGroupItem, 
            self.ui.actionNewFieldItem,
            self.ui.actionNewDataSourceItem, 
            self.ui.actionNewStrategyItem, 
            self.ui.actionNewAttributeItem, 
            self.ui.actionNewLinkItem,
            None,
            self.ui.actionLoadSubComponentItem, 
            self.ui.actionLoadDataSourceItem,
            None,
            self.ui.actionAddDataSourceItem,
            self.ui.actionLinkDataSourceItem,
            None,
            self.ui.actionCutItem, 
            self.ui.actionCopyItem,
            self.ui.actionPasteItem,
            self.ui.actionTakeDataSourceItem,
            None,
            self.ui.actionMoveUpComponentItem,
            self.ui.actionMoveDownComponentItem,
            None,
            self.ui.actionApplyComponentItem,
            self.ui.actionMergeComponentItems,
            None,
            self.ui.actionClearComponentItems
            ) 
        
        ## Component list menu
        self.componentListMenuActions =  ( 
            self.ui.actionNew, 
            self.ui.actionLoad, 
            self.ui.actionEditComponent, 
            None, 
            self.ui.actionSave, 
            self.ui.actionSaveAs,
            self.ui.actionSaveAll, 
            None,
            self.ui.actionClose,
            None,
            self.ui.actionFetchComponentsServer,
            self.ui.actionStoreComponentServer,
            self.ui.actionStoreAllComponentsServer,
            self.ui.actionDeleteComponentServer,
            self.ui.actionGetMandatoryComponentsServer,
            self.ui.actionSetComponentMandatoryServer,
            self.ui.actionUnsetComponentMandatoryServer,
            None,
            self.ui.actionReloadList,
            self.ui.actionChangeDirectory,
            None,
            self.ui.actionTakeDataSources
            ) 


        ## DataSource list menu
        self.dsourceListMenuActions =  ( 
            self.ui.actionNewDataSource,
            self.ui.actionLoadDataSource, 
            self.ui.actionEditDataSource, 
            None, 
            self.ui.actionSaveDataSource,
            self.ui.actionSaveDataSourceAs,
            self.ui.actionSaveAllDataSources,
            None,
            self.ui.actionCloseDataSource,
            None,
            self.ui.actionFetchDataSourcesServer,
            self.ui.actionStoreDataSourceServer,
            self.ui.actionStoreAllDataSourcesServer,
            self.ui.actionDeleteDataSourceServer,
            None,
            self.ui.actionReloadDataSourceList,
            self.ui.actionChangeDataSourceDirectory
            ) 
        


        # datasource widget actions
        self.externalDSActions = {
            "externalSave":self.slots["File"].dsourceSaveButton, 
            "externalApply":self.slots["Edit"].dsourceApplyButton, 
            "externalClose":self.slots["Windows"].dsourceClose, 
            "externalStore":self.slots["Server"].\
                serverStoreDataSourceButton}    


        # component widget actions
        self.externalCPActions = {
            "externalSave":self.slots["File"].componentSaveButton,
            "externalStore":self.slots["Server"].serverStoreComponentButton,
            "externalApply":self.slots["Item"].componentApplyItemButton,
            "externalClose":self.slots["Windows"].componentClose,
            "externalDSLink":self.slots["Item"].\
                componentLinkDataSourceItemButton}


    ## stores the list element before finishing the application 
    # \param event Qt event   
    # \param elementList element list
    # \param failures a list of errors
    # \returns True if not canceled    
    def __closeList(self, event, elementList, failures):
        status = None
        for k in elementList.elements.keys():
            cp = elementList.elements[k]
            if (hasattr(cp,"isDirty") and cp.isDirty()) or \
                    (hasattr(cp,"instance") \
                         and hasattr(cp.instance,"isDirty") \
                         and cp.instance.isDirty()):
                if status != QMessageBox.YesToAll \
                        and status != QMessageBox.NoToAll :
                    status = QMessageBox.question(
                        self, "%s - Save" % elementList.clName,
                        "Do you want to save %s: %s".encode() \
                            %  (elementList.clName, cp.name),
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel \
                            | QMessageBox.YesToAll| QMessageBox.NoToAll,
                        QMessageBox.Yes)
                    
                if status == QMessageBox.Yes or status == QMessageBox.YesToAll:
                    try:
                        cid = elementList.currentListElement()
                        elementList.populateElements(cp.id)
                        self.componentEdit()
                        cp.instance.merge()
                        if not cp.instance.save():
                            elementList.populateElements(cid)
                            event.ignore()
                            return
                        elementList.populateElements(cid)
                        
                    except IOError, e:
                        failures.append(unicode(e))
                        
                elif status == QMessageBox.Cancel:
                    event.ignore()
                    return
        return True

    ## Stores settings in QSettings object 
    def __storeSettings(self):
        settings = QSettings()
        settings.setValue(
            "MainWindow/Geometry",
            QVariant(self.saveGeometry()))
        settings.setValue(
            "MainWindow/State",
            QVariant(self.saveState()))
        settings.setValue(
            "DataSources/directory",
            QVariant(os.path.abspath(self.sourceList.directory)))
        settings.setValue(
            "Components/directory",
            QVariant(os.path.abspath(self.componentList.directory)))

        if self.configServer:
            settings.setValue("ConfigServer/device",
                              QVariant(self.configServer.device))
            settings.setValue("ConfigServer/host",
                              QVariant(self.configServer.host))
            settings.setValue("ConfigServer/port",
                              QVariant(self.configServer.port))
            self.configServer.close()

        

    ## stores the setting before finishing the application 
    # \param event Qt event   
    def closeEvent(self, event):
        failures = []
        if not self.__closeList(event, self.componentList, failures):
            return
        if not self.__closeList(event, self.sourceList, failures):
            return
        if (failures and
            QMessageBox.warning(
                self, "NDTS Component Designer -- Save Error",
                "Failed to save%s\nQuit anyway?"  \
                    % unicode("\n\t".join(failures)),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.No):
            event.ignore()
            return

        self.__storeSettings()
        self.ui.mdi.closeAllSubWindows()



    ## disables/enable the server actions
    # \param status True for disable
    def disableServer(self, status):
        self.ui.actionFetchComponentsServer.setDisabled(status)
        self.ui.actionStoreComponentServer.setDisabled(status)
        self.ui.actionStoreAllComponentsServer.setDisabled(status)
        self.ui.actionDeleteComponentServer.setDisabled(status)
        self.ui.actionGetMandatoryComponentsServer.setDisabled(status)
        self.ui.actionSetComponentMandatoryServer.setDisabled(status)
        self.ui.actionUnsetComponentMandatoryServer.setDisabled(status)
        self.ui.actionFetchDataSourcesServer.setDisabled(status)
        self.ui.actionStoreDataSourceServer.setDisabled(status)
        self.ui.actionStoreAllDataSourcesServer.setDisabled(status)
        self.ui.actionDeleteDataSourceServer.setDisabled(status)
        self.ui.actionCloseServer.setDisabled(status)
        

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
        self.componentList.loadList(
            self.externalCPActions, 
            self.contextMenuActions
            )
        ide =  self.componentList.elements.itervalues().next().id \
            if len(self.componentList.elements) else None

        self.componentList.populateElements(ide)
        


    ## update datasource list item according to open window
    # \returns True if windows is open
    def updateDataSourceListItem(self):
        status = False
        if self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(),
            CommonDataSourceDlg):
            widget = self.ui.mdi.activeSubWindow().widget()
            if isinstance(widget, CommonDataSourceDlg):
                if widget.datasource.id is not None:
                    if hasattr(self.sourceList.currentListElement(), "id"):
                        if self.sourceList.currentListElement().id \
                                != widget.datasource.id: 
                            self.sourceList.populateElements(
                                widget.datasource.id)
                    status = True        
        return status        


    ## update component list item according to open window
    # \returns True if windows is open
    def updateComponentListItem(self):
        status = False
        if self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            widget  = self.ui.mdi.activeSubWindow().widget()
            if isinstance(widget, ComponentDlg):
                if widget.component.id is not None:

                    if hasattr(self.componentList.currentListElement(),"id"):
                        if self.componentList.currentListElement().id \
                                != widget.component.id:
                            self.componentList.populateElements(
                                widget.component.id)
                    status = True        
        return status        
            


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


