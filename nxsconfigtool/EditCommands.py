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
# \file EditCommands.py
# user commands of GUI application

""" Component Designer commands """

from PyQt5.QtWidgets import (QUndoCommand, QMessageBox)

from .DataSourceDlg import DataSourceDlg
from . import DataSource
from .Component import Component

import sys
import logging
# message logger
logger = logging.getLogger("nxsdesigner")


def iternext(it):
    if sys.version_info > (3,):
        return next(iter(it.values()))
    else:
        return it.itervalues().next()


# Command which opens dialog with the current component
class ComponentEdit(QUndoCommand):

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
    # \brief It opens dialog with the current component
    def redo(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is None:
            QMessageBox.warning(self.receiver, "Component not selected",
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
                    "%s [Component]*" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance

            if hasattr(self._cpEdit, "connectExternalActions"):
                self._cpEdit.connectExternalActions(
                    **self.receiver.externalCPActions)

            subwindow = self.receiver.subWindow(
                self._cpEdit, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._cpEdit.reconnectSaveAction()
            else:
                self._cpEdit.createGUI()

                self._cpEdit.addContextMenu(
                    self.receiver.contextMenuActions)
                if self._cpEdit.isDirty():
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]*" % self._cp.name)
                else:
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]" % self._cp.name)

                self._cpEdit.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._cpEdit.dialog)
                self._subwindow.resize(680, 560)
                self._cpEdit.dialog.show()
            self._cp.instance = self._cpEdit

        logger.debug("EXEC componentEdit")

    # unexecutes the command
    # \brief It does nothing
    def undo(self):
        logger.debug("UNDO componentEdit")


# Command which copies the current datasource into the clipboard
class DataSourceCopy(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None

    # executes the command
    # \brief It copies the current datasource into the clipboard
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected",
                                "Please select one of the datasources")
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState()
                self._ds.instance.copyToClipboard()
            else:
                self.receiver.sourceList.elements[
                    self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

            self._newstate = self._ds.instance.getState()

        logger.debug("EXEC dsourceCopy")

    # unexecutes the command
    # \brief It updates state of datasource to the old state
    def undo(self):
        if self._ds is not None and hasattr(self._ds, 'instance') \
                and self._ds.instance is not None:

            self.receiver.sourceList.elements[
                self._ds.id].instance.setState(self._oldstate)
            self.receiver.sourceList.elements[
                self._ds.id].instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

        logger.debug("UNDO dsourceCopy")


# Command which moves the current datasource into the clipboard
class DataSourceCut(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None

    # executes the command
    # \brief It moves the current datasource into the clipboard
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected",
                                "Please select one of the datasources")
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState()
                self._ds.instance.copyToClipboard()
                self._ds.instance.clear()
                self._ds.instance.updateForm()
                self._ds.instance.dialog.show()
            else:
                self.receiver.sourceList.elements[
                    self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

            self._newstate = self._ds.instance.getState()
        if hasattr(self._ds, "id"):
            self.receiver.sourceList.populateElements(self._ds.id)
        else:
            self.receiver.sourceList.populateElements()

        logger.debug("EXEC dsourceCut")

    # unexecutes the command
    # \brief It copy back the removed datasource
    def undo(self):
        if self._ds is not None and hasattr(self._ds, 'instance') \
                and self._ds.instance is not None:

            self.receiver.sourceList.elements[
                self._ds.id].instance.setState(self._oldstate)
            self.receiver.sourceList.elements[
                self._ds.id].instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

        if hasattr(self._ds, "id"):
            self.receiver.sourceList.populateElements(self._ds.id)
        else:
            self.receiver.sourceList.populateElements()

        logger.debug("UNDO dsourceCut")


# Command which pastes the current datasource from the clipboard
class DataSourcePaste(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None

    # executes the command
    # \brief It pastes the current datasource from the clipboard
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected",
                                "Please select one of the datasources")
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState()
                self._ds.instance.clear()
                if not self._ds.instance.copyFromClipboard():
                    QMessageBox.warning(
                        self.receiver, "Pasting item not possible",
                        "Probably clipboard does not contain datasource")

                self._ds.instance.updateForm()
#                self._ds.instance.updateNode()
                self._ds.instance.dialog.setFrames(
                    self._ds.instance.dataSourceType)

#                self._ds.instance.updateForm()
                self._ds.instance.dialog.show()
            else:
                self.receiver.sourceList.elements[
                    self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()
#                self._ds.instance.updateNode()

            self._newstate = self._ds.instance.getState()

            self.receiver.sourceList.elements[
                self._ds.id].instance.setState(self._oldstate)
            self._ds.instance.updateNode()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createDialog()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

            if hasattr(self._ds, "id"):
                self.receiver.sourceList.populateElements(self._ds.id)
            else:
                self.receiver.sourceList.populateElements()
        logger.debug("EXEC dsourcePaste")

    # unexecutes the command
    # \brief It remove the pasted datasource
    def undo(self):
        if self._ds is not None and hasattr(self._ds, 'instance') \
                and self._ds.instance is not None:

            self.receiver.sourceList.elements[
                self._ds.id].instance.setState(self._oldstate)
            self.receiver.sourceList.elements[
                self._ds.id].instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

            if hasattr(self._ds, "id"):
                self.receiver.sourceList.populateElements(self._ds.id)
            else:
                self.receiver.sourceList.populateElements()

        logger.debug("UNDO dsourcePaste")


# Command which applies the changes from the form for the current datasource
class DataSourceApply(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None
        self._oldstate = None
        self._newstate = None
        self._subwindow = None

    # executes the command
    # \brief It applies the changes from the form for the current datasource
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected",
                                "Please select one of the datasources")
            return
        if self._ds.instance is None:
            #                self._dsEdit = FieldWg()
            self._ds.instance = DataSource.DataSource(self.receiver.sourceList)
            self._ds.instance.id = self._ds.id
            self._ds.instance.directory = \
                self.receiver.sourceList.directory
            self._ds.instance.name = self.receiver.sourceList.elements[
                self._ds.id].name
        if not self._ds.instance.dialog:
            self._ds.instance.createDialog()
            self._ds.instance.dialog.setWindowTitle(
                "%s [DataSource]*" % self._ds.name)

            if hasattr(self._ds.instance, "connectExternalActions"):
                self._ds.instance.connectExternalActions(
                    **self.receiver.externalDSActions)
            self._subwindow = self.receiver.ui.mdi.addSubWindow(
                self._ds.instance.dialog)
            self._subwindow.resize(440, 550)
            self._ds.instance.dialog.show()

        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState()
            else:
                self.receiver.sourceList.elements[
                    self._ds.id].instance.setState(
                    self._newstate)
                if not hasattr(self._ds.instance.dialog.ui, "docTextEdit"):
                    self._ds.instance.createDialog()
                self._ds.instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [Component]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [Component]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._ds.instance.dialog.show()

            self._ds.instance.apply()
            self._newstate = self._ds.instance.getState()

            if hasattr(self._ds, "id"):
                self.receiver.sourceList.populateElements(self._ds.id)
            else:
                self.receiver.sourceList.populateElements()
        else:
            QMessageBox.warning(self.receiver, "DataSource not created",
                                "Please edit one of the datasources")

        logger.debug("EXEC dsourceApply")

    # unexecutes the command
    # \brief It recovers the old state of the current datasource
    def undo(self):
        if self._ds is not None and hasattr(self._ds, 'instance') \
                and self._ds.instance is not None:

            self.receiver.sourceList.elements[
                self._ds.id].instance.setState(self._oldstate)

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self.receiver.sourceList.elements[
                    self._ds.id].instance.updateForm()
                self._ds.instance.reconnectSaveAction()

            else:
                self._ds.instance.createDialog()

                self.receiver.sourceList.elements[
                    self._ds.id].instance.updateForm()

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)

            self._ds.instance.updateNode()
            if self._ds.instance.isDirty():
                self._ds.instance.dialog.setWindowTitle(
                    "%s [Component]*" % self._ds.name)
            else:
                self._ds.instance.dialog.setWindowTitle(
                    "%s [Component]" % self._ds.name)
            self._ds.instance.dialog.show()

            if hasattr(self._ds, "id"):
                self.receiver.sourceList.populateElements(self._ds.id)
            else:
                self.receiver.sourceList.populateElements()

        logger.debug("UNDO dsourceApply")


# Command which takes the datasources from the current component
class ComponentTakeDataSources(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._cp = None

    # executes the command
    # \brief It reloads the datasources from the current datasource directory
    #        into the datasource list
    def redo(self):

        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is None:
            QMessageBox.warning(self.receiver, "Component not selected",
                                "Please select one of the components")
        else:
            if self._cp.instance is not None:
                datasources = self._cp.instance.getDataSources()

                if datasources:
                    dialogs = self.receiver.ui.mdi.subWindowList()
                    if dialogs:
                        for dialog in dialogs:
                            if isinstance(dialog, DataSourceDlg):
                                self.receiver.setActiveSubWindow(
                                    dialog)
                                self.receiver.ui.mdi.closeActiveSubWindow()

                    self.receiver.setDataSources(datasources, new=True)
                else:
                    QMessageBox.warning(
                        self.receiver, "DataSource item not selected",
                        "Please select one of the datasource items")

        logger.debug("EXEC componentTakeDataSources")

    # unexecutes the command
    # \brief It does nothing
    def undo(self):
        logger.debug("UNDO componentTakeDataSources")


# Command which takes the datasources from the current component
class ComponentTakeDataSource(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._cp = None
        self._ids = None
        self._ds = None
        self._lids = None

    # executes the command
    # \brief It reloads the datasources from the current datasource directory
    #        into the datasource list
    def redo(self):

        if not self._lids:
            self._lids = \
                iternext(self.receiver.sourceList.elements).id \
                if len(self.receiver.sourceList.elements) else None
        if self._ids and self._ds:
            self.receiver.sourceList.addElement(self._ds)
            self.receiver.sourceList.populateElements(self._ids)

        else:
            if self._cp is None:
                self._cp = \
                    self.receiver.componentList.currentListElement()
            if self._cp is not None:
                if self._cp.instance is not None:

                    datasource = self._cp.instance.getCurrentDataSource()
                    if datasource:
                        dialogs = self.receiver.ui.mdi.subWindowList()
                        if dialogs:
                            for dialog in dialogs:
                                if isinstance(dialog, DataSourceDlg):
                                    self.receiver.ui.mdi.\
                                        setActiveSubWindow(
                                            dialog)
                                    self.receiver.ui.mdi\
                                        .closeActiveSubWindow()

                        self._ids = self.receiver.setDataSources(
                            datasource, new=True)
                        self._ds = \
                            self.receiver.sourceList.elements[self._ids]
                        self.receiver.sourceList.populateElements(
                            self._ids)
                    else:
                        QMessageBox.warning(
                            self.receiver, "DataSource item not selected",
                            "Please select one of the datasource items")

        logger.debug("EXEC componentTakeDataSource")

    # unexecutes the command
    # \brief It does nothing
    def undo(self):
        logger.debug("UNDO componentTakeDataSource")

        self.receiver.sourceList.removeElement(self._ds, False)
        if hasattr(self._ds, 'instance'):
            subwindow = self.receiver.subWindow(
                self._ds.instance,
                self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self.receiver.ui.mdi.closeActiveSubWindow()

        self.receiver.sourceList.populateElements(self._lids)


# Command which opens the dialog with the current datasource
class DataSourceEdit(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None
        self._dsEdit = None
        self._subwindow = None

    # executes the command
    # \brief It opens the dialog with the current datasource
    def redo(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected",
                                "Please select one of the datasources")
        else:
            if self._ds.instance is None:
                #                self._dsEdit = FieldWg()
                self._dsEdit = DataSource.DataSource(self.receiver.sourceList)

                self._dsEdit.id = self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
                self._dsEdit.name = self.receiver.sourceList.elements[
                    self._ds.id].name
                self._dsEdit.createDialog()
                self._dsEdit.dialog.setWindowTitle(
                    "%s [DataSource]*" % self._ds.name)
                self._ds.instance = self._dsEdit
            else:
                if not self._ds.instance.dialog:
                    self._ds.instance.createDialog()
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                self._dsEdit = self._ds.instance

            if hasattr(self._dsEdit, "connectExternalActions"):
                self._dsEdit.connectExternalActions(
                    **self.receiver.externalDSActions)

            subwindow = self.receiver.subWindow(
                self._dsEdit, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.reconnectSaveAction()
            else:
                if self._ds.instance.dialog is None:
                    self._ds.instance.createDialog()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle(
                        "%s [DataSource]" % self._ds.name)

                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(440, 550)
                self._dsEdit.dialog.show()

        logger.debug("EXEC dsourceEdit")


if __name__ == "__main__":
    pass
