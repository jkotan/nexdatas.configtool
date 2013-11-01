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
## \file ServerSlots.py
# user pool commands of GUI application

""" Server slots """

from PyQt4.QtGui import  (QAction, QIcon, QKeySequence) 
from PyQt4.QtCore import (QString, SIGNAL, Qt)

from .ServerCommands import (
    ServerConnect,
    ServerFetchComponents,
    ServerStoreComponent,
    ServerStoreAllComponents,
    ServerDeleteComponent,
    ServerSetMandatoryComponent,
    ServerGetMandatoryComponents,
    ServerUnsetMandatoryComponent,
    ServerFetchDataSources,
    ServerStoreDataSource,
    ServerStoreAllDataSources,
    ServerDeleteDataSource,
    ServerClose)



## stack with the application commands
class ServerSlots(object):

    ## constructor
    # \param length maximal length of the stack
    def __init__(self, main):
        self.main = main
        self.undoStack = main.undoStack

        self.actions = {
        "actionConnectServer":[
            "&Connect ...", "serverConnect", 
            "Ctrl+T", "serverconnect", 
            "Connect to the configuration server"],
        "actionFetchComponentsServer":[
            "&Fetch Components", "serverFetchComponents", 
            "Ctrl+F", "serverfetchdatasources", 
            "Fetch datasources from the configuration server"],

        "actionStoreComponentServer":[
            "&Store Component", "serverStoreComponent", 
            "Ctrl+B", "serverstorecomponent", 
            "Store component in the configuration server"],

        "actionStoreAllComponentsServer":[
            "&Store All Components", "serverStoreAllComponents", 
            "", "serverstoreallcomponents", 
            "Store all components in the configuration server"],

        "actionDeleteComponentServer":[
            "&Delete Component", "serverDeleteComponent", 
            "", "serverdeletedatasource", 
            "Delete datalsource from the configuration server"],



        "actionFetchDataSourcesServer":[
            "&Fetch DataSources", "serverFetchDataSources", 
            "Ctrl+Shift+F", "serverfetchdatasources", 
            "Fetch datasources from the configuration server"],

        "actionStoreDataSourceServer":[
            "&Store Datasource", "serverStoreDataSource", 
            "Ctrl+Shift+B", "serverstoredatasource", 
            "Store datasource in the configuration server"],

        "actionStoreAllDataSourcesServer":[
            "&Store All Datasources", "serverStoreAllDataSources", 
            "", "serverstorealldatasources", 
            "Store all datasources in the configuration server"],

        "actionDeleteDataSourceServer":[
            "&Delete Datasource", "serverDeleteDataSource", 
            "", "serverdeletedatasource", 
            "Delete datasource from the configuration server"],



        "actionSetComponentMandatoryServer":[
            "Set Component Mandatory", "serverSetMandatoryComponent", 
            "", "serversetmandatory", 
            "Set the component as mandatory  on the configuration server"],

        "actionGetMandatoryComponentsServer":[
            "Get Mandatory Components", "serverGetMandatoryComponents", 
            "", "servergetmandatory", 
            "Get mandatory components  from the configuration server"],

        "actionUnsetComponentMandatoryServer":[
            "Unset Component Mandatory", "serverUnsetMandatoryComponent", 
            "", "serverunsetmandatory", 
            "Unset the component as mandatory on the configuration server"],



        "actionCloseServer":[
            "C&lose", "serverClose", 
            "Ctrl+L", "serverclose", 
            "Close connection to the configuration server"]
        }


   # server


    ## connect server action
    # \brief It connects to configuration server
    def serverConnect(self):
        cmd = self.pool.getCommand('serverConnect').clone()
        cmd.execute()
        self.cmdStack.append(cmd)

        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## fetch server components action
    # \brief It fetches components from the configuration server
    def serverFetchComponents(self):
        cmd = self.pool.getCommand('serverFetchComponents').clone()
        cmd.execute()

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## store server component action executed by button
    # \brief It stores the current component 
    #        in the configuration server executed by button
    def serverStoreComponentButton(self):
        if self.updateComponentListItem():
            self.serverStoreComponent()


    ## store server component action
    # \brief It stores the current component in the configuration server
    def serverStoreComponent(self):
        cmd = self.pool.getCommand('componentEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('componentMerge').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      
        cmd = self.pool.getCommand('serverStoreComponent').clone()
        cmd.execute()


    ## store server all components action
    # \brief It stores all components in the configuration server
    def serverStoreAllComponents(self):
        cmd = self.pool.getCommand('serverStoreAllComponents').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      

    ## delete server component action
    # \brief It deletes the current component from the configuration server
    def serverDeleteComponent(self):
        cmd = self.pool.getCommand('serverDeleteComponent').clone()
        cmd.execute()


    ## set component mandatory action
    # \brief It sets the current component as mandatory
    def serverSetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverSetMandatoryComponent').clone()
        cmd.execute()


    ## get mandatory components action
    # \brief It fetches mandatory components
    def serverGetMandatoryComponents(self):
        cmd = self.pool.getCommand('serverGetMandatoryComponents').clone()
        cmd.execute()


    ## unset component mandatory action
    # \brief It unsets the current component as mandatory
    def serverUnsetMandatoryComponent(self):
        cmd = self.pool.getCommand('serverUnsetMandatoryComponent').clone()
        cmd.execute()

    ## fetch server datasources action
    # \brief It fetches datasources from the configuration server
    def serverFetchDataSources(self):
        cmd = self.pool.getCommand('serverFetchDataSources').clone()
        cmd.execute()

        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## store server datasource action
    # \brief It stores the current datasource in the configuration server
    def serverStoreDataSource(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('dsourceApply').clone()
        cmd.execute()
        self.cmdStack.append(cmd)
        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      

        cmd = self.pool.getCommand('serverStoreDataSource').clone()
        cmd.execute()



    ## store server datasource action executed by button
    # \brief It stores the current datasource in 
    #        the configuration server executed by button
    def serverStoreDataSourceButton(self):
        if self.updateDataSourceListItem():
            self.serverStoreDataSource()

    ## store server all datasources action
    # \brief It stores all components in the configuration server
    def serverStoreAllDataSources(self):
        cmd = self.pool.getCommand('serverStoreAllDataSources').clone()
        cmd.execute()
        self.cmdStack.clear()
        self.pool.setDisabled("undo", True, "Can't Undo")   
        self.pool.setDisabled("redo", True, "Can't Redo")      


    ## delete server datasource action
    # \brief It deletes the current datasource from the configuration server
    def serverDeleteDataSource(self):
        cmd = self.pool.getCommand('dsourceEdit').clone()
        cmd.execute()
        cmd = self.pool.getCommand('serverDeleteDataSource').clone()
        cmd.execute()


    ## close server action
    # \brief It closes the configuration server
    def serverClose(self):
        cmd = self.pool.getCommand('serverClose').clone()
        cmd.execute()
        self.cmdStack.append(cmd)


        self.pool.setDisabled("undo", False, "Undo: ", 
                              self.cmdStack.getUndoName() )
        self.pool.setDisabled("redo", True, "Can't Redo")      


if __name__ == "__main__":   
    pass
