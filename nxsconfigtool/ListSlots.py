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
# \file ListSlots.py
# user pool commands of GUI application

""" List slots """

from PyQt5.QtGui import QKeySequence

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
    DataSourceEdit
)


# stack with the application commands
class ListSlots(object):

    # constructor
    # \param main the main window dialog
    def __init__(self, main):
        # main window
        self.main = main
        # command stack
        self.undoStack = main.undoStack

        # action data
        self.actions = {
            "actionClose": [
                "&Remove", "componentRemove",
                "Ctrl+P", "componentremove", "Close the component"],
            "actionCloseDataSource": [
                "&Remove DataSource", "dsourceRemove",
                "Ctrl+Shift+P", "dsourceremove",
                "Close the data source"],
            "actionNew": [
                "&New", "componentNew",
                QKeySequence.New, "componentnew", "Create a new component"],
            "actionNewDataSource": [
                "&New DataSource", "dsourceNew",
                "Ctrl+Shift+N", "dsourceadd",
                "Create a new data source"],
            "actionQuit": [
                "&Quit", "closeApp",
                "Ctrl+Q", "filequit", "Close the application"],

        }

        # task data
        self.tasks = [
            ["dsourceChanged",
             self.main.sourceList.ui.elementListWidget,
             "itemChanged"],
            ["componentChanged",
             self.main.componentList.ui.elementListWidget,
             "itemChanged"],
            ["componentRowChanged",
             self.main.componentList.ui.elementListWidget,
             "currentRowChanged"],
            ["dsourceRowChanged",
             self.main.sourceList.ui.elementListWidget,
             "currentRowChanged"]
        ]

    # remove component action
    # \brief It removes from the component list the current component
    def componentRemove(self):
        cmd = ComponentRemove(self.main)
        self.undoStack.push(cmd)

    # remove datasource action
    # \brief It removes the current datasource
    def dsourceRemove(self):
        cmd = DataSourceRemove(self.main)
        self.undoStack.push(cmd)

    # new component action
    # \brief It creates a new component
    def componentNew(self):
        cmd = ComponentNew(self.main)
        self.undoStack.push(cmd)

    # new datasource action
    # \brief It creates a new datasource
    def dsourceNew(self):
        cmd = DataSourceNew(self.main)
        self.undoStack.push(cmd)

    # close application action
    # \brief It closes the main application
    def closeApp(self):
        cmd = CloseApplication(self.main)
        self.undoStack.push(cmd)

    # component change action
    # \param item new selected item on the component list
    def componentChanged(self, item):
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentListChanged(self.main)
        cmd.item = item
        self.undoStack.push(cmd)

    # datasource change action
    # \param item new selected item ond the datasource list
    def dsourceChanged(self, item):
        cmd = DataSourceEdit(self.main)
        cmd.redo()
        cmd = DataSourceListChanged(self.main)
        cmd.item = item
        self.undoStack.push(cmd)

    # component row change action
    # \param row row Changed
    def componentRowChanged(self, row):
        self.main.deselectComponentSubWindow()

        did = self.main.componentList.currentListElement()
        if did and hasattr(did, 'id'):
            self.main.componentContent(did.id)

    # dsource row change action
    # \param row row Changed
    def dsourceRowChanged(self, row):
        self.main.deselectDataSourceSubWindow()
        did = self.main.sourceList.currentListElement()
        if did and hasattr(did, 'id'):
            self.main.dataSourceContent(did.id)


if __name__ == "__main__":
    pass
