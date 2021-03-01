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
# \file FileCommands.py
# user commands of GUI application

""" Component Designer commands """

from PyQt5.QtWidgets import (QMessageBox, QFileDialog, QUndoCommand,
                             QProgressDialog)
from PyQt5.QtCore import (Qt, QFileInfo)

from .DataSourceDlg import CommonDataSourceDlg
from . import DataSource
from .ComponentDlg import ComponentDlg
from .Component import Component
from .LabeledObject import LabeledObject

import sys
import logging
# message logger
logger = logging.getLogger("nxsdesigner")

if sys.version_info > (3,):
    unicode = str


# Command which loads an existing component from the file
class ComponentOpen(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._cpEdit = None
        self._cp = None
        self._fpath = None
        self._subwindow = None

    # executes the command
    # \brief It loads an existing component from the file
    def redo(self):
        if hasattr(self.receiver.ui, 'mdi'):
            if self._cp is None:
                self._cp = LabeledObject("", None)
            else:
                self._cp.instance = None

            self._cpEdit = Component(self.receiver.componentList)
            self._cpEdit.id = self._cp.id
            self._cpEdit.directory = self.receiver.componentList.directory
            self._cpEdit.createGUI()
            self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
            if self._fpath:
                path = self._cpEdit.load(self._fpath)
            else:
                path = self._cpEdit.load()
                self._fpath = path

            if hasattr(self._cpEdit, "connectExternalActions"):
                self._cpEdit.connectExternalActions(
                    **self.receiver.externalCPActions)

            if path:
                self._cp.name = self._cpEdit.name
                self._cp.instance = self._cpEdit

                self.receiver.componentList.addElement(self._cp, False)
                self._cpEdit.dialog.setWindowTitle(
                    "%s [Component]" % self._cp.name)

                subwindow = self.receiver.subWindow(
                    self._cp.instance,
                    self.receiver.ui.mdi.subWindowList())
                if subwindow:
                    self.receiver.setActiveSubWindow(subwindow)
                    self._cp.instance.dialog.setSaveFocus()
                else:
                    self._subwindow = self.receiver.ui.mdi.addSubWindow(
                        self._cpEdit.dialog)
                    self._subwindow.resize(680, 560)
                    self._cpEdit.dialog.setSaveFocus()
                    self._cpEdit.dialog.show()
                    self._cp.instance = self._cpEdit
                self._cpEdit.dialog.show()
                logger.debug("EXEC componentOpen")

    # unexecutes the command
    # \brief It removes the loaded component from the component list
    def undo(self):
        if hasattr(self._cp, "instance"):
            if self._fpath:

                if hasattr(self._cp, 'instance') and self._cp.instance:
                    subwindow = self.receiver.subWindow(
                        self._cpEdit, self.receiver.ui.mdi.subWindowList())
                    if subwindow:
                        self.receiver.setActiveSubWindow(subwindow)
                        self.receiver.ui.mdi.closeActiveSubWindow()

                self.receiver.componentList.removeElement(
                    self._cp, False)
                self._cp.instance = None

        logger.debug("UNDO componentOpen")


# Command which loads an existing datasource from the file
class DataSourceOpen(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._dsEdit = None
        self._ds = None
        self._fpath = None
        self._subwindow = None

    # executes the command
    # \brief It loads an existing datasource from the file
    def redo(self):
        if hasattr(self.receiver.ui, 'mdi'):
            if self._ds is None:
                self._ds = LabeledObject("", None)
            else:
                self._ds.instance = None

            self._dsEdit = DataSource.DataSource(self.receiver.sourceList)
            self._dsEdit.id = self._ds.id
            self._dsEdit.directory = self.receiver.sourceList.directory
            if self._fpath:
                path = self._dsEdit.load(self._fpath)
            else:
                path = self._dsEdit.load()
                self._fpath = path
            if hasattr(self._dsEdit, "connectExternalActions"):
                self._dsEdit.connectExternalActions(
                    **self.receiver.externalDSActions)
            if path:
                self._ds.name = self._dsEdit.name
                self._ds.instance = self._dsEdit

                self.receiver.sourceList.addElement(self._ds, False)

                self._dsEdit.dialog.setWindowTitle(
                    "%s [DataSource]" % self._ds.name)

                subwindow = self.receiver.subWindow(
                    self._ds.instance,
                    self.receiver.ui.mdi.subWindowList())
                if subwindow:
                    self.receiver.setActiveSubWindow(subwindow)
                    self._ds.instance.dialog.setSaveFocus()
                else:
                    self._subwindow = self.receiver.ui.mdi.addSubWindow(
                        self._dsEdit.dialog)
                    self._subwindow.resize(440, 550)
                    self._dsEdit.dialog.setSaveFocus()
                    self._dsEdit.dialog.show()
                    self._ds.instance = self._dsEdit

                self._dsEdit.dialog.show()
                logger.debug("EXEC dsourceOpen")

    # unexecutes the command
    # \brief It removes the loaded datasource from the datasource list
    def undo(self):
        if hasattr(self._ds, "instance"):
            if self._fpath:

                if hasattr(self._ds, 'instance'):
                    subwindow = self.receiver.subWindow(
                        self._ds.instance,
                        self.receiver.ui.mdi.subWindowList())
                    if subwindow:
                        self.receiver.setActiveSubWindow(subwindow)
                        self.receiver.ui.mdi.closeActiveSubWindow()

                self.receiver.sourceList.removeElement(self._ds, False)
                self._ds.instance = None

        logger.debug("UNDO dsourceOpen")


# Command which saves with the current component in the file
class ComponentSave(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._cp = None
        self._cpEdit = None
        self._subwindow = None

    # executes the command
    # \brief It saves with the current component in the file
    def redo(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is None:
            QMessageBox.warning(
                self.receiver, "Component not selected",
                "Please select one of the components")
        else:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()
                self._cpEdit = Component(self.receiver.componentList)
                self._cpEdit.id = self._cp.id
                self._cpEdit.directory = \
                    self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.elements[
                    self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(
                    self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle(
                    "%s [Component]" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance

            if hasattr(self._cpEdit, "connectExternalActions"):
                self._cpEdit.connectExternalActions(
                    **self.receiver.externalCPActions)

            subwindow = self.receiver.subWindow(
                self._cpEdit, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
            else:
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._cpEdit.dialog)
                self._subwindow.resize(680, 560)
                self._cpEdit.dialog.show()
            self._cp.instance = self._cpEdit

            if self._cpEdit.save():
                self._cp.savedName = self._cp.name
        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()

        logger.debug("EXEC componentSave")

    # unexecutes the command
    # \brief It populates the component list
    def undo(self):
        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()
        logger.debug("UNDO componentSave")


# Command which saves all components in the file
class ComponentSaveAll(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It saves all components in the file
    def redo(self):

        keys = list(self.receiver.componentList.elements.keys())
        progress = QProgressDialog(
            "Saving Component elements",
            "", 0, len(keys), self.receiver.componentList)
        progress.setWindowTitle("Save All Components")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        for i in range(len(keys)):
            icp = keys[i]
            cp = self.receiver.componentList.elements[icp]
            if cp.instance is None:
                #                self._cpEdit = FieldWg()
                cpEdit = Component(self.receiver.componentList)
                cpEdit.id = cp.id
                cpEdit.directory = self.receiver.componentList.directory
                cpEdit.name = \
                    self.receiver.componentList.elements[cp.id].name
                cpEdit.createGUI()
                cpEdit.addContextMenu(self.receiver.contextMenuActions)
                cpEdit.createHeader()
                cpEdit.dialog.setWindowTitle("%s [Component]" % cp.name)
                cp.instance = cpEdit

            if cp.instance is not None:
                cp.instance.merge(False)
                cp.instance.save()
            progress.setValue(i)
        progress.setValue(len(keys))
        progress.close()

        logger.debug("EXEC componentSaveAll")


# Command which saves the current components in the file with a different name
class ComponentSaveAs(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        # new name of component
        self.name = None
        # directory of the component file
        self.directory = None

        self._cp = None
        self._pathFile = None
        self._subwindow = None

    # executes the command
    # \brief It saves the current components in the file with a different name
    def redo(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is None:
            QMessageBox.warning(self.receiver, "Component not selected",
                                "Please select one of the components")
        else:
            if self._cp.instance is not None:
                self._pathFile = self._cp.instance.getNewName()
                fi = QFileInfo(self._pathFile)
                self.name = unicode(fi.fileName())
                if self.name[-4:] == '.xml':
                    self.name = self.name[:-4]
                self.directory = unicode(fi.dir().path())
                self._cp.instance.name = self.name
                self._cp.instance.directory = self.directory

        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()
        logger.debug("EXEC componentSaveAs")

    # unexecutes the command
    # \brief It populates the Component list
    def undo(self):
        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()
        logger.debug("UNDO componentSaveAs")


# Command which changes the current component file directory
class ComponentChangeDirectory(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It changes the current component file directory
    def redo(self):
        failures = []
        if not self.receiver.closeList(
                None, self.receiver.componentList, failures):
            return
        if (failures and QMessageBox.question(
                self.receiver,
                "Component - Reload List from Configuration server",
                ("All unsaved components will be lost. "
                 "Would you like to proceed ?").encode(),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes) == QMessageBox.No):
            return

        path = unicode(QFileDialog.getExistingDirectory(
            self.receiver, "Open Directory",
            self.receiver.componentList.directory,
            QFileDialog.ShowDirsOnly or QFileDialog.DontResolveSymlinks))

        if not path:
            return
        subwindows = self.receiver.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), ComponentDlg):
                    self.receiver.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        self.receiver.componentList.elements = {}
        self.receiver.componentList.directory = path
        self.receiver.updateStatusBar()

        self.receiver.loadComponents()

        logger.debug("EXEC componentChangeDirectory")


# Command which saves all the datasources in files
class DataSourceSaveAll(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It saves all the datasources in files
    def redo(self):
        keys = self.receiver.sourceList.elements.keys()
        progress = QProgressDialog(
            "Saving DataSource elements",
            "", 0, len(keys), self.receiver.sourceList)
        progress.setWindowTitle("Save All DataSources")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()

        for i in range(len(keys)):
            ids = keys[i]
            ds = self.receiver.sourceList.elements[ids]
            if ds.instance is None:
                dsEdit = DataSource.DataSource(self.receiver.sourceList)
                dsEdit.id = ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = \
                    self.receiver.sourceList.elements[ds.id].name
                ds.instance = dsEdit

            if ds.instance is not None:
                if ds.instance.save():
                    ds.savedName = ds.name
            progress.setValue(i)
        progress.setValue(len(keys))
        progress.close()

        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds, "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()

        logger.debug("EXEC dsourceSaveAll")


# Command which saves the current datasource in files
class DataSourceSave(QUndoCommand):
    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None

    # executes the command
    # \brief It saves the current datasource in files
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(
                self.receiver, "DataSource not selected",
                "Please select one of the datasources")

        if self._ds is not None and hasattr(self._ds, "instance"):
            if self._ds.instance is None:
                dsEdit = DataSource.DataSource(self.receiver.sourceList)
                dsEdit.id = self._ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = self.receiver.sourceList.elements[
                    self._ds.id].name
                self._ds.instance = dsEdit

            if self._ds.instance.save():
                self._ds.savedName = self._ds.name

        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds, "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()

        logger.debug("EXEC dsourceSave")

    # unexecutes the command
    # \brief It populates the datasource list
    def undo(self):
        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds, "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()
        logger.debug("UNDO dsourceSave")


# Command which saves the current datasource in files with a different name
class DataSourceSaveAs(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        # new datasource name
        self.name = None
        # new file directory
        self.directory = None

        self._ds = None
        self._pathFile = None

    # executes the command
    # \brief It saves the current datasource in files with a different name
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected",
                                "Please select one of the datasources")
        else:
            if self._ds.instance is None:
                dsEdit = DataSource.DataSource(self.receiver.sourceList)
                dsEdit.id = self._ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = self.receiver.sourceList.elements[
                    self._ds.id].name
                self._ds.instance = dsEdit

            if self._ds.instance is not None:
                self._pathFile = self._ds.instance.getNewName()
                fi = QFileInfo(self._pathFile)
                self.name = unicode(fi.fileName())
                if self.name[-4:] == '.xml':
                    self.name = self.name[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]

                self.directory = unicode(fi.dir().path())

        logger.debug("EXEC dsourceSaveAs")


# Command which changes the current file directory with datasources
class DataSourceChangeDirectory(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It changes the current file directory with datasources
    def redo(self):
        failures = []
        if not self.receiver.closeList(
                None, self.receiver.sourceList, failures):
            return
        if (failures and QMessageBox.question(
                self.receiver,
                "DataSource - Reload List from Configuration Server",
                ("All unsaved datasources will be lost. "
                 "Would you like to proceed ?").encode(),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes) == QMessageBox.No):
            return

        path = unicode(QFileDialog.getExistingDirectory(
            self.receiver, "Open Directory",
            self.receiver.sourceList.directory,
            QFileDialog.ShowDirsOnly or QFileDialog.DontResolveSymlinks))

        if not path:
            return

        subwindows = self.receiver.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), CommonDataSourceDlg):
                    self.receiver.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        self.receiver.sourceList.elements = {}
        self.receiver.sourceList.directory = path
        self.receiver.updateStatusBar()

        self.receiver.loadDataSources()

        logger.debug("EXEC dsourceChangeDirectory")


# Command which reloads the components from the current component directory
#  into the component list
class ComponentReloadList(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It reloads the components from the current component directory
    #        into the component list
    def redo(self):
        failures = []
        if not self.receiver.closeList(
                None, self.receiver.componentList, failures):
            return
        if (failures and QMessageBox.question(
                self.receiver,
                "Component - Reload List from Configuration server",
                ("All unsaved components will be lost. "
                 "Would you like to proceed ?").encode(),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes) == QMessageBox.No):
            return

        subwindows = self.receiver.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), ComponentDlg):
                    self.receiver.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        self.receiver.componentList.elements = {}
        self.receiver.loadComponents()

        logger.debug("EXEC componentReloadList")


# Command which reloads the datasources from the current datasource directory
#  into the datasource list
class DataSourceReloadList(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It reloads the datasources from the current datasource directory
    #        into the datasource list
    def redo(self):
        failures = []
        if not self.receiver.closeList(
                None, self.receiver.sourceList, failures):
            return
        if (failures and QMessageBox.question(
                self.receiver,
                "DataSource - Reload List from Configuration Server",
                ("All unsaved datasources will be lost. "
                 "Would you like to proceed ?").encode(),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes) == QMessageBox.No):
            return

        subwindows = self.receiver.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), CommonDataSourceDlg):
                    self.receiver.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        self.receiver.sourceList.elements = {}
        self.receiver.loadDataSources()

        logger.debug("EXEC dsourceReloadList")


if __name__ == "__main__":
    pass
