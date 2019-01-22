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
# \file FileSlots.py
# user pool commands of GUI application

""" File slots """

from PyQt5.QtGui import QKeySequence

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

from .EditCommands import (
    ComponentEdit,
    DataSourceEdit,
    DataSourceApply
)

from .ItemCommands import (
    ComponentApplyItem,
    ComponentMerge
)

from .ListCommands import (
    ComponentListChanged,
    DataSourceListChanged
)


# stack with the application commands
class FileSlots(object):

    # constructor
    # \param main the main window dialog
    def __init__(self, main):
        # main window
        self.main = main
        # command stack
        self.undoStack = main.undoStack

        # action data
        self.actions = {
            "actionLoad": [
                "&Load...", "componentOpen",
                QKeySequence.Open, "componentopen",
                "Load an existing component"],
            "actionLoadDataSource": [
                "&Load DataSource...", "dsourceOpen",
                "Ctrl+Shift+O", "dsourceopen",
                "Load an existing data source"],
            "actionSave": [
                "&Save", "componentSave",
                QKeySequence.Save, "componentsave",
                "Write the component into a file"],
            "actionSaveDataSource": [
                "&Save DataSource", "dsourceSave",
                "Ctrl+Shift+S", "dsourcesave",
                "Write the data source into a file"],
            "actionSaveAs": [
                "Save &As...", "componentSaveAs",
                "", "componentsaveas",
                "Write the component into a file as ..."],
            "actionSaveDataSourceAs": [
                "Save DataSource &As...", "dsourceSaveAs",
                "", "dsourcesaveas",
                "Write the data source  in a file as ..."],
            "actionSaveAll": [
                "Save All", "componentSaveAll",
                "", "componentsaveall", "Write all components into files"],
            "actionSaveAllDataSources": [
                "Save All DataSources", "dsourceSaveAll",
                "", "dsourcessaveall", "Write all data sources in files"],
            "actionReloadDataSourceList": [
                "Reload DataSource List", "dsourceReloadList",
                "", "dsourcereloadlist", "Reload the data-source list"],
            "actionReloadList": [
                "Reload List", "componentReloadList",
                "", "componentreloadlist", "Reload the component list"],
            "actionChangeDirectory": [
                "Change Directory...", "componentChangeDirectory",
                "", "componentrechangedirectory",
                "Change the component list directory"],
            "actionChangeDataSourceDirectory": [
                "Change DataSource Directory...", "dsourceChangeDirectory",
                "", "dsourcerechangedirectory",
                "Change the data-source list directory"]
        }

    # open component action
    # \brief It opens component from the file
    def componentOpen(self):
        cmd = ComponentOpen(self.main)
        self.undoStack.push(cmd)

    # open datasource action
    # \brief It opens datasource from the file
    def dsourceOpen(self):
        cmd = DataSourceOpen(self.main)
        self.undoStack.push(cmd)

    # save component action
    # \brief It saves the current component
    def componentSave(self, focus=True):
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentMerge(self.main)
        self.undoStack.push(cmd)
        cmd = ComponentSave(self.main)
        cmd.redo()
        if focus:
            self.main.componentList.setItemFocus()

    # save component action executed by button
    # \brief It saves the current component executed by button
    def componentSaveButton(self):
        if self.main.updateComponentListItem():
            cmd = ComponentApplyItem(self.main)
            self.undoStack.push(cmd)
            self.componentSave(False)

    # save datasource item action
    # \brief It saves the changes in the current datasource item
    def dsourceSave(self, focus=True):
        cmd = DataSourceEdit(self.main)
        cmd.redo()
        cmd = DataSourceApply(self.main)
        self.undoStack.push(cmd)
        cmd = DataSourceSave(self.main)
        cmd.redo()
        if focus:
            self.main.sourceList.setItemFocus()

    # save datasource item action executed by button
    # \brief It saves the changes in the current datasource item executed
    #        by button
    def dsourceSaveButton(self):
        if self.main.updateDataSourceListItem():
            self.dsourceSave(False)

    # save component item as action
    # \brief It saves the changes in the current component item with a new name
    def componentSaveAs(self):
        cmd = ComponentApplyItem(self.main)
        self.undoStack.push(cmd)
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentMerge(self.main)
        self.undoStack.push(cmd)
        cmdSA = ComponentSaveAs(self.main)
        cmdSA.redo()

        cmd = ComponentListChanged(self.main)
        cmd.directory = cmdSA.directory
        cmd.name = cmdSA.name
        self.undoStack.push(cmd)
        cmd = ComponentSave(self.main)
        cmd.redo()

    # save datasource item as action
    # \brief It saves the changes in the current datasource item with
    #        a new name
    def dsourceSaveAs(self):
        cmd = DataSourceEdit(self.main)
        cmd.redo()
        cmd = DataSourceApply(self.main)
        self.undoStack.push(cmd)
        cmdSA = DataSourceSaveAs(self.main)
        cmdSA.redo()

        cmd = DataSourceListChanged(self.main)
        cmd.directory = cmdSA.directory
        cmd.name = cmdSA.name
        self.undoStack.push(cmd)
        cmd = DataSourceSave(self.main)
        cmd.redo()

    # save all components item action
    # \brief It saves the changes in all components item
    def componentSaveAll(self):
        cmd = ComponentSaveAll(self.main)
        cmd.redo()
        self.undoStack.clear()

    # save all datasource item action
    # \brief It saves the changes in all datasources item
    def dsourceSaveAll(self):
        cmd = DataSourceSaveAll(self.main)
        cmd.redo()
        self.undoStack.clear()

    # change component directory action
    # \brief It changes the default component directory
    def componentChangeDirectory(self):
        cmd = ComponentChangeDirectory(self.main)
        cmd.redo()
        self.undoStack.clear()

    # change datasource directory action
    # \brief It changes the default datasource directory
    def dsourceChangeDirectory(self):
        cmd = DataSourceChangeDirectory(self.main)
        cmd.redo()
        self.undoStack.clear()

    # reload component list
    # \brief It changes the default component directory and reload components
    def componentReloadList(self):
        cmd = ComponentReloadList(self.main)
        cmd.redo()
        self.undoStack.clear()

    # reload datasource list
    # \brief It changes the default datasource directory and reload datasources
    def dsourceReloadList(self):
        cmd = DataSourceReloadList(self.main)
        cmd.redo()
        self.undoStack.clear()


if __name__ == "__main__":
    pass
