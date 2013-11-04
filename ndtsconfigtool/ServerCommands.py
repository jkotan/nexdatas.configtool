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

from PyQt4.QtGui import (QMessageBox)

from .DataSourceDlg import (CommonDataSourceDlg)
from . import DataSource
from .ComponentDlg import ComponentDlg
from .Component import Component
from .Command import Command

## Command which performs connection to the configuration server
class ServerConnect(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._oldstate = None
        self._state = None
        

    ## executes the command
    # \brief It perform connection to the configuration server
    def redo(self):       
        if self.receiver.main.configServer:
            try:
                if self._oldstate is None:
                    self._oldstate = self.receiver.main.configServer.getState()
                if  self._state is None:   
                    self.receiver.main.configServer.open()
                    self._state = self.receiver.main.configServer.getState()
                else:
                    self.receiver.main.configServer.setState(self._state)
                    self.receiver.main.configServer.connect()
                    
                self.receiver.main.disableServer(False)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in connecting to Configuration Server", 
                    unicode(e))
    
        print "EXEC serverConnect"

    ## unexecutes the command
    # \brief It undo connection to the configuration server, 
    #        i.e. it close the connection to the server
    def undo(self):
        if self.receiver.main.configServer:
            try:
                self.receiver.main.configServer.close()
                if self._oldstate is None:
                    self.receiver.main.configServer.setState(self._oldstate)
                self.receiver.main.disableServer(True)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in Closing Configuration Server Connection", 
                    unicode(e))

        print "UNDO serverConnect"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerConnect(self.receiver, self.slot) 



## Command which fetches the components from the configuration server
class ServerFetchComponents(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    ## executes the command
    # \brief It fetches the components from the configuration server
    def redo(self):       
        if QMessageBox.question(
            self.receiver.main, 
            "Component - Reload List from Configuration server",
            ("All unsaved components will be lost. "\
                 "Would you like to proceed ?").encode(),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes) == QMessageBox.No :
            return

        
        subwindows = self.receiver.main.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                dialog = subwindow.widget()
                if isinstance(dialog, ComponentDlg):
                    self.receiver.main.ui.mdi.setActiveSubWindow(subwindow)
                    self.receiver.main.ui.mdi.closeActiveSubWindow()

        self.receiver.main.componentList.elements = {} 

        if self.receiver.main.configServer:
            try:
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )

                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                cdict = self.receiver.main.configServer.fetchComponents()
                self.receiver.main.setComponents(cdict)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in fetching components", unicode(e))
    
        print "EXEC serverFetchComponents"

    ## unexecutes the command
    # \brief It does nothing
    def undo(self):
        print "UNDO serverFetchComponents"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerFetchComponents(self.receiver, self.slot) 


## Command which stores the current component in the configuration server
class ServerStoreComponent(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        

    ## executes the command
    # \brief It stores the current component in the configuration server
    def redo(self):       
        if self._cp is None:
            self._cp = self.receiver.main.componentList.currentListElement()
        if self._cp is not None:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = Component()
                self._cpEdit.id = self._cp.id
                self._cpEdit.directory = \
                    self.receiver.main.componentList.directory
                self._cpEdit.name = \
                    self.receiver.main.componentList.elements[
                    self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(
                    self.receiver.main.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle(
                    "%s [Component]" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance 
                
            if hasattr(self._cpEdit, "connectExternalActions"):     
                self._cpEdit.connectExternalActions(
                    **self.receiver.main.externalCPActions)      


                
            subwindow = self.receiver.main.subWindow(
                self._cpEdit, self.receiver.main.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.main.ui.mdi.setActiveSubWindow(subwindow) 
            else:    
                self._cpEdit.createGUI()

                self._cpEdit.addContextMenu(
                    self.receiver.main.contextMenuActions)
                if self._cpEdit.isDirty():
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]*" % self._cp.name)
                else:
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]" % self._cp.name)
                     
                self._cpEdit.reconnectSaveAction()
                subwindow = self.receiver.main.ui.mdi.addSubWindow(
                    self._cpEdit.dialog)
                subwindow.resize(680, 560)
                self._cpEdit.dialog.show()
                self._cp.instance = self._cpEdit 
                    
            try:
                xml = self._cpEdit.get()    
                if not self.receiver.main.configServer.connected:
                    if QMessageBox.question(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            ),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes) == QMessageBox.No :
                        raise Exception("Server not connected")

                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                self.receiver.main.configServer.storeComponent(
                    self._cpEdit.name, xml)
                self._cpEdit.savedXML = xml
                self._cp.savedName = self._cp.name
            except Exception, e:
                QMessageBox.warning(self.receiver.main, 
                                    "Error in storing the component", 
                                    unicode(e))
        if hasattr(self._cp, "id"):
            self.receiver.main.componentList.populateElements(self._cp.id)
        else:
            self.receiver.main.componentList.populateElements()

            
        print "EXEC serverStoreComponent"

    ## unexecutes the command
    # \brief It populates only the component list
    def undo(self):
        if hasattr(self._cp, "id"):
            self.receiver.main.componentList.populateElements(self._cp.id)
        else:
            self.receiver.main.componentList.populateElements()
        print "UNDO serverStoreComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerStoreComponent(self.receiver, self.slot) 





## Command which deletes the current component from the configuration server
class ServerDeleteComponent(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        

    ## executes the command
    # \brief It deletes the current component from the configuration server
    def redo(self):       
        if self._cp is None:
            self._cp = self.receiver.main.componentList.currentListElement()
        if self._cp is not None:

            try:
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )

                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                self.receiver.main.configServer.deleteComponent(self._cp.name)
                self._cp.savedName = ""
                if hasattr(self._cp, "instance"):
                    self._cp.instance.savedXML = ""
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, "Error in deleting the component", 
                    unicode(e))

        cid = self._cp.id if hasattr(self._cp, "id") else None
        self.receiver.main.componentList.populateElements(cid)

            
        print "EXEC serverDeleteComponent"

    ## unexecutes the command
    # \brief It populates only the component list
    def undo(self):
        if hasattr(self._cp, "id"):
            self.receiver.main.componentList.populateElements(self._cp.id)
        else:
            self.receiver.main.componentList.populateElements()
        print "UNDO serverDeleteComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerDeleteComponent(self.receiver, self.slot) 




## Command which sets on the configuration server the current component 
#  as mandatory
class ServerSetMandatoryComponent(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        

    ## executes the command
    # \brief It sets on the configuration server the current component 
    #        as mandatory
    def redo(self):       
        if self._cp is None:
            self._cp = self.receiver.main.componentList.currentListElement()
        if self._cp is not None:
            try:
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )

                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                self.receiver.main.configServer.setMandatory(self._cp.name)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in setting the component as mandatory", 
                    unicode(e))
        print "EXEC serverSetMandatoryComponent"

    ## unexecutes the command
    # \brief It does nothing    
    def undo(self):
        print "UNDO serverSetMandatoryComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerSetMandatoryComponent(self.receiver, self.slot) 



## Command which fetches a list of the mandatory components from 
#  the configuration server
class ServerGetMandatoryComponents(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        

    ## executes the command
    # \brief It fetches a list of the mandatory components from 
    #        the configuration server
    def redo(self):       
        try:
            if not self.receiver.main.configServer.connected:
                QMessageBox.information(
                    self.receiver.main, 
                    "Connecting to Configuration Server", 
                    "Connecting to %s on %s:%s" % (
                        self.receiver.main.configServer.device,
                        self.receiver.main.configServer.host,
                        self.receiver.main.configServer.port
                        )
                    )

            self.receiver.main.configServer.connect()
            self.receiver.main.disableServer(False)
            mandatory = self.receiver.main.configServer.getMandatory()
            QMessageBox.information(
                self.receiver.main, "Mandatory", 
                "Mandatory Components: \n %s" % unicode(mandatory)) 
        except Exception, e:
            QMessageBox.warning(
                self.receiver.main, 
                "Error in getting the mandatory components", 
                unicode(e))
        print "EXEC serverGetMandatoryComponent"

    ## unexecutes the command
    # \brief It does nothing    
    def undo(self):
        print "UNDO serverGetMandatoryComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerGetMandatoryComponents(self.receiver, self.slot) 




## Command which sets on the configuration server the current component 
#  as not mandatory
class ServerUnsetMandatoryComponent(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        

    ## executes the command
    # \brief It sets on the configuration server the current component 
    #        as not mandatory
    def redo(self):       
        if self._cp is None:
            self._cp = \
                self.receiver.main.componentList.currentListElement()
        if self._cp is not None:
            try:
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )

                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                self.receiver.main.configServer.unsetMandatory(
                    self._cp.name)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in setting the component as mandatory", 
                    unicode(e))
        print "EXEC serverUnsetMandatoryComponent"

    ## unexecutes the command
    # \brief It does nothing    
    def undo(self):
        print "UNDO serverUnsetMandatoryComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerUnsetMandatoryComponent(self.receiver, self.slot) 


## Command which fetches the datasources from the configuration server
class ServerFetchDataSources(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        

    ## executes the command
    # \brief It fetches the datasources from the configuration server
    def redo(self):       

        if QMessageBox.question(
            self.receiver.main, 
            "DataSource - Reload List from Configuration Server",
            ("All unsaved datasources will be lost. "\
                 "Would you like to proceed ?").encode(),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return


        subwindows = self.receiver.main.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                dialog = subwindow.widget()
                if isinstance(dialog, CommonDataSourceDlg):
                    self.receiver.main.ui.mdi.setActiveSubWindow(subwindow)
                    self.receiver.main.ui.mdi.closeActiveSubWindow()
                    
        self.receiver.main.sourceList.elements = {} 


        if self.receiver.main.configServer:
            try:
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )
                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                cdict = self.receiver.main.configServer.fetchDataSources()
                self.receiver.main.setDataSources(cdict)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in fetching datasources", unicode(e))
    

        print "EXEC serverFetchDataSources"

    ## unexecutes the command
    # \brief It does nothing    
    def undo(self):
        print "UNDO serverFetchDataSources"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerFetchDataSources(self.receiver, self.slot) 


## Command which stores the current datasource in the configuration server
class ServerStoreDataSource(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        

    ## executes the command
    # \brief It fetches the datasources from the configuration server
    def redo(self):       
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListElement()
        if self._ds is not None and hasattr(self._ds, "instance"):
            try:
                xml = self._ds.instance.get()    
                if not self.receiver.main.configServer.connected:
                    if QMessageBox.question(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            ),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes) == QMessageBox.No :
                        raise Exception("Server not connected")

                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                if self._ds.instance.name:
                    self.receiver.main.configServer.storeDataSource(
                        self._ds.instance.dataSourceName, xml)
                else:
                    self.receiver.main.configServer.storeDataSource(
                        self._ds.instance.name, xml)
                self._ds.instance.savedXML = xml
                self._ds.savedName = self._ds.name
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in datasource storing", unicode(e))
            

        ds = self.receiver.main.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.main.sourceList.populateElements(ds.id)
        else:
            self.receiver.main.sourceList.populateElements()
            
        print "EXEC serverStoreDataSource"

    ## unexecutes the command
    # \brief It populates the datasource list
    def undo(self):
        ds = self.receiver.main.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.main.sourceList.populateElements(ds.id)
        else:
            self.receiver.main.sourceList.populateElements()
        print "UNDO serverStoreDataSource"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerStoreDataSource(self.receiver, self.slot) 

## Command which deletes the current datasource in the configuration server
class ServerDeleteDataSource(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None

    ## executes the command
    # \brief It deletes the current datasource in the configuration server
    def redo(self):       
        if self._ds is None:
            self._ds = self.receiver.main.sourceList.currentListElement()
        if self._ds is not None:
            try:
                if hasattr(self._ds, "instance"):
                    self._ds.instance.savedXML = ""
                    name = self._ds.instance.dataSourceName 
                    if name is None:
                        name = ""
                    if not self.receiver.main.configServer.connected:
                        QMessageBox.information(
                            self.receiver.main, 
                            "Connecting to Configuration Server", 
                            "Connecting to %s on %s:%s" % (
                                self.receiver.main.configServer.device,
                                self.receiver.main.configServer.host,
                                self.receiver.main.configServer.port
                                )
                            )

                    self.receiver.main.configServer.connect()
                    self.receiver.main.disableServer(False)
                    self.receiver.main.configServer.deleteDataSource(name)
                    self._ds.savedName = ""

            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in datasource deleting", unicode(e))
            

        ds = self.receiver.main.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.main.sourceList.populateElements(ds.id)
        else:
            self.receiver.main.sourceList.populateElements()
        print "EXEC serverDeleteDataSource"

    ## unexecutes the command
    # \brief It populates the datasource list
    def undo(self):
        ds = self.receiver.main.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.main.sourceList.populateElements(ds.id)
        else:
            self.receiver.main.sourceList.populateElements()
        print "UNDO serverDeleteDataSource"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerDeleteDataSource(self.receiver, self.slot) 



## Command which closes connection to the configuration server
class ServerClose(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._state = None

    ## executes the command
    # \brief It closes connection to the configuration server
    def redo(self):       
        if self.receiver.main.configServer:
            self.receiver.main.configServer.close()


        if self.receiver.main.configServer:
            try:
                if self._state is None:
                    self._state = self.receiver.main.configServer.getState()
                self.receiver.main.configServer.close()
                self.receiver.main.disableServer(True)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in closing connection to Configuration Server", 
                    unicode(e))
    
        print "EXEC serverClose"

    ## unexecutes the command
    # \brief It reopen the connection to the configuration server
    def undo(self):
        if self.receiver.main.configServer:
            try:
                if  self._state is None:   
                    self.receiver.main.configServer.open()
                else:
                    self.receiver.main.configServer.setState(self._state)
                    self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, 
                    "Error in connecting to Configuration Server", 
                    unicode(e))
        print "UNDO serverClose"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerClose(self.receiver, self.slot) 


## Command which saves all components in the file
class ServerStoreAllComponents(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._subwindow = None
        
        
    ## executes the command
    # \brief It saves all components in the file
    def redo(self):
            
        for icp in self.receiver.main.componentList.elements.keys():
            cp = self.receiver.main.componentList.elements[icp]
            if cp.instance is None:
                #                self._cpEdit = FieldWg()  
                cpEdit = Component()
                cpEdit.id = cp.id
                cpEdit.directory = self.receiver.main.componentList.directory
                cpEdit.name = self.receiver.main.componentList.elements[
                    cp.id].name
                cpEdit.createGUI()
                cpEdit.addContextMenu(self.receiver.main.contextMenuActions)
                cpEdit.createHeader()
                cpEdit.dialog.setWindowTitle("%s [Component]" % cp.name)
                cp.instance = cpEdit

            try:
                cp.instance.merge()    
                xml = cp.instance.get()    
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )
                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                self.receiver.main.configServer.storeComponent(
                    cp.instance.name, xml)
                cp.instance.savedXML = xml
                cp.savedName = cp.name
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, "Error in storing the component", 
                    unicode(e))
        if hasattr(cp, "id"):
            self.receiver.main.componentList.populateElements(cp.id)
        else:
            self.receiver.main.componentList.populateElements()


        print "EXEC componentStoreAll"


    ## unexecutes the command
    # \brief It does nothing
    def undo(self):
        print "UNDO componentStoreAll"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerStoreAllComponents(self.receiver, self.slot) 


## Command which saves all the datasources in files
class ServerStoreAllDataSources(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It saves all the datasources in files
    def redo(self):
            
        for ids in self.receiver.main.sourceList.elements.keys():
            ds = self.receiver.main.sourceList.elements[ids]
            if ds.instance is None:
                dsEdit = DataSource.DataSource()
                dsEdit.id = ds.id
                dsEdit.directory = self.receiver.main.sourceList.directory
                dsEdit.name = \
                    self.receiver.main.sourceList.elements[ds.id].name
                ds.instance = dsEdit 
            print "Store", ds.instance.name

            try:
                xml = ds.instance.get()    
                if not self.receiver.main.configServer.connected:
                    QMessageBox.information(
                        self.receiver.main, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.main.configServer.device,
                            self.receiver.main.configServer.host,
                            self.receiver.main.configServer.port
                            )
                        )
                self.receiver.main.configServer.connect()
                self.receiver.main.disableServer(False)
                if ds.instance.name:
                    self.receiver.main.configServer.storeDataSource(
                        ds.instance.dataSourceName, xml)
                else:
                    self.receiver.main.configServer.storeDataSource(
                        ds.instance.name, xml)
                ds.instance.savedXML = xml
                ds.savedName = ds.name
            except Exception, e:
                QMessageBox.warning(
                    self.receiver.main, "Error in datasource storing", 
                    unicode(e))


        ds = self.receiver.main.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.main.sourceList.populateElements(ds.id)
        else:
            self.receiver.main.sourceList.populateElements()


        print "EXEC dsourceStoreAll"

    ## executes the command
    # \brief It does nothing
    def undo(self):
        print "UNDO dsourceStoreAll"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerStoreAllDataSources(self.receiver, self.slot) 
        

if __name__ == "__main__":
    pass

