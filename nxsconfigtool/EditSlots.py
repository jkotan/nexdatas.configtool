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
# \file EditSlots.py
# user pool commands of GUI application

""" Edit slots """

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


from .EditCommands import (
    ComponentEdit,
    DataSourceCopy,
    DataSourceCut,
    DataSourcePaste,
    DataSourceApply,
    DataSourceEdit,
    ComponentTakeDataSources,
    ComponentTakeDataSource
)


# stack with the application commands
class EditSlots(object):

    # constructor
    # \param main the main window dialog
    def __init__(self, main):
        # main window
        self.main = main
        # command stack
        self.undoStack = main.undoStack

        # action data
        self.actions = {
            "actionEditComponent": [
                "&Edit Component", "componentEdit",
                "Ctrl+E", "componentedit", "Edit the component"],
            "actionTakeDataSourceItem": [
                "Take DataSource Item ", "componentTakeDataSource",
                "Ctrl+G",
                "componenttakedatasource",
                "Take the currnet data sources from the component"],
            "actionTakeDataSources": [
                "Take DataSources ", "componentTakeDataSources",
                "",
                "componenttakedatasource",
                "Take data sources from the component"],
            "actionEditDataSource": [
                "&Edit DataSource", "dsourceEdit",
                "Ctrl+Shift+E",
                "dsourceedit", "Edit the data source"],
            "actionApplyDataSource": [
                "Apply DataSource", "dsourceApply",
                "Ctrl+Shift+R", "dsourceapply", "Apply the data source"],
            "actionCopyDataSource": [
                "Copy DataSource", "dsourceCopy",
                "", "copy", "Copy the data source"],
            "actionCutDataSource": [
                "Cut DataSource", "dsourceCut",
                QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Delete),
                "cut", "Cut the data source"],
            "actionPasteDataSource": [
                "Paste DataSource", "dsourcePaste",
                QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Insert),
                "paste", "Paste the data source"]
        }

    # take datasources
    # \brief It takes datasources from the current component
    def componentTakeDataSources(self):
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentTakeDataSources(self.main)
        cmd.redo()
        self.undoStack.clear()

    # take datasources
    # \brief It takes datasources from the current component
    def componentTakeDataSource(self):
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentTakeDataSource(self.main)
        self.undoStack.push(cmd)

    # edit component action
    # \brief It opens a dialog with the current component
    def componentEdit(self, _=None):
        cmd = ComponentEdit(self.main)
        cmd.redo()

    # edit datasource action
    # \brief It opens a dialog with the current datasource
    def dsourceEdit(self, _=None):
        cmd = DataSourceEdit(self.main)
        cmd.redo()

    # apply datasource item action executed by button
    # \brief It applies the changes in the current datasource item
    #        executed by button
    def dsourceApplyButton(self):
        if self.main.updateDataSourceListItem():
            self.dsourceApply()

    # apply datasource item action
    # \brief It applies the changes in the current datasource item
    def dsourceApply(self):
        cmd = DataSourceApply(self.main)
        self.undoStack.push(cmd)

    # copy datasource item action
    # \brief It copies the  current datasource item into the clipboard
    def dsourceCopy(self):
        cmd = DataSourceCopy(self.main)
        cmd.redo()

    # cuts datasource item action
    # \brief It removes the current datasources item and copies it
    #        into the clipboard
    def dsourceCut(self):
        cmd = DataSourceCut(self.main)
        self.undoStack.push(cmd)

    # paste datasource item action
    # \brief It pastes the datasource item from the clipboard
    def dsourcePaste(self):
        cmd = DataSourcePaste(self.main)
        self.undoStack.push(cmd)


if __name__ == "__main__":
    pass
