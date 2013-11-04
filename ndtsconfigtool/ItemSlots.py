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
## \file ItemSlots.py
# user pool commands of GUI application

""" Item slots """

from PyQt4.QtGui import  (QAction, QIcon, QKeySequence) 
from PyQt4.QtCore import (QString, SIGNAL, Qt)


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



## stack with the application commands
class ItemSlots(object):

    ## constructor
    # \param length maximal length of the stack
    def __init__(self, main):
        self.main = main
        self.undoStack = main.undoStack

        self.actions = {
        "actionNewGroupItem":[
            "New &Group Item", "componentNewGroupItem",
            "", "componentnewitem", "Add a new component group item"],
        "actionNewFieldItem":[
            "New &Field Item", "componentNewFieldItem", 
            "", "componentnewitem", "Add a new  component field item"],
        "actionNewStrategyItem":[
            "New &Strategy Item", "componentNewStrategyItem",
            "", "componentnewitem", "Add a new component strategy item"],
        "actionNewDataSourceItem":[
            "New &DataSource Item", "componentNewDataSourceItem",
            "", "componentnewitem", "Add a new component data source item"],
        "actionNewAttributeItem":[
            "New A&ttribute Item", "componentNewAttributeItem", 
            "", "componentnewitem", "Add a new component attribute item"],
        "actionNewLinkItem":[
            "New &Link Item", "componentNewLinkItem", 
            "", "componentnewitem", "Add a new  component link item"],
        "actionLoadSubComponentItem":[
            "Load SubComponent Item...", "componentLoadComponentItem", 
            "", "componentloaditem", 
            "Load an existing component part from the file"],
        "actionLoadDataSourceItem":[
            "Load DataSource Item...", "componentLoadDataSourceItem", 
            "", "componentloaditem", 
            "Load an existing data source from the file"],
        "actionAddDataSourceItem":[
            "Add DataSource Item", "componentAddDataSourceItem", 
            QKeySequence(Qt.CTRL +  Qt.Key_Plus),
            "componentadditem", "Add the data source from the list"],
        "actionLinkDataSourceItem":[
            "Link DataSource Item", "componentLinkDataSourceItem", 
            "Ctrl+L",
            "componentlinkitem", "Link the data source from the list"],
        "actionMoveUpComponentItem":[
            "&Move Up Component Item", "componentMoveUpItem", 
            "Ctrl+[", "componentsmoveupitem", "Move up the component item"],
        "actionMoveDownComponentItem":[
            "&Move Down Component Item", "componentMoveDownItem",
            "Ctrl+]", "componentsmovedownitem", "Move down the component item"],
        "actionMergeComponentItems":[
            "Merge Component Items", "componentMerge",
            "Ctrl+M", "componentmerge", "Merge the component items"],
        "actionApplyComponentItem":[
            "&Apply Component Item", "componentApplyItem",
            "Ctrl+R", "componentsapplyitem", "Apply the component item"],
        "actionClearComponentItems":[
            "Clear Component Items", "componentClear", 
            "", "componentclear", "Removes all component items"],
        "actionCutItem":[
            "C&ut Item", "cutItem", 
            QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_X),
            "cut", "Cut the item"],
        "actionCopyItem":[
            "&Copy Item", "copyItem",
            QKeySequence(Qt.CTRL + Qt.SHIFT  + Qt.Key_C),
            "copy", "Copy the item"],
        "actionPasteItem":[
            "&Paste Item", "pasteItem",
            QKeySequence(Qt.CTRL +  Qt.SHIFT  + Qt.Key_V),
            "paste", "Paste the item"],
        "actionCutComponentItem":[
            "Cut Component Item", "componentRemoveItem",
            QKeySequence(Qt.CTRL + Qt.Key_Delete),
            "cut", "Remove the component item"],
        "actionCopyComponentItem":[
            "Copy Component Item", "componentCopyItem", 
            "" ,
            "copy", "Copy the component item"],
        "actionPasteComponentItem":[
            "Paste Component Item", "componentPasteItem",
            QKeySequence(Qt.CTRL + Qt.Key_Insert),
            "paste", "Paste the component item"],



        }



    ## copy component item action
    # \brief It copies the  current component item into the clipboard
    def componentCopyItem(self):
        cmd = self.pool.getCommand('componentCopyItem').clone()
        cmd.redo()

    ## remove component item action
    # \brief It removes the current component item and copies it 
    #        into the clipboard
    def componentRemoveItem(self):
        cmd = self.pool.getCommand('componentRemoveItem').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## paste component item action
    # \brief It pastes the component item from the clipboard
    def componentPasteItem(self):
        cmd = self.pool.getCommand('componentPasteItem').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        


    ## copy item action
    # \brief It copies the current item into the clipboard
    def copyItem(self):
        cmd = self.pool.getCommand('copyItem').clone()
        if self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None
            return
        cmd.redo()



    ## cuts item action
    # \brief It removes the current item and copies it into the clipboard
    def cutItem(self):
        cmd = self.pool.getCommand('cutItem').clone()
        if self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None

            return
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## paste item action
    # \brief It pastes the item from the clipboard
    def pasteItem(self):
        cmd = self.pool.getCommand('pasteItem').clone()
        if self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd.type = "component"
        elif self.ui.mdi.activeSubWindow() and isinstance(
            self.ui.mdi.activeSubWindow().widget(), CommonDataSourceDlg):
            cmd.type = "datasource"
        else:
            QMessageBox.warning(self, "Item not selected", 
                                "Please select one of the items")            
            cmd.type = None
            return
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      






    # Item 








    ## new group component item action
    # \brief It adds a new group component item
    def componentNewGroupItem(self):
        if isinstance(self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewGroupItem').clone()
            cmd.itemName = 'group' 
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewStrategyItem').clone()
            cmd.itemName = 'strategy' 
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewFieldItem').clone()
            cmd.itemName = 'field' 
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewAttributeItem').clone()
            cmd.itemName = 'attribute' 
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentNewLinkItem').clone()
            cmd.itemName = 'link' 
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(),
                      ComponentDlg):
            cmd = self.pool.getCommand('componentNewDataSourceItem').clone()
            cmd.itemName = 'datasource' 
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(), ComponentDlg):
            cmd = self.pool.getCommand('componentLoadComponentItem').clone()
            cmd.redo()
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
        if isinstance(self.ui.mdi.activeSubWindow().widget(),
                      ComponentDlg):
            cmd = self.pool.getCommand('componentLoadDataSourceItem').clone()
            cmd.redo()
            self.cmdStack.append(cmd)
            self.pool.setDisabled("undo", False, "Undo: ", 
                                  self.cmdStack.getUndoName() )
            self.pool.setDisabled("redo", True, "Can't Redo")      
        else:
            QMessageBox.warning(self, "Component not created", 
                                "Please edit one of the components")            



    ## add datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentAddDataSourceItem(self):
#        cmd = self.pool.getCommand('dsourceEdit').clone()
#        cmd.redo()
        cmd = self.pool.getCommand('componentAddDataSourceItem').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## link datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentLinkDataSourceItem(self):
        cmd = self.pool.getCommand('componentLinkDataSourceItem').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


        
    ## link datasource component item action
    # \brief It adds the current datasource item into component tree
    def componentLinkDataSourceItemButton(self):
        if self.updateComponentListItem():
            self.componentLinkDataSourceItem()



    ## move-up component item action
    # \brief It moves the current component item up
    def componentMoveUpItem(self):
        cmd = self.pool.getCommand('componentMoveUpItem').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      


    ## move-down component item action
    # \brief It moves the current component item down
    def componentMoveDownItem(self):
        cmd = self.pool.getCommand('componentMoveDownItem').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Undo")      





    ## apply component item action
    # \brief It applies the changes in the current component item 
    def componentApplyItem(self):
        cmd = self.pool.getCommand('componentApplyItem').clone()
        cmd.redo()
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








    ## merge component action
    # \brief It merges the current component
    def componentMerge(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.redo()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## clear component action
    # \brief It clears the current component      
    def componentClear(self):
        cmd = self.pool.getCommand('componentClear').clone()
        cmd.redo()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      





if __name__ == "__main__":   
    pass
