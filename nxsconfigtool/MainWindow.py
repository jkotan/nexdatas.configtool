#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package nxsconfigtool nexdatas
# \file MainWindow.py
# Main window of the application

""" main window application dialog """

import os
import sys

from PyQt5.QtCore import (
    QSettings, Qt, pyqtSlot)
from PyQt5.QtGui import (
    QIcon,
    QTextCursor)
from PyQt5.QtWidgets import (
    QFrame, QUndoGroup, QUndoStack,
    QMainWindow, QMessageBox, QLabel)
from PyQt5 import uic

# from .ui.ui_mainwindow import Ui_MainWindow

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
from .Logger import LogStream, LogActions

from .ConfigurationServer import (ConfigurationServer, PYTANGO_AVAILABLE)
from .ComponentCreator import (NXSTOOLS_AVAILABLE)

import logging

# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "mainwindow.ui"))

if sys.version_info > (3,):
    unicode = str


def iternext(it):
    if sys.version_info > (3,):
        return next(iter(it.values()))
    else:
        return it.itervalues().next()


# main window class
class MainWindow(QMainWindow):

    # constructor
    # \param components component direcotry
    # \param datasources datasource directory
    # \param server configuration server
    # \param parent parent widget
    def __init__(self, components=None, datasources=None,
                 server=None, parent=None):
        super(MainWindow, self).__init__(parent)
        logger.debug("PARAMETERS: %s %s %s %s",
                     components, datasources, server, parent)

        # component tree menu under mouse cursor
        self.contextMenuActions = None

        # slots for DataSource widget buttons
        self.externalDSActions = {}
        # datasource list menu under mouse cursor
        self.dsourceListMenuActions = None
        # list of datasources
        self.sourceList = None
        # datasource directory label
        self.dsDirLabel = None

        # slots for Component widget buttons
        self.externalCPActions = {}
        # component list menu under mouse cursor
        self.componentListMenuActions = None
        # list of components
        self.componentList = None
        # component directory label
        self.cpDirLabel = None

        # stack with used commands
        self.undoStack = None
        # group of command stacks
        self.undoGroup = None

        # user interface
        self.ui = _formclass()

        # configuration server
        self.configServer = None

        # online.xml file name
        self.onlineFile = None

        # action slots
        self.slots = {}

        # log actions
        self.logActions = LogActions(self)

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

        mgeo = settings.value("MainWindow/Geometry")
        if mgeo is not None:
            self.restoreGeometry(mgeo)
        mst = settings.value("MainWindow/State")
        if mst is not None:
            self.restoreState(mst)

        if PYTANGO_AVAILABLE:
            self.setupServer(settings, server)

        status = self.createStatusBar()
        status.showMessage("Ready", 5000)
        self.setWindowTitle("NXS Component Designer")

    def dataSourceContent(self, did):
        if logger.getEffectiveLevel() > 20:
            return
        ds = self.sourceList.elements[did]
        components = []
        datasources = []
        message = ""
        if ds and ds.name:
            if ds and ds.name and ds.instance:
                name = ds.instance.name
                components = self.componentList.dataSourceComponents(name)
                datasources = ds.instance.datasources
            message = "datasource '%s' " % name
            if name != ds.name:
                message += "('%s')" % (ds.name)
            if components:
                message += "\n    is linked to: '%s' components" % \
                           "', '".join([
                               str(el) for el in components])
            if datasources:
                message += "\n    depends on: '%s' datasources" % \
                           "', '".join([
                               str(el) for el in datasources])
        if message:
            logger.info(message)

    def componentContent(self, did):
        if logger.getEffectiveLevel() > 20:
            return
        cp = self.componentList.elements[did]
        components = []
        datasources = []
        message = ""
        if cp and cp.name:
            if cp and cp.name and cp.instance:
                name = cp.instance.name
                components = cp.instance.components
                datasources = cp.instance.datasources
            message = "component '%s' " % name
            if name != cp.name:
                message += "('%s')" % (cp.name)
            if components:
                message += "\n    depends on: '%s' components" % \
                           "', '".join([
                               str(el) for el in components])
            if datasources:
                message += "\n    depends on: '%s' datasources" % \
                           "', '".join([
                               str(el) for el in datasources])
        if message:
            logger.info(message)

    #  creates GUI
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
        self.connectLogger()

    @pyqtSlot(bool)
    def debug(self, flag):
        self.logActions.setlevel("debug", flag)

    @pyqtSlot(bool)
    def info(self, flag):
        self.logActions.setlevel("info", flag)

    @pyqtSlot(bool)
    def warning(self, flag):
        self.logActions.setlevel("warning", flag)

    @pyqtSlot(bool)
    def error(self, flag):
        self.logActions.setlevel("error", flag)

    @pyqtSlot(bool)
    def critical(self, flag):
        self.logActions.setlevel("critical", flag)

    @pyqtSlot(str)
    def insertText(self, message):
        self.ui.logTextBrowser.insertPlainText(message)
        self.ui.logTextBrowser.moveCursor(QTextCursor.End)

    def connectLogger(self):
        self.ui.actionDebug.triggered.connect(self.debug)
        self.ui.actionInfo.triggered.connect(self.info)
        self.ui.actionWarning.triggered.connect(self.warning)
        self.ui.actionError.triggered.connect(self.error)
        self.ui.actionCritical.triggered.connect(self.critical)
        LogStream.stdout().written.connect(self.insertText)
        self.logActions.updatelevel()
        doc = self.ui.logTextBrowser.document()
        doc.setMaximumBlockCount(1000)

    # setups direcconfiguration server
    # \param settings application QSettings object
    # \param name setting variable name
    # \param default defualt value
    # \param directory user's directory
    # \returns set directory
    @classmethod
    def __setDirectory(cls, settings, name, default, directory=None):
        if directory and os.path.exists(directory):
            return os.path.abspath(directory)
        ldir = ""
        dsdir = unicode(settings.value(name))
        if dsdir:
            ldir = os.path.abspath(dsdir)
        else:
            if os.path.exists(os.path.join(os.getcwd(), default)):
                ldir = os.path.abspath(
                    os.path.join(os.getcwd(), default))
            else:
                ldir = os.getcwd()
        return ldir

    # setups configuration server
    # \param settings application QSettings object
    # \param server user's server
    def setupServer(self, settings, server=None):

        self.configServer = ConfigurationServer()
        if server:
            self.configServer.setServer(server)
        else:
            self.configServer.device = unicode(
                settings.value("ConfigServer/device"))
            self.configServer.host = unicode(
                settings.value("ConfigServer/host"))
            self.onlineFile = unicode(
                settings.value("Online/filename"))
            port = str(settings.value("ConfigServer/port") or "")
            if port:
                self.configServer.port = int(port)

    # updates directories in status bar
    def updateStatusBar(self):
        self.cpDirLabel.setText("CP: %s" % (self.componentList.directory))
        self.dsDirLabel.setText("DS: %s" % (self.sourceList.directory))

    # creates status bar
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

    # creates action
    # \param action the action instance
    # \param text string shown in menu
    # \param slot action slot
    # \param shortcut key short-cut
    # \param icon qrc_resource icon name
    # \param tip text for status bar and text hint
    # \param checkable if command/action checkable
    # \param signal action signal
    def __setAction(self, action, _, slot=None, shortcut=None, icon=None,
                    tip=None, checkable=False, signal="triggered"):
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % unicode(icon).strip()))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            # self.connect(action, SIGNAL(signal), slot)
            getattr(action, signal).connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def __setActions(self, slots):
        for ac, pars in slots.actions.items():
            action = getattr(self.ui, ac)
            self.__setAction(
                action, pars[0],
                getattr(slots, pars[1]),
                pars[2], pars[3], pars[4])

    def __setTasks(self, slots):
        if hasattr(slots, "tasks"):
            for pars in slots.tasks:
                # self.connect(pars[1], SIGNAL(pars[2]),
                #             getattr(slots, pars[0]))
                getattr(pars[1], pars[2]).connect(getattr(slots, pars[0]))

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

        actionUndo.setShortcut("Ctrl+Z")
        actionRedo.setShortcut("Ctrl+Y")

        self.ui.menuEdit.insertAction(self.ui.menuEdit.actions()[0],
                                      actionUndo)
        self.ui.menuEdit.insertAction(actionUndo, actionRedo)
        self.ui.editToolBar.addAction(actionUndo)
        self.ui.editToolBar.addAction(actionRedo)

    # creates actions
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

        viewCompDockAction = self.ui.compDockWidget.toggleViewAction()
        viewCompDockAction.setToolTip("Show/Hide the dock lists")
        viewCompDockAction.setStatusTip("Show/Hide the dock lists")

        viewLogDockAction = self.ui.logDockWidget.toggleViewAction()
        viewLogDockAction.setToolTip("Show/Hide the logger")
        viewLogDockAction.setStatusTip("Show/Hide the logger")

        self.ui.menuView.insertAction(
            self.ui.menuView.actions()[0],
            viewLogDockAction)

        self.ui.menuView.insertAction(
            self.ui.menuView.actions()[0],
            viewCompDockAction)

        self.__setAction(
            self.ui.actionAllAttributesView,
            "&All Attributes", self.viewAllAttributes, "",
            tip="Go to the component list", checkable=True)

        # Signals
        # self.connect(self.componentList.ui.elementListWidget,
        #              SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
        #              self.slots["Edit"].componentEdit)
        self.componentList.ui.elementListWidget.itemDoubleClicked.connect(
            self.slots["Edit"].componentEdit)

        # self.connect(self.sourceList.ui.elementListWidget,
        #              SIGNAL("itemDoubleClicked(QListWidgetItem*)"),
        #              self.slots["Edit"].dsourceEdit)
        self.sourceList.ui.elementListWidget.itemDoubleClicked.connect(
            self.slots["Edit"].dsourceEdit)

        # Component context menu
        self.ui.mdi.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.contextMenuActions = (
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
            None,
            self.ui.actionClearComponentItems
        )

        # Component list menu
        self.componentListMenuActions = (
            self.ui.actionNew,
            self.ui.actionEditComponent,
            self.ui.actionMergeComponentItems,
            self.ui.actionClose,
            None, {"File": (
                self.ui.actionLoad,
                self.ui.actionSave,
                self.ui.actionSaveAs,
                self.ui.actionSaveAll,
                self.ui.actionReloadList,
                self.ui.actionChangeDirectory)},
            None, {"Server": (
                self.ui.actionFetchComponentsServer,
                self.ui.actionStoreComponentServer,
                self.ui.actionStoreAllComponentsServer,
                self.ui.actionDeleteComponentServer,
                self.ui.actionGetMandatoryComponentsServer,
                self.ui.actionSetComponentMandatoryServer,
                self.ui.actionUnsetComponentMandatoryServer)},
            None,
            self.ui.actionTakeDataSources
        )

        # DataSource list menu
        self.dsourceListMenuActions = (
            self.ui.actionNewDataSource,
            self.ui.actionEditDataSource,
            self.ui.actionApplyDataSource,
            self.ui.actionCloseDataSource,
            None,
            self.ui.actionCopyDataSource,
            self.ui.actionCutDataSource,
            self.ui.actionPasteDataSource,
            None, {"File": (
                self.ui.actionLoadDataSource,
                self.ui.actionSaveDataSource,
                self.ui.actionSaveDataSourceAs,
                self.ui.actionSaveAllDataSources,
                self.ui.actionReloadDataSourceList,
                self.ui.actionChangeDataSourceDirectory)},
            None, {"Server": (
                self.ui.actionFetchDataSourcesServer,
                self.ui.actionStoreDataSourceServer,
                self.ui.actionStoreAllDataSourcesServer,
                self.ui.actionDeleteDataSourceServer)}
        )

        # datasource widget actions
        self.externalDSActions = {
            "externalSave": self.slots["File"].dsourceSaveButton,
            "externalApply": self.slots["Edit"].dsourceApplyButton,
            "externalClose": self.slots["Windows"].dsourceClose,
            "externalStore": self.slots[
                "Server"].serverStoreDataSourceButton}

        # component widget actions
        self.externalCPActions = {
            "externalSave": self.slots["File"].componentSaveButton,
            "externalStore": self.slots["Server"].serverStoreComponentButton,
            "externalApply": self.slots["Item"].componentApplyItemButton,
            "externalClose": self.slots["Windows"].componentClose,
            "externalDSLink": self.slots[
                "Item"].componentLinkDataSourceItemButton}

    # stores the list element before finishing the application
    # \param event Qt event
    # \param elementList element list
    # \param failures a list of errors
    # \returns True if not canceled
    def closeList(self, event, elementList, failures):
        status = None
        for k in elementList.elements.keys():
            cp = elementList.elements[k]
            if (hasattr(cp, "isDirty") and cp.isDirty()) or \
                    (hasattr(cp, "instance")
                     and hasattr(cp.instance, "isDirty")
                     and cp.instance.isDirty()):
                if status != QMessageBox.YesToAll \
                        and status != QMessageBox.NoToAll:
                    status = QMessageBox.question(
                        self, "%s - Save" % elementList.clName,
                        "Do you want to save %s: %s"
                        % (elementList.clName, cp.name),
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                        | QMessageBox.YesToAll | QMessageBox.NoToAll,
                        QMessageBox.Yes)

                if status == QMessageBox.Yes or status == QMessageBox.YesToAll:
                    try:
                        cid = elementList.currentListElement()
                        elementList.populateElements(cp.id)
                        if hasattr(cp.instance, "merge"):
                            self.slots["Edit"].componentEdit()
                            cp.instance.merge()
                        else:
                            self.slots["Edit"].dsourceEdit()
                        if not cp.instance.save():
                            elementList.populateElements(cid)
                            if event:
                                event.ignore()
                            return
                        elementList.populateElements(cid)

                    except IOError as e:
                        failures.append(unicode(e))

                elif status == QMessageBox.Cancel:
                    if event:
                        event.ignore()
                    return
        return True

    # Provides a name of the currently selected datasource
    def currentDataSourceName(self):
        name = ""
        if hasattr(self.sourceList.currentListElement(), "id"):
            dsid = self.sourceList.currentListElement().id
            ds = self.sourceList.elements[dsid]
            if ds and ds.name:
                name = ds.name
                if ds and ds.name and ds.instance:
                    name = ds.instance.name
        return name

    # Stores settings in QSettings object
    def __storeSettings(self):
        settings = QSettings()
        settings.setValue(
            "MainWindow/Geometry",
            (self.saveGeometry()))
        settings.setValue(
            "MainWindow/State",
            (self.saveState()))
        settings.setValue(
            "DataSources/directory",
            (os.path.abspath(self.sourceList.directory)))
        settings.setValue(
            "Components/directory",
            (os.path.abspath(self.componentList.directory)))

        if self.configServer:
            settings.setValue("ConfigServer/device",
                              (self.configServer.device))
            settings.setValue("ConfigServer/host",
                              (self.configServer.host))
            settings.setValue("ConfigServer/port",
                              (self.configServer.port))
            settings.setValue("ConfigServer/port",
                              (self.configServer.port))
            settings.setValue("Online/filename",
                              (self.onlineFile))
            self.configServer.close()

    # stores the setting before finishing the application
    # \param event Qt event
    def closeEvent(self, event):
        failures = []
        if not self.closeList(event, self.componentList, failures):
            return
        if not self.closeList(event, self.sourceList, failures):
            return
        if (failures and
            QMessageBox.warning(
                self, "NXS Component Designer -- Save Error",
                "Failed to save%s\nQuit anyway?"
                % unicode("\n\t".join(failures)),
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No):
            event.ignore()
            return

        self.__storeSettings()
        self.ui.mdi.closeAllSubWindows()

    # disables/enable the server actions
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
        self.ui.actionCreateComponentServer.setDisabled(
            status or not NXSTOOLS_AVAILABLE)
        self.ui.actionCreateStdComponentServer.setDisabled(
            status or not NXSTOOLS_AVAILABLE)
        self.ui.actionCreateDataSourcesServer.setDisabled(
            status or not NXSTOOLS_AVAILABLE)

        if self.configServer and self.configServer.device:
            dev = "%s:%s/%s" % (
                self.configServer.host
                if self.configServer.host else "localhost",
                str(self.configServer.port)
                if self.configServer.port else "10000",
                self.configServer.device
            )
        else:
            dev = "None"

        if status:
            self.setWindowTitle("NXS Component Designer -||- [%s]" % dev)
        else:
            self.setWindowTitle("NXS Component Designer <-> [%s]" % dev)

    # loads the datasource list
    # \brief It loads the datasource list from the default directory
    def loadDataSources(self):
        self.sourceList.loadList(self.externalDSActions)
        ide = iternext(self.sourceList.elements).id \
            if len(self.sourceList.elements) else None

        self.sourceList.populateElements(ide)

    # sets the datasource list from dictionary
    # \param datasources dictionary with datasources, i.e. name:xml
    # \param new logical variable set to True if objects are not saved
    def setDataSources(self, datasources, new=False):
        last = self.sourceList.setList(
            datasources,
            self.externalDSActions,
            None,
            new)
        ide = iternext(self.sourceList.elements).id \
            if len(self.sourceList.elements) else None

        self.sourceList.populateElements(ide)
        return last

    # sets the component list from the given dictionary
    # \param components dictionary with components, i.e. name:xml
    def setComponents(self, components):
        self.componentList.setList(
            components,
            self.externalCPActions,
            self.contextMenuActions
        )
        ide = iternext(self.componentList.elements).id \
            if len(self.componentList.elements) else None

        self.componentList.populateElements(ide)

    # loads the component list
    # \brief It loads the component list from the default directory
    def loadComponents(self):
        self.componentList.loadList(
            self.externalCPActions,
            self.contextMenuActions
        )
        ide = iternext(self.componentList.elements).id \
            if len(self.componentList.elements) else None

        self.componentList.populateElements(ide)

    # update datasource list item according to open window
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

    # update component list item according to open window
    # \returns True if windows is open
    def updateComponentListItem(self):
        status = False
        if self.ui.mdi.activeSubWindow() and isinstance(
                self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            widget = self.ui.mdi.activeSubWindow().widget()
            if isinstance(widget, ComponentDlg):
                if widget.component.id is not None:

                    if hasattr(self.componentList.currentListElement(), "id"):
                        if self.componentList.currentListElement().id \
                                != widget.component.id:
                            self.componentList.populateElements(
                                widget.component.id)
                    status = True
        return status

    # actives sub-window if in mdi area
    def setActiveSubWindow(self, window):
        w = window if window in self.ui.mdi.subWindowList() else None
        self.ui.mdi.setActiveSubWindow(w)

    # deselect component list item according to open window
    def deselectComponentSubWindow(self):
        if self.ui.mdi.activeSubWindow() and isinstance(
                self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            widget = self.ui.mdi.activeSubWindow().widget()
            if isinstance(widget, ComponentDlg):
                if widget.component.id is not None:

                    if hasattr(self.componentList.currentListElement(), "id"):
                        if self.componentList.currentListElement().id \
                                != widget.component.id:

                            self.setActiveSubWindow(None)

    # deselect component list item according to open window
    def deselectDataSourceSubWindow(self):
        if self.ui.mdi.activeSubWindow() and isinstance(
                self.ui.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            widget = self.ui.mdi.activeSubWindow().widget()
            if isinstance(widget, CommonDataSourceDlg):
                if widget.datasource.id is not None:

                    if hasattr(self.sourceList.currentListElement(), "id"):
                        if self.sourceList.currentListElement().id \
                                != widget.datasource.id:

                            self.setActiveSubWindow(None)

    # shows all attributes in the tree
    # \brief switch between all attributes in the tree or only type attribute
    def viewAllAttributes(self):
        self.componentList.viewAttributes(
            not self.componentList.viewAttributes())

    # provides subwindow defined by instance
    # \param instance given instance
    # \param subwindows list of subwindows
    # \returns required subwindow
    @classmethod
    def subWindow(cls, instance, subwindows):
        swin = None
        for sw in subwindows:
            if hasattr(sw, "widget"):
                if hasattr(sw.widget(), "component") \
                        and sw.widget().component == instance:
                    swin = sw
                    break
                elif hasattr(sw.widget(), "datasource") \
                        and sw.widget().datasource == instance:
                    swin = sw
                    break
        return swin
