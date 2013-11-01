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
## \file FileSlots.py
# user pool commands of GUI application

""" File slots """

from PyQt4.QtGui import  (QAction, QIcon, QKeySequence) 
from PyQt4.QtCore import (QString, SIGNAL)


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
    ComponentEdit
    )

from .ItemCommands import (
    ComponentMerge
    )


## stack with the application commands
class FileSlots(object):

    ## constructor
    # \param length maximal length of the stack
    def __init__(self, main):
        self.main = main
        self.undoStack = main.undoStack

        self.actions = {
            "actionLoad":[
                "&Load...", "componentOpen",
                QKeySequence.Open, "componentopen", "Load an existing component"],
            "actionLoadDataSource":[
                "&Load DataSource...", "dsourceOpen",
                "Ctrl+Shift+O", "dsourceopen", "Load an existing data source"],
            "actionSave":[
                "&Save", "componentSave",
                QKeySequence.Save, "componentsave", 
                "Write the component into a file"],
            "actionSaveDataSource":[
                "&Save DataSource", "dsourceSave",
                "Ctrl+Shift+S", "dsourcesave", "Write the data source into a file"],
            "actionSaveAs":[
                "Save &As...", "componentSaveAs",
                "", "componentsaveas", "Write the component into a file as ..."],
            "actionSaveDataSourceAs":[
                "Save DataSource &As...", "dsourceSaveAs",
                "", "dsourcesaveas", 
                "Write the data source  in a file as ..."],
            "actionSaveAll":[
                "Save All", "componentSaveAll",
                "", "componentsaveall", "Write all components into files"],
            "actionSaveAllDataSources":[
                "Save All DataSources", "dsourceSaveAll",
                "", "dsourcessaveall", "Write all data sources in files"],
            "actionClose":[
                "&Remove", "componentRemove",
                "Ctrl+P", "componentremove", "Close the component"],
            "actionCloseDataSource":[
                "&Remove DataSource", "dsourceRemove",
                "Ctrl+Shift+P", "dsourceremove", 
                "Close the data source"],
            "actionReloadDataSourceList":[
                "Reload DataSource List", "dsourceReloadList", 
                "", "dsourcereloadlist", "Reload the data-source list"],
            "actionReloadList":[
                "Reload List", "componentReloadList", 
                "", "componentreloadlist", "Reload the component list"],
            "actionChangeDirectory":[
                "Change Directory...", "componentChangeDirectory",
                "", "componentrechangedirectory", 
                "Change the component list directory"],
            "actionChangeDataSourceDirectory":[
                "Change DataSource Directory...", "dsourceChangeDirectory", 
                "", "dsourcerechangedirectory", 
                "Change the data-source list directory"]
            }


        



    ## open component action
    # \brief It opens component from the file
    def componentOpen(self):        
        cmd = ComponentOpen(self.main)
        cmd.execute()
        self.undoStack.push(cmd)

    ## open datasource action
    # \brief It opens datasource from the file
    def dsourceOpen(self):
        cmd = DataSourceOpen(self.main)
        cmd.execute()
        self.undoStack.push(cmd)


    ## save component action
    # \brief It saves the current component      
    def componentSave(self):
        cmd = ComponentEdit(self.main)
        cmd.execute()
        cmd = ComponentMerge(self.main)
        cmd.execute()
        self.undoStack.push(cmd)
        cmd = ComponentSave(self.main)
        cmd.execute()


    ## save component action executed by button
    # \brief It saves the current component executed by button   
    def componentSaveButton(self):
        if self.main.updateComponentListItem():
            self.componentSave()




    ## remove component action
    # \brief It removes from the component list the current component
    def componentRemove(self):
        cmd = self.pool.getCommand('componentRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## remove datasource action
    # \brief It removes the current datasource      
    def dsourceRemove(self):
        cmd = self.pool.getCommand('dsourceRemove').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

 


    ## save datasource item action
    # \brief It saves the changes in the current datasource item 
    def dsourceSave(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceSave').clone()
        cmd.execute()


    ## save datasource item action executed by button
    # \brief It saves the changes in the current datasource item executed 
    #        by button
    def dsourceSaveButton(self):
        if self.updateDataSourceListItem():
            self.dsourceSave()


    ## save component item as action
    # \brief It saves the changes in the current component item with a new name
    def componentSaveAs(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmdSA = self.pool.getCommand('componentSaveAs').clone()
        cmdSA.execute()

        cmd = self.pool.getCommand('componentChanged').clone()
        cmd.directory = cmdSA.directory
        cmd.name = cmdSA.name
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


        cmd = self.pool.getCommand('componentSave').clone()
        cmd.execute()





    ## save datasource item as action
    # \brief It saves the changes in the current datasource item with 
    #        a new name
    def dsourceSaveAs(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()

        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmdSA = self.pool.getCommand('dsourceSaveAs').clone()
        cmdSA.execute()

        cmd = self.pool.getCommand('dsourceChanged').clone()
        cmd.directory = cmdSA.directory
        cmd.name = cmdSA.name
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('dsourceSave').clone()
        cmd.execute()


    ## save all components item action
    # \brief It saves the changes in all components item
    def componentSaveAll(self):
        cmd = self.pool.getCommand('componentSaveAll').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      



    ## save all datasource item action
    # \brief It saves the changes in all datasources item
    def dsourceSaveAll(self):
        cmd = self.pool.getCommand('dsourceSaveAll').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## change component directory action
    # \brief It changes the default component directory
    def componentChangeDirectory(self):
        cmd = self.pool.getCommand('componentChangeDirectory').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## change datasource directory action
    # \brief It changes the default datasource directory
    def dsourceChangeDirectory(self):
        cmd = self.pool.getCommand('dsourceChangeDirectory').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## reload component list
    # \brief It changes the default component directory and reload components
    def componentReloadList(self):
        cmd = self.pool.getCommand('componentReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## reload datasource list
    # \brief It changes the default datasource directory and reload datasources
    def dsourceReloadList(self):
        cmd = self.pool.getCommand('dsourceReloadList').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


        

if __name__ == "__main__":   
    pass
