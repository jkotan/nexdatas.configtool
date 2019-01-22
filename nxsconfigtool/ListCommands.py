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
# \file ListCommands.py
# user commands of GUI application

""" Component Designer commands """

from PyQt5.QtWidgets import (QMessageBox, QUndoCommand)

from .Component import Component
from .LabeledObject import LabeledObject

import sys
import logging
# message logger
logger = logging.getLogger("nxsdesigner")

if sys.version_info > (3,):
    unicode = str


# Command which creates a new component
class ComponentNew(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._comp = None

    # executes the command
    # \brief It creates a new component
    def redo(self):

        if self._comp is None:
            self._comp = LabeledObject("", None)
        else:
            self._comp.instance = None

        self.receiver.componentList.addElement(self._comp)
        logger.debug("EXEC componentNew")

    # unexecutes the command
    # \brief It removes the new component
    def undo(self):
        if self._comp is not None:
            self.receiver.componentList.removeElement(self._comp, False)

            if hasattr(self._comp, 'instance') and self._comp.instance:
                subwindow = self.receiver.subWindow(
                    self._comp.instance,
                    self.receiver.ui.mdi.subWindowList())
                if subwindow:
                    self.receiver.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        logger.debug("UNDO componentNew")


# Command which removes the current component from the component list
class ComponentRemove(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._cp = None
        self._subwindow = None

    # executes the command
    # \brief It removes the current component from the component list
    def redo(self):
        if self._cp is not None:
            self.receiver.componentList.removeElement(self._cp, False)
        else:
            self._cp = self.receiver.componentList.currentListElement()
            if self._cp is None:
                QMessageBox.warning(
                    self.receiver,
                    "Component not selected",
                    "Please select one of the components")
            else:
                self.receiver.componentList.removeElement(self._cp, True)

        if hasattr(self._cp, "instance"):
            subwindow = self.receiver.subWindow(
                self._cp.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self.receiver.ui.mdi.closeActiveSubWindow()

        logger.debug("EXEC componentRemove")

    # unexecutes the command
    # \brief It reloads the removed component from the component list
    def undo(self):
        if self._cp is not None:

            self.receiver.componentList.addElement(self._cp, False)
            if self._cp.instance is None:
                self._cp.instance = Component(self.receiver.componentList)
                self._cp.instance.id = self._cp.id
                self._cp.instance.directory = \
                    self.receiver.componentList.directory
                self._cp.instance.name = \
                    self.receiver.componentList.elements[
                        self._cp.id].name

            self._cp.instance.createGUI()
            self._cp.instance.addContextMenu(
                self.receiver.contextMenuActions)

            subwindow = self.receiver.subWindow(
                self._cp.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._cp.instance.dialog.setSaveFocus()
            else:
                if not self._cp.instance.dialog:
                    self._cp.instance.createGUI()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._cp.instance.dialog)
                self._subwindow.resize(680, 560)
                self._cp.instance.dialog.setSaveFocus()
                self._cp.instance.dialog.show()

            self._cp.instance.dialog.show()

            if hasattr(self._cp.instance, "connectExternalActions"):
                self._cp.instance.connectExternalActions(
                    **self.receiver.externalCPActions)

        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()
        logger.debug("UNDO componentRemove")


# Command which changes the current component in the list
class ComponentListChanged(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        # new item
        self.item = None
        # new directory
        self.directory = None
        # new component name
        self.name = None

        self._cp = None
        self._oldName = None
        self._oldDirectory = None

    # executes the command
    # \brief It changes the current component in the list
    def redo(self):
        if self.item is not None or self.name is not None:
            if self.name is None:
                self.name = unicode(self.item.text())
            if self._cp is None:
                self._cp, self._oldName = \
                    self.receiver.componentList.listItemChanged(
                        self.item, self.name)
            else:
                self._cp.name = self.name

            self.receiver.componentList.populateElements(
                self._cp.id if hasattr(self._cp, "id") else None)
            if hasattr(self._cp, "instance") and self._cp.instance is not None:
                self._oldDirectory = self._cp.instance.directory
                self._cp.instance.setName(self.name, self.directory)
            else:
                self._oldDirectory = \
                    self.receiver.componentList.directory

        cp = self.receiver.componentList.currentListElement()
        if hasattr(cp, "id"):
            self.receiver.componentList.populateElements(cp.id)
        else:
            self.receiver.componentList.populateElements()

        logger.debug("EXEC componentChanged")

    # unexecutes the command
    # \brief It changes back the current component in the list
    def undo(self):
        if self._cp is not None:
            self._cp.name = self._oldName
            self.receiver.componentList.addElement(self._cp, False)
            if self._cp.instance is not None:
                self._cp.instance.setName(self._oldName, self._oldDirectory)

        cp = self.receiver.componentList.currentListElement()
        if hasattr(cp, "id"):
            self.receiver.componentList.populateElements(cp.id)
        else:
            self.receiver.componentList.populateElements()

        logger.debug("UNDO componentChanged")


# Command which creates a new datasource
class DataSourceNew(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None

    # executes the command
    # \brief It creates a new datasource
    def redo(self):
        if self._ds is None:
            self._ds = LabeledObject("", None)
        else:
            self._ds.instance = None
        self.receiver.sourceList.addElement(self._ds)
        logger.debug("EXEC dsourceNew")

    # unexecutes the command
    # \brief It removes the added datasource
    def undo(self):
        if self._ds is not None:
            self.receiver.sourceList.removeElement(self._ds, False)

            if hasattr(self._ds, 'instance'):
                subwindow = \
                    self.receiver.subWindow(
                        self._ds.instance,
                        self.receiver.ui.mdi.subWindowList())
                if subwindow:
                    self.receiver.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        logger.debug("UNDO dsourceNew")


# Command which removes the current datasource from the datasource list
class DataSourceRemove(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        self._ds = None
        self._subwindow = None

    # executes the command
    # \brief It removes the current datasource from the datasource list
    def redo(self):

        if self._ds is not None:
            self.receiver.sourceList.removeElement(self._ds, False)
        else:
            self._ds = self.receiver.sourceList.currentListElement()
            if self._ds is None:
                QMessageBox.warning(
                    self.receiver, "DataSource not selected",
                    "Please select one of the datasources")
            else:
                self.receiver.sourceList.removeElement(self._ds, True)

        if hasattr(self._ds, "instance"):
            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self.receiver.ui.mdi.closeActiveSubWindow()

        logger.debug("EXEC dsourceRemove")

    # unexecutes the command
    # \brief It adds the removes datasource into the datasource list
    def undo(self):
        if self._ds is not None:

            self.receiver.sourceList.addElement(self._ds, False)

            self._ds.instance.createGUI()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.setActiveSubWindow(subwindow)
                self._ds.instance.dialog.setSaveFocus()
            else:
                self._ds.instance.createDialog()
                self._subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._ds.instance.dialog)
                self._subwindow.resize(680, 560)
                self._ds.instance.dialog.setSaveFocus()
                self._ds.instance.dialog.show()

            self._ds.instance.dialog.show()
        logger.debug("UNDO dsourceRemove")


# Command which performs change of  the current datasource
class DataSourceListChanged(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver
        # new item
        self.item = None
        # new datasource name
        self.name = None
        # new datasource directory
        self.directory = None

        self._ds = None
        self._oldName = None
        self._oldDirectory = None

    # executes the command
    # \brief It performs change of  the current datasource
    def redo(self):
        if self.item is not None or self.name is not None:
            if self.name is None:
                self.name = unicode(self.item.text())
            if self._ds is None:
                self._ds, self._oldName = \
                    self.receiver.sourceList.listItemChanged(
                        self.item, self.name)
            else:
                self._ds.name = self.name

            self.receiver.sourceList.populateElements(
                self._ds.id if hasattr(self._ds, "id") else None)
            if hasattr(self._ds, "instance") and self._ds.instance is not None:
                self._oldDirectory = self._ds.instance.directory
                self._ds.instance.setName(self.name, self.directory)
            else:
                self._oldDirectory = self.receiver.sourceList.directory

        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds, "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()

        logger.debug("EXEC dsourceChanged")

    # unexecutes the command
    # \brief It changes back the current datasource
    def undo(self):
        if self._ds is not None:
            self._ds.name = self._oldName
            self.receiver.sourceList.addElement(self._ds, False)
            if self._ds.instance is not None:
                self._ds.instance.setName(
                    self._oldName, self._oldDirectory)

        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds, "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()

        logger.debug("UNDO dsourceChanged")


# Command which is performed during closing the Component Designer
class CloseApplication(QUndoCommand):

    # constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        # main window
        self.receiver = receiver

    # executes the command
    # \brief It is performed during closing the Component Designer
    def redo(self):
        if hasattr(self.receiver.ui, 'mdi'):
            self.receiver.close()
            logger.debug("EXEC closeApp")


if __name__ == "__main__":
    pass
