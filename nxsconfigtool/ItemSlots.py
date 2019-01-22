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
# \file ItemSlots.py
# user pool commands of GUI application

""" Item slots """

from PyQt5.QtGui import (QKeySequence)
from PyQt5.QtWidgets import (QMessageBox)
from PyQt5.QtCore import (Qt)


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

from .EditCommands import (
    ComponentEdit
)

from .DataSourceDlg import CommonDataSourceDlg
from .ComponentDlg import ComponentDlg


# stack with the application commands
class ItemSlots(object):

    # constructor
    # \param main the main window dialog
    def __init__(self, main):
        # main window
        self.main = main
        # command stack
        self.undoStack = main.undoStack

        # action data
        self.actions = {
            "actionNewGroupItem": [
                "Add &Group Item", "componentNewGroupItem",
                "", "componentnewitem", "Add a new component group item"],
            "actionNewFieldItem": [
                "Add &Field Item", "componentNewFieldItem",
                "", "componentnewitem", "Add a new  component field item"],
            "actionNewStrategyItem": [
                "Add &Strategy Item", "componentNewStrategyItem",
                "", "componentnewitem", "Add a new component strategy item"],
            "actionNewDataSourceItem": [
                "Add &DataSource Item", "componentNewDataSourceItem",
                "", "componentnewitem",
                "Add a new component data source item"],
            "actionNewAttributeItem": [
                "Add A&ttribute Item", "componentNewAttributeItem",
                "", "componentnewitem", "Add a new component attribute item"],
            "actionNewLinkItem": [
                "Add &Link Item", "componentNewLinkItem",
                "", "componentnewitem", "Add a new  component link item"],
            "actionLoadSubComponentItem": [
                "Load SubComponent Item...", "componentLoadComponentItem",
                "", "componentloaditem",
                "Load an existing component part from the file"],
            "actionLoadDataSourceItem": [
                "Load DataSource Item...", "componentLoadDataSourceItem",
                "", "componentloaditem",
                "Load an existing data source from the file"],
            "actionAddDataSourceItem": [
                "Append DataSource Item", "componentAddDataSourceItem",
                QKeySequence(Qt.CTRL + Qt.Key_Plus),
                "componentadditem", "Append the data source from the list"],
            "actionLinkDataSourceItem": [
                "Link DataSource Item", "componentLinkDataSourceItem",
                "Ctrl+L",
                "componentlinkitem", "Link the data source from the list"],
            "actionMoveUpComponentItem": [
                "&Move Up Component Item", "componentMoveUpItem",
                "Ctrl+[", "componentsmoveupitem",
                "Move up the component item"],
            "actionMoveDownComponentItem": [
                "&Move Down Component Item", "componentMoveDownItem",
                "Ctrl+]", "componentsmovedownitem",
                "Move down the component item"],
            "actionMergeComponentItems": [
                "Merge Component Items", "componentMerge",
                "Ctrl+M", "componentmerge", "Merge the component items"],
            "actionApplyComponentItem": [
                "&Apply Component Item", "componentApplyItem",
                "Ctrl+R", "componentsapplyitem", "Apply the component item"],
            "actionClearComponentItems": [
                "Clear Component Items", "componentClear",
                "", "componentclear", "Removes all component items"],
            "actionCutItem": [
                "C&ut Item", "cutItem",
                QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_X),
                "cut", "Cut the item"],
            "actionCopyItem": [
                "&Copy Item", "copyItem",
                QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_C),
                "copy", "Copy the item"],
            "actionPasteItem": [
                "&Paste Item", "pasteItem",
                QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_V),
                "paste", "Paste the item"],
            "actionCutComponentItem": [
                "Cut Component Item", "componentRemoveItem",
                QKeySequence(Qt.CTRL + Qt.Key_Delete),
                "cut", "Remove the component item"],
            "actionCopyComponentItem": [
                "Copy Component Item", "componentCopyItem", "",
                "copy", "Copy the component item"],
            "actionPasteComponentItem": [
                "Paste Component Item", "componentPasteItem",
                QKeySequence(Qt.CTRL + Qt.Key_Insert),
                "paste", "Paste the component item"],
        }

    # copy component item action
    # \brief It copies the  current component item into the clipboard
    def componentCopyItem(self):
        cmd = ComponentCopyItem(self.main)
        cmd.redo()

    # remove component item action
    # \brief It removes the current component item and copies it
    #        into the clipboard
    def componentRemoveItem(self):
        cmd = ComponentRemoveItem(self.main)
        self.undoStack.push(cmd)

    # paste component item action
    # \brief It pastes the component item from the clipboard
    def componentPasteItem(self):
        cmd = ComponentPasteItem(self.main)
        self.undoStack.push(cmd)

    # copy item action
    # \brief It copies the current item into the clipboard
    def copyItem(self):
        cmd = CopyItem(self.main)
        if self.main.ui.mdi.activeSubWindow() and isinstance(
                self.main.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.main.ui.mdi.activeSubWindow() and isinstance(
                self.main.ui.mdi.activeSubWindow().widget(),
                CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self.main, "Item not selected",
                                "Please select one of the items")
            cmd.type = None
            return
        cmd.redo()

    # cuts item action
    # \brief It removes the current item and copies it into the clipboard
    def cutItem(self):
        cmd = CutItem(self.main)
        if self.main.ui.mdi.activeSubWindow() and isinstance(
                self.main.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.main.ui.mdi.activeSubWindow() and isinstance(
                self.main.ui.mdi.activeSubWindow().widget(),
                CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self.main, "Item not selected",
                                "Please select one of the items")
            cmd.type = None

            return
        self.undoStack.push(cmd)

    # paste item action
    # \brief It pastes the item from the clipboard
    def pasteItem(self):
        cmd = PasteItem(self.main)
        if self.main.ui.mdi.activeSubWindow() and isinstance(
                self.main.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.main.ui.mdi.activeSubWindow() and isinstance(
                self.main.ui.mdi.activeSubWindow().widget(),
                CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self.main, "Item not selected",
                                "Please select one of the items")
            cmd.type = None
            return
        self.undoStack.push(cmd)

    # new group component item action
    # \brief It adds a new group component item
    def componentNewGroupItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentNewItem(self.main)
            cmd.itemName = 'group'
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # new group component item action
    # \brief It adds a new group component item
    def componentNewStrategyItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentNewItem(self.main)
            cmd.itemName = 'strategy'
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # new field component item action
    # \brief It adds a new field component item
    def componentNewFieldItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentNewItem(self.main)
            cmd.itemName = 'field'
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # new attribute component item action
    # \brief It adds a new attribute component item
    def componentNewAttributeItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentNewItem(self.main)
            cmd.itemName = 'attribute'
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # new link component item action
    # \brief It adds a new link component item
    def componentNewLinkItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentNewItem(self.main)
            cmd.itemName = 'link'
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # new datasource component item action
    # \brief It adds a new datasource component item
    def componentNewDataSourceItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentNewItem(self.main)
            cmd.itemName = 'datasource'
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # load sub-component item action
    # \brief It loads a sub-component item from a file
    def componentLoadComponentItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentLoadComponentItem(self.main)
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # load datasource component item action
    # \brief It loads a datasource component item from a file
    def componentLoadDataSourceItem(self):
        if hasattr(self.main.ui.mdi.activeSubWindow(), 'widget') and \
                isinstance(self.main.ui.mdi.activeSubWindow().widget(),
                           ComponentDlg):
            cmd = ComponentLoadDataSourceItem(self.main)
            self.undoStack.push(cmd)
        else:
            QMessageBox.warning(self.main, "Component not created",
                                "Please edit one of the components")

    # add datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentAddDataSourceItem(self):
        cmd = ComponentAddDataSourceItem(self.main)
        self.undoStack.push(cmd)

    # link datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentLinkDataSourceItem(self):
        cmd = ComponentLinkDataSourceItem(self.main)
        self.undoStack.push(cmd)

    # link datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentLinkDataSourceItemButton(self):
        if self.main.updateComponentListItem():
            self.componentLinkDataSourceItem()

    # move-up component item action
    # \brief It moves the current component item up
    def componentMoveUpItem(self):
        cmd = ComponentMoveUpItem(self.main)
        self.undoStack.push(cmd)

    # move-down component item action
    # \brief It moves the current component item down
    def componentMoveDownItem(self):
        cmd = ComponentMoveDownItem(self.main)
        self.undoStack.push(cmd)

    # apply component item action
    # \brief It applies the changes in the current component item
    def componentApplyItem(self):
        cmd = ComponentApplyItem(self.main)
        self.undoStack.push(cmd)

    # apply component item action executed by button
    # \brief It applies the changes in the current component item
    #        executed by button
    def componentApplyItemButton(self):
        if self.main.updateComponentListItem():
            self.componentApplyItem()

    # merge component action
    # \brief It merges the current component
    def componentMerge(self):
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentMerge(self.main)
        self.undoStack.push(cmd)

    # clear component action
    # \brief It clears the current component
    def componentClear(self):
        cmd = ComponentClear(self.main)
        self.undoStack.push(cmd)


if __name__ == "__main__":
    pass
