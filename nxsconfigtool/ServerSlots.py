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
# \file ServerSlots.py
# user pool commands of GUI application

""" Server slots """


from .ServerCommands import (
    ServerConnect,
    ServerCPCreate,
    ServerSCPCreate,
    ServerDSCreate,
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

from .EditCommands import (
    ComponentEdit,
    DataSourceApply,
    DataSourceEdit
)

from .ItemCommands import (
    ComponentApplyItem,
    ComponentMerge,
)


# stack with the application commands
class ServerSlots(object):

    # constructor
    # \param main the main window dialog
    def __init__(self, main):
        # main window
        self.main = main
        # command stack
        self.undoStack = main.undoStack

        # action data
        self.actions = {
            "actionConnectServer": [
                "&Connect ...", "serverConnect",
                "Ctrl+T", "serverconnect",
                "Connect to the configuration server"],
            "actionFetchComponentsServer": [
                "&Fetch Components", "serverFetchComponents",
                "Ctrl+F", "serverfetchdatasources",
                "Fetch datasources from the configuration server"],

            "actionStoreComponentServer": [
                "&Store Component", "serverStoreComponent",
                "Ctrl+B", "serverstorecomponent",
                "Store component in the configuration server"],

            "actionStoreAllComponentsServer": [
                "&Store All Components", "serverStoreAllComponents",
                "", "serverstoreallcomponents",
                "Store all components in the configuration server"],

            "actionDeleteComponentServer": [
                "&Delete Component", "serverDeleteComponent",
                "Ctrl+H", "serverdeletecomponent",
                "Delete component from the configuration server"],

            "actionFetchDataSourcesServer": [
                "&Fetch DataSources", "serverFetchDataSources",
                "Ctrl+Shift+F", "serverfetchdatasources",
                "Fetch datasources from the configuration server"],

            "actionStoreDataSourceServer": [
                "&Store Datasource", "serverStoreDataSource",
                "Ctrl+Shift+B", "serverstoredatasource",
                "Store datasource in the configuration server"],

            "actionStoreAllDataSourcesServer": [
                "&Store All Datasources", "serverStoreAllDataSources",
                "", "serverstorealldatasources",
                "Store all datasources in the configuration server"],

            "actionDeleteDataSourceServer": [
                "&Delete Datasource", "serverDeleteDataSource",
                "Ctrl+Shift+H", "serverdeletedatasource",
                "Delete datasource from the configuration server"],

            "actionSetComponentMandatoryServer": [
                "Set Component Mandatory", "serverSetMandatoryComponent",
                "", "serversetmandatory",
                "Set the component as mandatory  on the configuration server"],

            "actionGetMandatoryComponentsServer": [
                "Get Mandatory Components", "serverGetMandatoryComponents",
                "", "servergetmandatory",
                "Get mandatory components  from the configuration server"],

            "actionUnsetComponentMandatoryServer": [
                "Unset Component Mandatory", "serverUnsetMandatoryComponent",
                "", "serverunsetmandatory",
                "Unset the component as mandatory on"
                " the configuration server"],
            "actionCreateStdComponentServer": [
                "&Create Standard Component ...", "serverSCPCreate",
                "", "serverscpcreate",
                "Create Component defined in online.xml file"],
            "actionCreateComponentServer": [
                "&Create Online Component ...", "serverCPCreate",
                "", "servercpcreate",
                "Create Component defined in online.xml file"],
            "actionCreateDataSourcesServer": [
                "&Create Online Component ...", "serverDSCreate",
                "", "serverdscreate",
                "Create all known DataSources defined in online.xml file"],
            "actionCloseServer": [
                "C&lose", "serverClose",
                "Ctrl+L", "serverclose",
                "Close connection to the configuration server"]
        }

    # connect server action
    # \brief It connects to configuration server
    def serverConnect(self):
        cmd = ServerConnect(self.main)
        self.undoStack.push(cmd)

    # create component action
    # \brief It creates components and datasources from online.xml
    def serverCPCreate(self):
        cmd = ServerCPCreate(self.main)
        cmd.redo()
        self.undoStack.clear()

    # create standard component action
    # \brief It creates stamdard components and datasources from online.xml
    def serverSCPCreate(self):
        cmd = ServerSCPCreate(self.main)
        cmd.redo()
        self.undoStack.clear()

    # create datasources action
    # \brief It creates all known datasources from online.xml
    def serverDSCreate(self):
        cmd = ServerDSCreate(self.main)
        cmd.redo()
        self.undoStack.clear()

    # fetch server components action
    # \brief It fetches components from the configuration server
    def serverFetchComponents(self):
        cmd = ServerFetchComponents(self.main)
        cmd.redo()
        self.undoStack.clear()

    # store server component action executed by button
    # \brief It stores the current component
    #        in the configuration server executed by button
    def serverStoreComponentButton(self):
        if self.main.updateComponentListItem():
            cmd = ComponentApplyItem(self.main)
            self.undoStack.push(cmd)
            self.serverStoreComponent(False)

    # store server component action
    # \brief It stores the current component in the configuration server
    def serverStoreComponent(self, focus=True):
        cmd = ComponentEdit(self.main)
        cmd.redo()
        cmd = ComponentMerge(self.main)
        self.undoStack.push(cmd)
        cmd = ServerStoreComponent(self.main)
        cmd.redo()
        if focus:
            self.main.componentList.setItemFocus()

    # store server all components action
    # \brief It stores all components in the configuration server
    def serverStoreAllComponents(self):
        cmd = ComponentApplyItem(self.main)
        cmd = ServerStoreAllComponents(self.main)
        cmd.redo()
        self.undoStack.clear()

    # delete server component action
    # \brief It deletes the current component from the configuration server
    def serverDeleteComponent(self):
        cmd = ServerDeleteComponent(self.main)
        cmd.redo()
        self.main.componentList.setItemFocus()

    # set component mandatory action
    # \brief It sets the current component as mandatory
    def serverSetMandatoryComponent(self):
        cmd = ServerSetMandatoryComponent(self.main)
        cmd.redo()

    # get mandatory components action
    # \brief It fetches mandatory components
    def serverGetMandatoryComponents(self):
        cmd = ServerGetMandatoryComponents(self.main)
        cmd.redo()

    # unset component mandatory action
    # \brief It unsets the current component as mandatory
    def serverUnsetMandatoryComponent(self):
        cmd = ServerUnsetMandatoryComponent(self.main)
        cmd.redo()

    # fetch server datasources action
    # \brief It fetches datasources from the configuration server
    def serverFetchDataSources(self):
        cmd = ServerFetchDataSources(self.main)
        cmd.redo()
        self.undoStack.clear()

    # store server datasource action
    # \brief It stores the current datasource in the configuration server
    def serverStoreDataSource(self, focus=True):
        cmd = DataSourceEdit(self.main)
        cmd.redo()
        cmd = DataSourceApply(self.main)
        self.undoStack.push(cmd)
        cmd = ServerStoreDataSource(self.main)
        cmd.redo()
        if focus:
            self.main.sourceList.setItemFocus()

    # store server datasource action executed by button
    # \brief It stores the current datasource in
    #        the configuration server executed by button
    def serverStoreDataSourceButton(self):
        if self.main.updateDataSourceListItem():
            self.serverStoreDataSource(False)

    # store server all datasources action
    # \brief It stores all components in the configuration server
    def serverStoreAllDataSources(self):
        cmd = ServerStoreAllDataSources(self.main)
        cmd.redo()
        self.undoStack.clear()

    # delete server datasource action
    # \brief It deletes the current datasource from the configuration server
    def serverDeleteDataSource(self):
        cmd = DataSourceEdit(self.main)
        cmd.redo()
        cmd = ServerDeleteDataSource(self.main)
        cmd.redo()
        self.main.sourceList.setItemFocus()

    # close server action
    # \brief It closes the configuration server
    def serverClose(self):
        cmd = ServerClose(self.main)
        self.undoStack.push(cmd)


if __name__ == "__main__":
    pass
