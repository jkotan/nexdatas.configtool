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
## \file Command.py
# user commands of GUI application

""" Component Designer commands """

from PyQt4.QtGui import QMessageBox, QUndoCommand
from PyQt4.QtCore import SIGNAL

from . import DataSource
from .Component import Component
from .ComponentModel import ComponentModel
from .EditCommands import (DataSourceCut, DataSourceCopy, DataSourcePaste)


## Abstract Command which helps in defing commands related to 
#  Component item operations
class ComponentItemCommand(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._cp = None
        self._oldstate = None
        self._index = None
        self._newstate = None
        self._subwindow = None

    ## helps to construct the execute component item command as a pre-executor
    # \brief It stores the old states of the current component
    def preExecute(self):
        if self._cp is None:
            self._cp = self.receiver.main.componentList.currentListElement()
        if self._cp is not None:
            if self._oldstate is None and hasattr(self._cp, "instance") \
                    and hasattr(self._cp.instance, "setState"):
                self._oldstate = self._cp.instance.getState() 
                self._index = self._cp.instance.currentIndex()

            else:
                QMessageBox.warning(
                    self.receiver.main, "Component not created", 
                    "Please edit one of the components")
                
        else:
            QMessageBox.warning(
                self.receiver.main, "Component not selected", 
                "Please select one of the components")

    
    ## helps to construct the execute component item command as a post-executor
    # \brief It stores the new states of the current component
    def postExecute(self):    
        if self._cp is not None:
            if self._cp.instance is None:
                self._cp.instance = Component()
                self._cp.instance.id = self._cp.id
                self._cp.instance.directory = \
                    self.receiver.main.componentList.directory
                self._cp.instance.name = \
                    self.receiver.main.componentList.elements[
                    self._cp.id].name

            if self._newstate is None and hasattr(
                self._cp.instance, "getState"):
                self._newstate = self._cp.instance.getState() 
            else:
                if hasattr(
                    self.receiver.main.componentList.elements[
                        self._cp.id].instance, "setState"): 
                    self.receiver.main.componentList.elements[
                        self._cp.id].instance.setState(self._newstate)



                subwindow = self.receiver.main.subWindow(
                    self._cp.instance, 
                    self.receiver.main.ui.mdi.subWindowList())

                if subwindow:
                    self.receiver.main.ui.mdi.setActiveSubWindow(subwindow) 
                    self._cp.instance.reconnectSaveAction()
                else:    
                    self._cp.instance.createGUI()

                    self._cp.instance.addContextMenu(
                        self.receiver.main.contextMenuActions)
                    if self._cp.instance.isDirty():
                        self._cp.instance.dialog.setWindowTitle(
                            "%s [Component]*" % self._cp.name)
                    else:
                        self._cp.instance.dialog.setWindowTitle(
                            "%s [Component]" % self._cp.name)
                     
                    self._cp.instance.reconnectSaveAction()
                    self._subwindow = self.receiver.main.ui.mdi.addSubWindow(
                        self._cp.instance.dialog)
                    self._subwindow.resize(680, 560)

                    if hasattr(self._cp.instance.dialog, "show"):
                        self._cp.instance.dialog.show()

                if hasattr(self._cp.instance, "connectExternalActions"):     
                    self._cp.instance.connectExternalActions(
                        **self.receiver.main.externalCPActions) 


        if hasattr(self._cp, "id"):
            self.receiver.main.componentList.populateElements(self._cp.id)
        else:
            self.receiver.main.componentList.populateElements()

        
    ## executes the command
    # \brief It execute pre- and post- executors
    def redo(self):
        if self._cp is None:
            self.preExecute()
    
        self.postExecute()
        print "EXEC componentItemCommand"


    ## helps to construct the unexecute component item command 
    # \brief It changes back the states of the current component 
    #        to the old state
    def undo(self):
        if self._cp is not None and self._oldstate is not None:
            self.receiver.main.componentList.elements[
                self._cp.id].instance.setState(self._oldstate)
            

            subwindow = self.receiver.main.subWindow(
                self._cp.instance, self.receiver.main.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.main.ui.mdi.setActiveSubWindow(subwindow)
            else:    
                if self._cp.instance is None:
                    self._cp.instance = Component()
                    self._cp.instance.id = self._cp.id
                    self._cp.instance.directory = \
                        self.receiver.main.componentList.directory
                    self._cp.instance.name = \
                        self.receiver.main.componentList.elements[
                        self._cp.id].name
                if not self._cp.instance.dialog:
                    self._cp.instance.createGUI()
                self._subwindow = self.receiver.main.ui.mdi.addSubWindow(
                    self._cp.instance.dialog)
                self._subwindow.resize(680, 560)

                self._cp.instance.dialog.show()
        self._cp.instance.reconnectSaveAction()
        if hasattr(self._cp, "id"):
            self.receiver.main.componentList.populateElements(self._cp.id)
        else:
            self.receiver.main.componentList.populateElements()

        print "UNDO componentItemComponent"





## Command which clears the whole current component
class ComponentClear(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)


    ## executes the command
    # \brief It clears the whole current component
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:                
                if QMessageBox.question(
                    self.receiver.main, "Component - Clear",
                    "Clear the component: %s ".encode() %  (self._cp.name),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes ) == QMessageBox.No :
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    return


                if hasattr(self._cp, "instance"):
                    if self._cp.instance in self.receiver.main.ui.mdi\
                            .subWindowList():
                        self.receiver.main.ui.mdi.setActiveSubWindow(
                            self._cp.instance)
                    self._cp.instance.createHeader()            
                
                    newModel = ComponentModel(
                        self._cp.instance.document, 
                        self._cp.instance.getAttrFlag())
                    self._cp.instance.view.setModel(newModel)
                    self._cp.instance.connectView()

                    if hasattr(self._cp.instance, 
                               "connectExternalActions"):     
                        self._cp.instance.connectExternalActions(
                            **self.receiver.main.externalCPActions) 


        self.postExecute()
        print "EXEC componentClear"






## Command which loads sub-components into the current component tree 
#  from the file
class ComponentLoadComponentItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        ## 
        self._itemName = ""        
        
    ## executes the command
    # \brief It loads sub-components into the current component 
    #        tree from the file
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None and self._cp.instance.view \
                        and self._cp.instance.view.model():
                    if hasattr(self._cp.instance, "loadComponentItem"):
                        if not self._cp.instance.loadComponentItem(
                            self._itemName):
                            QMessageBox.warning(
                                self.receiver.main, "SubComponent not loaded", 
                                "Please ensure that you have selected "\
                                    "the proper items")
                else:
                    QMessageBox.warning(
                        self.receiver.main, "Component item not selected", 
                        "Please select one of the component items")            
                        
        self.postExecute()
        print "EXEC componentLoadcomponentItem"





## Command which moves the current component item into the clipboard
class ComponentRemoveItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)

        
    ## executes the command
    # \brief It moves the current component item into the clipboard
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None:
                    if hasattr(self._cp.instance, "removeSelectedItem"):
                        if not self._cp.instance.removeSelectedItem():
                            QMessageBox.warning(
                                self.receiver.main, 
                                "Cutting item not possible", 
                                "Please select another tree item") 
        self.postExecute()
        print "EXEC componentRemoveItem"




## Command which copies the current component item into the clipboard
class ComponentCopyItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)

        
    ## executes the command
    # \brief It copies the current component item into the clipboard
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None:
                    if hasattr(self._cp.instance, "copySelectedItem"):
                        if not self._cp.instance.copySelectedItem():
                            QMessageBox.warning(
                                self.receiver.main, 
                                "Copying item not possible", 
                                "Please select another tree item") 
        self.postExecute()
        print "EXEC componentCopyItem"




## Command which pastes the component item from the clipboard into 
#  the current component tree
class ComponentPasteItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)

        
    ## executes the command
    # \brief It pastes the component item from the clipboard into 
    #        the current component tree
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None:
                    if hasattr(self._cp.instance, "pasteItem"):
                        if not self._cp.instance.pasteItem():
                            QMessageBox.warning(
                                self.receiver.main, 
                                "Pasting item not possible", 
                                "Please select another tree item") 
        self.postExecute()
        print "EXEC componentPasteItem"







## Command which moves the current, i.e. datasource or component item, 
#  into the clipboard
class CutItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        ## type of the cutting item with values: component of datasource
        self.type = None

        self._ds = DataSourceCut(receiver, parent)
        self._cp = ComponentRemoveItem(receiver, parent)

    ## executes the command
    # \brief It moves the current, i.e. datasource or component item, 
    #        into the clipboard
    def redo(self):
        if self.type == 'component':
            self._cp.redo()
        elif self.type == 'datasource':
            self._ds.redo()

    ## unexecutes the command
    # \brief It adds back the current, i.e. datasource or component item
    def undo(self):
        if self.type == 'component':
            self._cp.undo()
        elif self.type == 'datasource':
            self._ds.undo()
        








## Command which copies the current item, i.e. datasource or component item, 
#  into the clipboard
class CopyItem(ComponentItemCommand):


    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        ## type of the coping item with values: component of datasource
        self.type = None

        self._ds = DataSourceCopy(receiver, parent)
        self._cp = ComponentCopyItem(receiver, parent)


    ## executes the command
    # \brief It copies the current item, i.e. datasource or component item, 
    #        into the clipboard
    def redo(self):
        if self.type == 'component':
            self._cp.redo()
        elif self.type == 'datasource':
            self._ds.redo()


    ## unexecutes the command
    # \brief It unexecutes copy commands for datasources or components
    def undo(self):
        if self.type == 'component':
            self._cp.undo()
        elif self.type == 'datasource':
            self._ds.undo()
        



## Command which pastes the current item from the clipboard 
#  into the current dialog, i.e. the current datasource or 
#  the current component item tree
class PasteItem(QUndoCommand):


    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver 
        self.type = None

        self._ds = DataSourcePaste(receiver, parent)
        self._cp = ComponentPasteItem(receiver, parent)

    ## executes the command
    # \brief It pastes the current item from the clipboard into 
    #        the current dialog, i.e. the current datasource or 
    #        the current component item tree
    def redo(self):
        if self.type == 'component':
            self._cp.redo()
        elif self.type == 'datasource':
            self._ds.redo()

    ## unexecutes the command
    # \brief It unexecutes paste commands for datasources or components
    def undo(self):
        if self.type == 'component':
            self._cp.undo()
        elif self.type == 'datasource':
            self._ds.undo()
        



## Command which merges the current component
class ComponentMerge(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        
    ## executes the command
    # \brief It merges the current component
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:                
                if hasattr(self._cp.instance, "merge"):
                    self._cp.instance.merge()
        
        self.postExecute()
        print "EXEC componentMerge"






## Command which creates a new item in the current component tree
class ComponentNewItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        ## name of the new component item
        self.itemName = ""
        self._index = None
        self._childIndex = None
        self._child = None
                    

    ## executes the command
    # \brief It creates a new item in the current component tree
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is None:                
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not selected", 
                        "Please select one of the component Items")            
                if hasattr(self._cp.instance, "addItem"):
                    self._child = self._cp.instance.addItem(self.itemName)
                    if self._child:
                        self._index = self._cp.instance.view.currentIndex()
                            
                        if  self._index.column() != 0 \
                                and self._index.row() is not None:
                            
                            self._index = self._cp.instance.view.model().index(
                                self._index.row(), 0, self._index.parent())
                        row = self._cp.instance.dialog.getWidgetNodeRow(
                            self._child)
                        if row is not None:
                            self._childIndex = \
                                self._cp.instance.view.model().index(
                                row, 0, self._index)
                            self._cp.instance.view.setCurrentIndex(
                                self._childIndex)
                            self._cp.instance.tagClicked(self._childIndex)
                    else:
                        QMessageBox.warning(
                            self.receiver.main, 
                            "Creating the %s Item not possible" \
                                % self.itemName, 
                            "Please select another tree or new item ")
            if self._child and self._index.isValid():
                if self._index.isValid():
                    finalIndex = self._cp.instance.view.model().index(
                        self._index.parent().row(), 2, 
                        self._index.parent().parent())
                else:
                    finalIndex = self._cp.instance.view.model().index(
                        0, 2, self._index.parent().parent())
                    
                self._cp.instance.view.model().emit(
                    SIGNAL("dataChanged(QModelIndex,QModelIndex)"), 
                    self._index, self._index)
                self._cp.instance.view.model().emit(
                    SIGNAL("dataChanged(QModelIndex,QModelIndex)"), 
                    finalIndex, self._childIndex)

        self.postExecute()
        print "EXEC componentNewItem"





## Command which loads a datasource from a file into the current component tree
class ComponentLoadDataSourceItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        self._cp = None
        ## name of the new datasource item
        self.itemName = ""
        

    ## executes the command
    # \brief It loads a datasource from a file into the current component tree
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None and self._cp.instance.view \
                        and  self._cp.instance.view.model():
                    if hasattr(self._cp.instance, "loadDataSourceItem"):
                        if not self._cp.instance.loadDataSourceItem(
                            self.itemName):
                            QMessageBox.warning(
                                self.receiver.main, "DataSource not loaded", 
                                "Please ensure that you have selected "\
                                    "the proper items")
                else:
                    QMessageBox.warning(
                        self.receiver.main, "Component item not selected", 
                        "Please select one of the component items")            
                    
                        
        self.postExecute()
        print "EXEC componentMerge"

        



## Command which adds the current datasource into the current component tree
class ComponentAddDataSourceItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        
        
    ## executes the command
    # \brief It adds the current datasource into the current component tree
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is None or self._cp.instance.view is None \
                        or self._cp.instance.view.model() is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not created", 
                        "Please edit one of the component Items")            
                    return

                ds = self.receiver.main.sourceList.currentListElement()
                if ds is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "DataSource not selected", 
                        "Please select one of the datasources")            
                    return

                if ds.instance is None:
                    dsEdit = DataSource.DataSource()
                    dsEdit.id = ds.id
                    dsEdit.directory = self.receiver.main.sourceList.directory
                    dsEdit.name = self.receiver.main.sourceList.elements[
                        ds.id].name
                    ds.instance = dsEdit 
                else:
                    dsEdit = ds.instance 


                if hasattr(dsEdit, "connectExternalActions"):     
                    dsEdit.connectExternalActions(
                        **self.receiver.main.externalDSActions)
                
                if not hasattr(ds.instance, "createNodes"):
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not created", 
                        "Please edit one of the component Items")            
                    return

                dsNode = ds.instance.createNodes()
                if dsNode is None:
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, 
                        "Datasource node cannot be created", 
                        "Problem in importing the external node")            
                    return
        
                if not hasattr(self._cp.instance, "addDataSourceItem"):
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not created", 
                        "Please edit one of the component Items")            
                    return
                if not self._cp.instance.addDataSourceItem(dsNode):
                    QMessageBox.warning(
                        self.receiver.main, 
                        "Adding the datasource item not possible", 
                        "Please ensure that you have selected the proper items")



        self.postExecute()
        print "EXEC componentAddDataSourceItem"



## Command which links the current datasource into the current component tree
class ComponentLinkDataSourceItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        
        
    ## executes the command
    # \brief It links the current datasource into the current component tree
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is None \
                        or self._cp.instance.view is None \
                        or self._cp.instance.view.model() is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not created", 
                        "Please edit one of the component Items")
                    return

                ds = self.receiver.main.sourceList.currentListElement()
                if ds is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "DataSource not selected", 
                        "Please select one of the datasources")
                    return

                if ds.instance is None:
                    dsEdit = DataSource.DataSource()
                    dsEdit.id = ds.id
                    dsEdit.directory = self.receiver.main.sourceList.directory
                    dsEdit.name = self.receiver.main.sourceList.elements[
                        ds.id].name
                    ds.instance = dsEdit 
                else:
                    dsEdit = ds.instance 

                if not hasattr(ds.instance, "dataSourceName") \
                        or not ds.instance.dataSourceName:
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "DataSource wihtout name", 
                        "Please define datasource name")
                    return

                    

                if hasattr(dsEdit, "connectExternalActions"):     
                    dsEdit.connectExternalActions(
                        **self.receiver.main.externalDSActions)
                
                if not hasattr(ds.instance, "createNodes"):
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not created", 
                        "Please edit one of the component Items")
                    return

        
                if not hasattr(self._cp.instance, "linkDataSourceItem"):
                    self._cp = None
                    QMessageBox.warning(
                        self.receiver.main, "Component Item not created", 
                        "Please edit one of the component Items")            
                    return
                if not self._cp.instance.linkDataSourceItem(
                    dsEdit.dataSourceName):
                    QMessageBox.warning(
                        self.receiver.main, 
                        "Linking the datasource item not possible", 
                        "Please ensure that you have selected "\
                            "the proper items")            

        self.postExecute()
        print "EXEC componentLinkDataSourceItem"



## Command which applies the changes from the form for 
#  the current component item
class ComponentApplyItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        
        
    ## executes the command
    # \brief It applies the changes from the form for 
    #        the current component item
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if hasattr(self._cp, "instance") \
                        and hasattr(self._cp.instance, "applyItem"):

                    if not self._cp.instance.applyItem():
                        QMessageBox.warning(
                            self.receiver.main, "Applying item not possible", 
                            "Please select another tree item") 


        self.postExecute()
        print "EXEC componentApplyItem"







## Command which move the current component item up
class ComponentMoveUpItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        self._index = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current component item
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if hasattr(self._cp, "instance") and hasattr(
                    self._cp.instance, "moveUpItem"):

                    if self._cp.instance.moveUpItem() is None:
                        QMessageBox.warning(
                            self.receiver.main, "Moving item up not possible", 
                            "Please select another tree item") 


        self.postExecute()

            
        print "EXEC componentMoveUpItem"







## Command which move the current component item down
class ComponentMoveDownItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        ComponentItemCommand.__init__(self, receiver, parent)
        self._index = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current component item
    def redo(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if hasattr(self._cp, "instance") \
                        and hasattr(self._cp.instance, "moveDownItem"):

                    if self._cp.instance.moveDownItem() is None:
                        QMessageBox.warning(
                            self.receiver.main, 
                            "Moving item down not possible", 
                            "Please select another tree item") 

        self.postExecute()
        print "EXEC componentMoveDownItem"




if __name__ == "__main__":
    pass

