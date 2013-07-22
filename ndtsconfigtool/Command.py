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

from PyQt4.QtGui import (QMessageBox, QFileDialog)
from PyQt4.QtCore import (SIGNAL, Qt, QFileInfo)

from DataSourceList import DataSourceList
from ComponentList import ComponentList
from DataSourceDlg import (DataSource, DataSourceDlg, CommonDataSourceDlg)
from ComponentDlg import (Component, ComponentDlg)
from LabeledObject import LabeledObject

import time
import copy
from ComponentModel import ComponentModel


## abstract command 
class Command(object):
    
    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self,receiver, slot):
        ## command receiver
        self.receiver = receiver
        ## command slot name 
        self.slot = slot

    ## connects the slot name to receiver
    # returns callable slot     
    def connectSlot(self):
        if hasattr(self.receiver, self.slot):
            return  getattr(self.receiver, self.slot)
        
    ## executes the command
    # \brief It is an abstract member function to reimplement execution of the derived command
    def execute(self):
        pass

    ## unexecutes the command
    # \brief It is an abstract member function to reimplement un-do execution of the derived command
    def unexecute(self):
        pass

    ## reexecutes the command
    # \brief It is an abstract member function to reimplement re-do execution of the derived command. In the current implementation it calls self.execute()
    def reexecute(self):
        return self.execute()


    ## clones the command
    # \brief It is an abstract member function to reimplement cloning of the derived command
    def clone(self): 
        pass



## Command which performs connection to the configuration server
class ServerConnect(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._oldstate = None
        self._state = None
        

    ## executes the command
    # \brief It perform connection to the configuration server
    def execute(self):       
        if self.receiver.configServer:
            try:
                if self._oldstate is None:
                    self._oldstate = self.receiver.configServer.getState()
                if  self._state is None:   
                    self.receiver.configServer.open()
                    self._state = self.receiver.configServer.getState()
                else:
                    self.receiver.configServer.setState(self._state)
                    self.receiver.configServer.connect()
                    
                self.receiver.disableServer(False)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in connecting to Configuration Server", unicode(e))
    
        print "EXEC serverConnect"

    ## unexecutes the command
    # \brief It undo connection to the configuration server, i.e. it close the connection to the server
    def unexecute(self):
        if self.receiver.configServer:
            try:
                self.receiver.configServer.close()
                if self._oldstate is None:
                    self.receiver.configServer.setState(self._oldstate)
                self.receiver.disableServer(True)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in Closing Configuration Server Connection", unicode(e))

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
        Command.__init__(self,receiver, slot)

    ## executes the command
    # \brief It fetches the components from the configuration server
    def execute(self):       
        if QMessageBox.question(self.receiver, "Component - Reload List from Configuration server",
                                "All unsaved components will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes) == QMessageBox.No :
            return

        
        subwindows = self.receiver.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                dialog = subwindow.widget()
                if isinstance(dialog,ComponentDlg):
                    self.receiver.mdi.setActiveSubWindow(subwindow)
                    self.receiver.mdi.closeActiveSubWindow()

        self.receiver.componentList.components = {} 

        if self.receiver.configServer:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                cdict = self.receiver.configServer.fetchComponents()
                self.receiver.setComponents(cdict)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in fetching components", unicode(e))
    
        print "EXEC serverFetchComponents"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
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
        Command.__init__(self,receiver, slot)
        self._cp = None
        self._cpEdit = None
        

    ## executes the command
    # \brief It stores the current component in the configuration server
    def execute(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = Component()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle("%s [Component]" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance 
                
            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(**self.receiver.externalCPActions)      


                
            subwindow = self.receiver.subWindow(
                self._cpEdit, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
            else:    
                self._cpEdit.createGUI()

                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                if self._cpEdit.isDirty():
                    self._cpEdit.dialog.setWindowTitle("%s [Component]*" % self._cp.name)
                else:
                    self._cpEdit.dialog.setWindowTitle("%s [Component]" % self._cp.name)
                     
                self._cpEdit.reconnectSaveAction()
                subwindow = self.receiver.mdi.addSubWindow(self._cpEdit.dialog)
                subwindow.resize(640,560)
                self._cpEdit.dialog.show()
                #                self._cpEdit.dialog.setAttribute(Qt.WA_DeleteOnClose)
                self._cp.instance = self._cpEdit 
                    
            try:
                xml = self._cpEdit.get()    
                if not self.receiver.configServer.connected:
                    if QMessageBox.question(self.receiver, "Connecting to Configuration Server", 
                                            "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            ),
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.Yes) == QMessageBox.No :
                        raise Exception("Server not connected")

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.storeComponent(self._cpEdit.name, xml)
                self._cpEdit.savedXML = xml
                self._cp.savedName = self._cp.name
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in storing the component", unicode(e))
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()

            
        print "EXEC serverStoreComponent"

    ## unexecutes the command
    # \brief It populates only the component list
    def unexecute(self):
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()
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
        Command.__init__(self,receiver, slot)
        self._cp = None
        self._cpEdit = None
        

    ## executes the command
    # \brief It deletes the current component from the configuration server
    def execute(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:

            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.deleteComponent(self._cp.name)
                self._cp.savedName = ""
                if hasattr(self._cp,"instance"):
                    self._cp.instance.savedXML = ""
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in deleting the component", unicode(e))

        cid = self._cp.id if hasattr(self._cp,"id") else None
        self.receiver.componentList.populateComponents(cid)

            
        print "EXEC serverDeleteComponent"

    ## unexecutes the command
    # \brief It populates only the component list
    def unexecute(self):
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()
        print "UNDO serverDeleteComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerDeleteComponent(self.receiver, self.slot) 




## Command which sets on the configuration server the current component as mandatory
class ServerSetMandatoryComponent(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._cp = None
        

    ## executes the command
    # \brief It sets on the configuration server the current component as mandatory
    def execute(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.setMandatory(self._cp.name)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in setting the component as mandatory", unicode(e))
        print "EXEC serverSetMandatoryComponent"

    ## unexecutes the command
    # \brief It does nothing    
    def unexecute(self):
        print "UNDO serverSetMandatoryComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerSetMandatoryComponent(self.receiver, self.slot) 



## Command which fetches a list of the mandatory components from the configuration server
class ServerGetMandatoryComponents(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        

    ## executes the command
    # \brief It fetches a list of the mandatory components from the configuration server
    def execute(self):       
        try:
            if not self.receiver.configServer.connected:
                QMessageBox.information(
                    self.receiver, "Connecting to Configuration Server", 
                    "Connecting to %s on %s:%s" % (
                        self.receiver.configServer.device,
                        self.receiver.configServer.host,
                        self.receiver.configServer.port
                        )
                    )

            self.receiver.configServer.connect()
            self.receiver.disableServer(False)
            mandatory = self.receiver.configServer.getMandatory()
            QMessageBox.information(self.receiver,"Mandatory", "Mandatory Components: \n %s" % unicode(mandatory)) 
        except Exception, e:
            QMessageBox.warning(self.receiver, "Error in getting the mandatory components", unicode(e))
        print "EXEC serverGetMandatoryComponent"

    ## unexecutes the command
    # \brief It does nothing    
    def unexecute(self):
        print "UNDO serverGetMandatoryComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerGetMandatoryComponents(self.receiver, self.slot) 




## Command which sets on the configuration server the current component as not mandatory
class ServerUnsetMandatoryComponent(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._cp = None
        

    ## executes the command
    # \brief It sets on the configuration server the current component as not mandatory
    def execute(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.unsetMandatory(self._cp.name)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in setting the component as mandatory", unicode(e))
        print "EXEC serverUnsetMandatoryComponent"

    ## unexecutes the command
    # \brief It does nothing    
    def unexecute(self):
        print "UNDO serverUnsetMandatoryComponent"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerUnsetMandatoryComponent(self.receiver, self.slot) 


## Command which fetches the datasources from the configuration server
class ServerFetchDataSources(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        

    ## executes the command
    # \brief It fetches the datasources from the configuration server
    def execute(self):       

        if QMessageBox.question(self.receiver, "DataSource - Reload List from Configuration Server",
                                "All unsaved datasources will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return


        subwindows = self.receiver.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                dialog = subwindow.widget()
                if isinstance(dialog, CommonDataSourceDlg):
                    self.receiver.mdi.setActiveSubWindow(subwindow)
                    self.receiver.mdi.closeActiveSubWindow()
                    
        self.receiver.sourceList.datasources = {} 


        if self.receiver.configServer:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )
                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                cdict = self.receiver.configServer.fetchDataSources()
                self.receiver.setDataSources(cdict)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in fetching datasources", unicode(e))
    

        print "EXEC serverFetchDataSources"

    ## unexecutes the command
    # \brief It does nothing    
    def unexecute(self):
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
        Command.__init__(self,receiver, slot)
        self._ds = None
        

    ## executes the command
    # \brief It fetches the datasources from the configuration server
    def execute(self):       
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None and hasattr(self._ds,"instance"):
            try:
                xml = self._ds.instance.get()    
                if not self.receiver.configServer.connected:
                    if QMessageBox.question(self.receiver, "Connecting to Configuration Server", 
                                            "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            ),
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.Yes) == QMessageBox.No :
                        raise Exception("Server not connected")

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                if self._ds.instance.name:
                    self.receiver.configServer.storeDataSource(self._ds.instance.dataSourceName, xml)
                else:
                    self.receiver.configServer.storeDataSource(self._ds.instance.name, xml)
                self._ds.instance.savedXML = xml
                self._ds.savedName = self._ds.name
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in datasource storing", unicode(e))
            

        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
            
        print "EXEC serverStoreDataSource"

    ## unexecutes the command
    # \brief It populates the datasource list
    def unexecute(self):
        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
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
        Command.__init__(self,receiver, slot)
        self._ds = None

    ## executes the command
    # \brief It deletes the current datasource in the configuration server
    def execute(self):       
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is not None:
            try:
                if hasattr(self._ds,"instance"):
                    self._ds.instance.savedXML = ""
                    print "DEL", self._ds.instance.dataSourceName
                    name = self._ds.instance.dataSourceName 
                    if name is None:
                        name = ""
                    if not self.receiver.configServer.connected:
                        QMessageBox.information(
                            self.receiver, "Connecting to Configuration Server", 
                            "Connecting to %s on %s:%s" % (
                                self.receiver.configServer.device,
                                self.receiver.configServer.host,
                                self.receiver.configServer.port
                                )
                            )

                    self.receiver.configServer.connect()
                    self.receiver.disableServer(False)
                    self.receiver.configServer.deleteDataSource(name)
                    self._ds.savedName = ""

            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in datasource deleting", unicode(e))
            

        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
        print "EXEC serverDeleteDataSource"

    ## unexecutes the command
    # \brief It populates the datasource list
    def unexecute(self):
        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
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
        Command.__init__(self,receiver, slot)
        self._state = None

    ## executes the command
    # \brief It closes connection to the configuration server
    def execute(self):       
        if self.receiver.configServer:
            self.receiver.configServer.close()


        if self.receiver.configServer:
            try:
                if self._state is None:
                    self._state = self.receiver.configServer.getState()
                self.receiver.configServer.close()
                self.receiver.disableServer(True)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in closing connection to Configuration Server", unicode(e))
    
        print "EXEC serverClose"

    ## unexecutes the command
    # \brief It reopen the connection to the configuration server
    def unexecute(self):
        if self.receiver.configServer:
            try:
                if  self._state is None:   
                    self.receiver.configServer.open()
                else:
                    self.receiver.configServer.setState(self._state)
                    self.receiver.configServer.connect()
                self.receiver.disableServer(False)
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in connecting to Configuration Server", unicode(e))
        print "UNDO serverClose"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerClose(self.receiver, self.slot) 






## Command which creates a new component
class ComponentNew(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._comp = None
        

    ## executes the command
    # \brief It creates a new component
    def execute(self):       
            
        if self._comp is None:
            self._comp = LabeledObject("", None)
        else:    
            self._comp.instance = None
        
        self.receiver.componentList.addComponent(self._comp)
        print "EXEC componentNew"
        
    ## unexecutes the command
    # \brief It removes the new component
    def unexecute(self):
        if self._comp is not None:
            self.receiver.componentList.removeComponent(self._comp, False)

            if hasattr(self._comp,'instance') and self._comp.instance:
                subwindow = self.receiver.subWindow(self._comp.instance, self.receiver.mdi.subWindowList())
                if subwindow:
                    self.receiver.mdi.setActiveSubWindow(subwindow) 
                    self.receiver.mdi.closeActiveSubWindow() 
            
        print "UNDO componentNew"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentNew(self.receiver, self.slot) 





## Command which loads an existing component from the file
class ComponentOpen(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._cpEdit = None
        self._cp = None
        self._fpath = None
        
    ## executes the command
    # \brief It loads an existing component from the file
    def execute(self):
        if hasattr(self.receiver,'mdi'):
            if self._cp is None:
                self._cp = LabeledObject("", None)
            else:    
                self._cp.instance = None

            self._cpEdit = Component()
            self._cpEdit.idc = self._cp.id
            self._cpEdit.directory = self.receiver.componentList.directory
            self._cpEdit.createGUI()
            self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
            if self._fpath:
                path = self._cpEdit.load(self._fpath)
            else:
                path = self._cpEdit.load()
                self._fpath = path

            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(**self.receiver.externalCPActions)      

            if path:   
                self._cp.name = self._cpEdit.name  
                self._cp.instance = self._cpEdit
            
                self.receiver.componentList.addComponent(self._cp,False)
                self._cpEdit.dialog.setWindowTitle("%s [Component]" % self._cp.name)

                subwindow = self.receiver.subWindow(
                    self._cp.instance, self.receiver.mdi.subWindowList())
                if subwindow:
                    self.receiver.mdi.setActiveSubWindow(subwindow) 
                    self._cp.instance.dialog.setSaveFocus()
                else:    
                    self._subwindow = self.receiver.mdi.addSubWindow(self._cpEdit.dialog)
                    self._subwindow.resize(640,560)
                    self._cpEdit.dialog.setSaveFocus()
                    self._cpEdit.dialog.show()
                    self._cp.instance = self._cpEdit 
                self._cpEdit.dialog.show()
                print "EXEC componentOpen"


    ## unexecutes the command
    # \brief It removes the loaded component from the component list
    def unexecute(self):
        if hasattr(self._cp, "instance"):
            if self._fpath:

                if hasattr(self._cp,'instance') and self._cp.instance:
                    subwindow = self.receiver.subWindow(
                        self._cpEdit, self.receiver.mdi.subWindowList())
                    if subwindow:
                        self.receiver.mdi.setActiveSubWindow(subwindow) 
                        self.receiver.mdi.closeActiveSubWindow() 

                self.receiver.componentList.removeComponent(self._cp, False)
                self._cp.instance = None


            
        print "UNDO componentOpen"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentOpen(self.receiver, self.slot) 




## Command which loads an existing datasource from the file
class DataSourceOpen(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self,receiver, slot)
        self._dsEdit = None
        self._ds = None
        self._fpath = None

        
    ## executes the command
    # \brief It loads an existing datasource from the file
    def execute(self):
        if hasattr(self.receiver,'mdi'):
            if self._ds is None:
                self._ds = LabeledObject("", None)
            else:    
                self._ds.instance = None

            self._dsEdit = DataSource()
            self._dsEdit.ids = self._ds.id
            self._dsEdit.directory = self.receiver.sourceList.directory
            if self._fpath:
                path = self._dsEdit.load(self._fpath)
            else:
                path = self._dsEdit.load()
                self._fpath = path
            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(**self.receiver.externalDSActions)     
            if path:   
                self._ds.name = self._dsEdit.name  
                self._ds.instance = self._dsEdit
            
                self.receiver.sourceList.addDataSource(self._ds,False)
            #               print  "ID", self._cp.id
 #               print "STAT", self._cp.id in self.receiver.componentList.components
                self._dsEdit.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)                  

                subwindow = self.receiver.subWindow(
                    self._ds.instance, self.receiver.mdi.subWindowList())
                if subwindow:
                    self.receiver.mdi.setActiveSubWindow(subwindow) 
                    self._ds.instance.dialog.setSaveFocus()
                else:    
 #               print "create"
                    self._subwindow = self.receiver.mdi.addSubWindow(self._dsEdit.dialog)
                    self._subwindow.resize(440,480)
                    self._dsEdit.dialog.setSaveFocus()
                    self._dsEdit.dialog.show()
                #                self._cpEdit.dialog.setAttribute(Qt.WA_DeleteOnClose)
                    self._ds.instance = self._dsEdit 



#                self._subwindow = self.receiver.mdi.addSubWindow(self._dsEdit)
#                self._subwindow.resize(640,560)
                    
#            self._component.setAttribute(Qt.WA_DeleteOnClose)
                self._dsEdit.dialog.show()
                print "EXEC dsourceOpen"


    ## unexecutes the command
    # \brief It removes the loaded datasource from the datasource list
    def unexecute(self):
        if hasattr(self._ds, "instance"):
            if self._fpath:

                if hasattr(self._ds,'instance'):
                    subwindow = self.receiver.subWindow(
                        self._ds.instance, self.receiver.mdi.subWindowList())
                    if subwindow:
                        self.receiver.mdi.setActiveSubWindow(subwindow) 
                        self.receiver.mdi.closeActiveSubWindow() 

                self.receiver.sourceList.removeDataSource(self._ds, False)
                self._ds.instance = None
            
        print "UNDO dsourceOpen"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceOpen(self.receiver, self.slot) 



## Command which removes the current component from the component list
class ComponentRemove(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._wList = False
        

    ## executes the command
    # \brief It removes the current component from the component list
    def execute(self):
        
        if self._cp is not None:
            self.receiver.componentList.removeComponent(self._cp, False)
        else:
            self._cp = self.receiver.componentList.currentListComponent()
            if self._cp is None:                
                QMessageBox.warning(self.receiver, "Component not selected", 
                                    "Please select one of the components")            
            else:
                self.receiver.componentList.removeComponent(self._cp, True)
            
        if hasattr(self._cp,"instance"):
            subwindow = self.receiver.subWindow(
                self._cp.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self._wList = True
                self.receiver.mdi.setActiveSubWindow(subwindow)
                self.receiver.mdi.closeActiveSubWindow()
            
            
        print "EXEC componentRemove"


    ## unexecutes the command
    # \brief It reloads the removed component from the component list
    def unexecute(self):
        if self._cp is not None:

            self.receiver.componentList.addComponent(self._cp, False)
            if self._cp.instance is None:
                self._cp.instance = Component()
                self._cp.instance.idc = self._cp.id
                self._cp.instance.directory = self.receiver.componentList.directory
                self._cp.instance.name = self.receiver.componentList.components[self._cp.id].name


            self._cp.instance.createGUI()
            self._cp.instance.addContextMenu(self.receiver.contextMenuActions)

            subwindow = self.receiver.subWindow(
                self._cp.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._cp.instance.dialog.setSaveFocus()
            else:    
                if not self._cp.instance.dialog:
                    self._cp.instance.createGUI()
                self._subwindow = self.receiver.mdi.addSubWindow(self._cp.instance.dialog)
                self._subwindow.resize(640,560)
                self._cp.instance.dialog.setSaveFocus()
                self._cp.instance.dialog.show()

            self._cp.instance.dialog.show()

            if hasattr(self._cp.instance,"connectExternalActions"):     
                self._cp.instance.connectExternalActions(**self.receiver.externalCPActions)      



        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()

                    



        print "UNDO componentRemove"




    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentRemove(self.receiver, self.slot) 


## Command which opens dialog with the current component 
class ComponentEdit(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
        
    ## executes the command
    # \brief It opens dialog with the current component 
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is None:                
            QMessageBox.warning(self.receiver, "Component not selected", 
                                "Please select one of the components")            
        else:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = Component()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle("%s [Component]*" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance 
                

            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(**self.receiver.externalCPActions) 


            subwindow = self.receiver.subWindow(
                self._cpEdit, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._cpEdit.reconnectSaveAction()
            else:    
                self._cpEdit.createGUI()

                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                if self._cpEdit.isDirty():
                    self._cpEdit.dialog.setWindowTitle("%s [Component]*" % self._cp.name)
                else:
                    self._cpEdit.dialog.setWindowTitle("%s [Component]" % self._cp.name)
                     
                self._cpEdit.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._cpEdit.dialog)
                self._subwindow.resize(640,560)
                self._cpEdit.dialog.show()
                #                self._cpEdit.dialog.setAttribute(Qt.WA_DeleteOnClose)
            self._cp.instance = self._cpEdit 

            
        print "EXEC componentEdit"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentEdit"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentEdit(self.receiver, self.slot) 




## Command which saves with the current component in the file
class ComponentSave(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._cpEdit = None
        
    ## executes the command
    # \brief It saves with the current component in the file
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is None:
            QMessageBox.warning(self.receiver, "Component not selected", 
                                "Please select one of the components")            
        else:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = Component()
                self._cpEdit.idc = self._cp.id
                self._cpEdit.directory = self.receiver.componentList.directory
                self._cpEdit.name = self.receiver.componentList.components[self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle("%s [Component]" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance 
                
            if hasattr(self._cpEdit,"connectExternalActions"):     
                self._cpEdit.connectExternalActions(**self.receiver.externalCPActions)




            subwindow = self.receiver.subWindow(
                self._cpEdit, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
            else:    
                self._subwindow = self.receiver.mdi.addSubWindow(self._cpEdit.dialog)
                self._subwindow.resize(640,560)
                self._cpEdit.dialog.show()
                #                self._cpEdit.dialog.setAttribute(Qt.WA_DeleteOnClose)
            self._cp.instance = self._cpEdit 

            if self._cpEdit.save():
                self._cp.savedName = self._cp.name
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()

            
        print "EXEC componentSave"

    ## unexecutes the command
    # \brief It populates the component list
    def unexecute(self):
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()
        print "UNDO componentSave"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentSave(self.receiver, self.slot) 



## Command which saves all components in the file
class ComponentSaveAll(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It saves all components in the file
    def execute(self):
            
        for icp in self.receiver.componentList.components.keys():
            cp = self.receiver.componentList.components[icp]
            if cp.instance is None:
                #                self._cpEdit = FieldWg()  
                cpEdit = Component()
                cpEdit.idc = cp.id
                cpEdit.directory = self.receiver.componentList.directory
                cpEdit.name = self.receiver.componentList.components[cp.id].name
                cpEdit.createGUI()
                cpEdit.addContextMenu(self.receiver.contextMenuActions)
                cpEdit.createHeader()
                cpEdit.dialog.setWindowTitle("%s [Component]" % cp.name)
                cp.instance = cpEdit

            if cp.instance is not None:
                cp.instance.merge()    
                cp.instance.save()    

        print "EXEC componentSaveAll"


    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentSaveAll"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentSaveAll(self.receiver, self.slot) 





## Command which saves all components in the file
class ServerStoreAllComponents(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It saves all components in the file
    def execute(self):
            
        for icp in self.receiver.componentList.components.keys():
            cp = self.receiver.componentList.components[icp]
            if cp.instance is None:
                #                self._cpEdit = FieldWg()  
                cpEdit = Component()
                cpEdit.idc = cp.id
                cpEdit.directory = self.receiver.componentList.directory
                cpEdit.name = self.receiver.componentList.components[cp.id].name
                cpEdit.createGUI()
                cpEdit.addContextMenu(self.receiver.contextMenuActions)
                cpEdit.createHeader()
                cpEdit.dialog.setWindowTitle("%s [Component]" % cp.name)
                cp.instance = cpEdit

            try:
                cp.instance.merge()    
                xml = cp.instance.get()    
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )
                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.storeComponent(cp.instance.name, xml)
                cp.instance.savedXML = xml
                cp.savedName = cp.name
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in storing the component", unicode(e))
        if hasattr(cp,"id"):
            self.receiver.componentList.populateComponents(cp.id)
        else:
            self.receiver.componentList.populateComponents()


        print "EXEC componentStoreAll"


    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentStoreAll"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerStoreAllComponents(self.receiver, self.slot) 



## Command which saves the current components in the file with a different name
class ComponentSaveAs(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        ## new name of component
        self.name = None
        ## directory of the component file
        self.directory = None

        self._cp = None
        self._pathName = None
        

    ## executes the command
    # \brief It saves the current components in the file with a different name
    def execute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is None:
            QMessageBox.warning(self.receiver, "Component not selected", 
                                "Please select one of the components")            
        else:
            if self._cp.instance is not None:
                self._pathFile = self._cp.instance.getNewName() 
                fi = QFileInfo(self._pathFile)
                self.name = unicode(fi.fileName())
                if self.name[-4:] == '.xml':
                    self.name = self.name[:-4]
                self.directory = unicode(fi.dir().path())

        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()
        print "EXEC componentSaveAs"

    ## unexecutes the command
    # \brief It populates the Component list
    def unexecute(self):
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()
        print "UNDO componentSaveAs"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentSaveAs(self.receiver, self.slot) 



## Command which changes the current component file directory
class ComponentChangeDirectory(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It changes the current component file directory
    def execute(self):
        if QMessageBox.question(self.receiver, "Component - Change Directory",
                                "All unsaved components will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return


        path = unicode(QFileDialog.getExistingDirectory(
                self.receiver, "Open Directory",
                self.receiver.cpDirectory,
                QFileDialog.ShowDirsOnly or QFileDialog.DontResolveSymlinks))

        if not path:
            return
        subwindows = self.receiver.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), ComponentDlg):
                    self.receiver.mdi.setActiveSubWindow(subwindow)
                    self.receiver.mdi.closeActiveSubWindow()



        self.receiver.componentList.components = {} 
        self.receiver.cpDirectory = path
        self.receiver.updateStatusBar()
        self.receiver.componentList.directory = path

        self.receiver.loadComponents()

        print "EXEC componentChangeDirectory"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentChangeDirectory"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentChangeDirectory(self.receiver, self.slot) 



## Command which copies the current datasource into the clipboard
class DataSourceCopy(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        
        
    ## executes the command
    # \brief It copies the current datasource into the clipboard
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
                self._ds.instance.copyToClipboard()
            else:
                self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()


            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
                

            self._newstate = self._ds.instance.getState() 
            
        print "EXEC dsourceCopy"

    ## unexecutes the command
    # \brief It updates state of datasource to the old state
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') and  self._ds.instance is not None:
        
            self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._oldstate)
            self.receiver.sourceList.datasources[self._ds.id].instance.updateForm()


            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
            
            
        print "UNDO dsourceCopy"
        

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceCopy(self.receiver, self.slot) 
        




## Command which moves the current datasource into the clipboard
class DataSourceCut(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        
        
    ## executes the command
    # \brief It moves the current datasource into the clipboard
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
                self._ds.instance.copyToClipboard()
                self._ds.instance.clear()
#                self._ds.instance.createNodes()
                self._ds.instance.updateForm()
                self._ds.instance.dialog.show()
            else:
                self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
                
                

            self._newstate = self._ds.instance.getState() 
        if hasattr(self._ds ,"id"):
            self.receiver.sourceList.populateDataSources(self._ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
            
        print "EXEC dsourceCut"

    ## unexecutes the command
    # \brief It copy back the removed datasource
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') and  self._ds.instance is not None:
        
            self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._oldstate)
            self.receiver.sourceList.datasources[self._ds.id].instance.updateForm()
#            self.receiver.sourceList.datasources[self._ds.id].instance.updateNode()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
            
        if hasattr(self._ds ,"id"):
            self.receiver.sourceList.populateDataSources(self._ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
            
        print "UNDO dsourceCut"
        

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceCut(self.receiver, self.slot) 
        




## Command which pastes the current datasource from the clipboard
class DataSourcePaste(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        
        
    ## executes the command
    # \brief It pastes the current datasource from the clipboard
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
                self._ds.instance.clear()
                if not self._ds.instance.copyFromClipboard():
                    QMessageBox.warning(self.receiver, "Pasting item not possible", 
                                        "Probably clipboard does not contain datasource")            
                    
                self._ds.instance.updateForm()
#                self._ds.instance.updateNode()
                self._ds.instance.dialog.setFrames(self._ds.instance.dataSourceType)

#                self._ds.instance.updateForm()
                self._ds.instance.dialog.show()
            else:
                self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._newstate)
                self._ds.instance.updateForm()
#                self._ds.instance.updateNode()

            self._newstate = self._ds.instance.getState() 

            self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._oldstate)
            self._ds.instance.updateNode()

            
            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createDialog()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
                                

            
            if hasattr(self._ds ,"id"):
                self.receiver.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.sourceList.populateDataSources()
        print "EXEC dsourcePaste"

    ## unexecutes the command
    # \brief It remove the pasted datasource
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') and  self._ds.instance is not None:
        
            self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._oldstate)
            self.receiver.sourceList.datasources[self._ds.id].instance.updateForm()


            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
            
            if hasattr(self._ds ,"id"):
                self.receiver.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.sourceList.populateDataSources()
            
        print "UNDO dsourcePaste"
        

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourcePaste(self.receiver, self.slot) 
        



## Command which applies the changes from the form for the current datasource 
class DataSourceApply(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._oldstate = None
        self._newstate = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current datasource  
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            
        if self._ds.instance is None:
            #                self._dsEdit = FieldWg()  
            self._ds.instance  = DataSource()
            self._ds.instance.ids = self._ds.id
            self._ds.instance.directory = self.receiver.sourceList.directory
            self._ds.instance.name = self.receiver.sourceList.datasources[self._ds.id].name
        if not self._ds.instance.dialog:
            self._ds.instance.createDialog()
            self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
            
            if hasattr(self._ds.instance,"connectExternalActions"):     
                self._ds.instance.connectExternalActions(**self.receiver.externalDSActions)
            self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
            self._subwindow.resize(440,480)
            self._ds.instance.dialog.show()

    
        if self._ds is not None and self._ds.instance is not None:
            if self._newstate is None:
                if self._oldstate is None:
                    self._oldstate = self._ds.instance.getState() 
            else:
                self.receiver.sourceList.datasources[self._ds.id].instance.setState(
                    self._newstate)
                self._ds.instance.updateForm()



            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction()
            else:    
                self._ds.instance.createGUI()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [Component]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [Component]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._ds.instance.dialog.show()
    
                    
            self._ds.instance.apply()    
            self._newstate = self._ds.instance.getState() 
            
            
            if hasattr(self._ds ,"id"):
                self.receiver.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.sourceList.populateDataSources()
        else:
            QMessageBox.warning(self.receiver, "DataSource not created", 
                                "Please edit one of the datasources")            
            
        print "EXEC dsourceApply"


    ## unexecutes the command
    # \brief It recovers the old state of the current datasource
    def unexecute(self):
        if self._ds is not None and hasattr(self._ds,'instance') and  self._ds.instance is not None:
        
            self.receiver.sourceList.datasources[self._ds.id].instance.setState(self._oldstate)
            print "print", self.receiver.sourceList.datasources[self._ds.id].instance.get()
            self.receiver.sourceList.datasources[self._ds.id].instance.apply()
            print "state", self._oldstate
            print "print2", self.receiver.sourceList.datasources[self._ds.id].instance.get()


            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self.receiver.sourceList.datasources[self._ds.id].instance.updateForm()
                self._ds.instance.reconnectSaveAction()
                
            else:    
                self._ds.instance.createDialog()

                self.receiver.sourceList.datasources[self._ds.id].instance.updateForm()
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
            if self._ds.instance.isDirty():
                print "DIRTY"
                self._ds.instance.dialog.setWindowTitle("%s [Component]*" % self._ds.name)
            else:
                print "NOT DIRTY"
                self._ds.instance.dialog.setWindowTitle("%s [Component]" % self._ds.name)
            self._ds.instance.dialog.show()
    

            if hasattr(self._ds ,"id"):
                self.receiver.sourceList.populateDataSources(self._ds.id)
            else:
                self.receiver.sourceList.populateDataSources()
            
            
        print "UNDO dsourceApply"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceApply(self.receiver, self.slot) 






## Command which saves all the datasources in files
class DataSourceSaveAll(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It saves all the datasources in files
    def execute(self):
            
        for ids in self.receiver.sourceList.datasources.keys():
            ds = self.receiver.sourceList.datasources[ids]
            if ds.instance is None:
                dsEdit = DataSource()
                dsEdit.ids = ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = self.receiver.sourceList.datasources[ds.id].name
                ds.instance = dsEdit 

            if ds.instance is not None: 
                if ds.instance.save():
                    ds.savedName = ds.name

        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()


        print "EXEC dsourceSaveAll"

    ## executes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceSaveAll"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceSaveAll(self.receiver, self.slot) 




## Command which saves all the datasources in files
class ServerStoreAllDataSources(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It saves all the datasources in files
    def execute(self):
            
        for ids in self.receiver.sourceList.datasources.keys():
            ds = self.receiver.sourceList.datasources[ids]
            if ds.instance is None:
                dsEdit = DataSource()
                dsEdit.ids = ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = self.receiver.sourceList.datasources[ds.id].name
                ds.instance = dsEdit 
            print "Store", ds.instance.name

            try:
                xml = ds.instance.get()    
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )
                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                if ds.instance.name:
                    self.receiver.configServer.storeDataSource(ds.instance.dataSourceName, xml)
                else:
                    self.receiver.configServer.storeDataSource(ds.instance.name, xml)
                ds.instance.savedXML = xml
                ds.savedName = ds.name
            except Exception, e:
                QMessageBox.warning(self.receiver, "Error in datasource storing", unicode(e))


        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()


        print "EXEC dsourceStoreAll"

    ## executes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceStoreAll"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ServerStoreAllDataSources(self.receiver, self.slot) 


## Command which saves the current datasource in files
class DataSourceSave(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        
        
    ## executes the command
    # \brief It saves the current datasource in files
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            

        if self._ds is not None and hasattr(self._ds,"instance"):
            if self._ds.instance is None:
                dsEdit = DataSource()
                dsEdit.ids =self._ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._ds.instance = dsEdit 

            if self._ds.instance.save():
                self._ds.savedName = self._ds.name


        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
            
        print "EXEC dsourceSave"

    ## unexecutes the command
    # \brief It populates the datasource list
    def unexecute(self):
        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds ,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()
        print "UNDO dsourceSave"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceSave(self.receiver, self.slot) 






## Command which saves the current datasource in files with a different name
class DataSourceSaveAs(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        ## new datasource name
        self.name = None
        ## new file directory
        self.directory = None

        self._ds = None
        self._pathName = None
        

    ## executes the command
    # \brief It saves the current datasource in files with a different name
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            
        else:
            if self._ds.instance is None:
                dsEdit = DataSource()
                dsEdit.ids =self._ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._ds.instance = dsEdit 
            
            if self._ds.instance is not None:
                self._pathFile = self._ds.instance.getNewName() 
                fi = QFileInfo(self._pathFile)
                self.name = unicode(fi.fileName())
                if self.name[-4:] == '.xml':
                    self.name = self.name[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]

                self.directory = unicode(fi.dir().path())


            
        print "EXEC dsourceSaveAs"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceSaveAs"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceSaveAs(self.receiver, self.slot) 




## Command which changes the current file directory with datasources
class DataSourceChangeDirectory(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It changes the current file directory with datasources
    def execute(self):
        if QMessageBox.question(self.receiver, "DataSource - Change Directory",
                                "All unsaved datasources will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return


        path = unicode(QFileDialog.getExistingDirectory(
                self.receiver, "Open Directory",
                self.receiver.dsDirectory,
                QFileDialog.ShowDirsOnly or QFileDialog.DontResolveSymlinks))

        if not path:
            return

        subwindows = self.receiver.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), CommonDataSourceDlg):
                    self.receiver.mdi.setActiveSubWindow(subwindow)
                    self.receiver.mdi.closeActiveSubWindow()



        self.receiver.sourceList.datasources = {} 
        self.receiver.dsDirectory = path
        self.receiver.updateStatusBar()
        self.receiver.sourceList.directory = path

        self.receiver.loadDataSources()

        print "EXEC dsourceChangeDirectory"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceChangeDirectory"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceChangeDirectory(self.receiver, self.slot) 




## Command which reloads the components from the current component directory into the component list
class ComponentReloadList(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It reloads the components from the current component directory into the component list
    def execute(self):
        if QMessageBox.question(self.receiver, "Component - Reload List",
                                "All unsaved components will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return

        
        subwindows = self.receiver.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(),ComponentDlg):
                    self.receiver.mdi.setActiveSubWindow(subwindow)
                    self.receiver.mdi.closeActiveSubWindow()

        self.receiver.componentList.components = {} 
        self.receiver.loadComponents()

        print "EXEC componentReloadList"


    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentReloadList"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentReloadList(self.receiver, self.slot) 


## Command which takes the datasources from the current component
class ComponentTakeDataSources(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
       

    ## executes the command
    # \brief It reloads the datasources from the current datasource directory into the datasource list
    def execute(self):
#        if QMessageBox.question(self.receiver, "DataSource - Take Data Sources",
#                                "Unsaved datasources may be overwritten. Would you like to proceed ?".encode(),
#                                QMessageBox.No | QMessageBox.Yes,
#                                QMessageBox.Yes  ) == QMessageBox.No:
#            return

        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is None:
            QMessageBox.warning(self.receiver, "Component not selected", 
                                "Please select one of the components")            
        else:
            if self._cp.instance is not None:
                datasources = self._cp.instance.getDataSources()
        
                dialogs = self.receiver.mdi.subWindowList()
                if dialogs:
                    for dialog in dialogs:
                        if isinstance(dialog, DataSourceDlg):
                            self.receiver.mdi.setActiveSubWindow(dialog)
                            self.receiver.mdi.closeActiveSubWindow()
        
                self.receiver.setDataSources(datasources, new = True)

        print "EXEC componentTakeDataSources"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentTakeDataSources"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentTakeDataSources(self.receiver, self.slot) 




## Command which takes the datasources from the current component
class ComponentTakeDataSource(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._ids = None
        self._ds = None
        self._lids = None

    ## executes the command
    # \brief It reloads the datasources from the current datasource directory into the datasource list
    def execute(self):
#        if QMessageBox.question(self.receiver, "DataSource - Take Data Sources",
#                                "Unsaved datasources may be overwritten. Would you like to proceed ?".encode(),
#                                QMessageBox.No | QMessageBox.Yes,
#                                QMessageBox.Yes  ) == QMessageBox.No:
#            return

        if not self._lids:
            self._lids =  self.receiver.sourceList.datasources.itervalues().next().id \
                if len(self.receiver.sourceList.datasources) else None
        if self._ids and self._ds:       
            self.receiver.sourceList.addDataSource(self._ds)
#            self.receiver.sourceList.datasources[self._ids] = self._ds
            self.receiver.sourceList.populateDataSources(self._ids)
          
        else:    
            if self._cp is None:
                self._cp = self.receiver.componentList.currentListComponent()
            if self._cp is not None:
                if self._cp.instance is not None:

                    datasource = self._cp.instance.getCurrentDataSource()
                    dialogs = self.receiver.mdi.subWindowList()
                    if dialogs:
                        for dialog in dialogs:
                            if isinstance(dialog, DataSourceDlg):
                                self.receiver.mdi.setActiveSubWindow(dialog)
                                self.receiver.mdi.closeActiveSubWindow()
        
                    self._ids = self.receiver.setDataSources(datasource, new = True)
                    self._ds = self.receiver.sourceList.datasources[self._ids]
                    self.receiver.sourceList.populateDataSources(self._ids)
        print "EXEC componentTakeDataSource"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO componentTakeDataSource"
        

        self.receiver.sourceList.removeDataSource(self._ds, False)
        if hasattr(self._ds,'instance'):
            subwindow = self.receiver.subWindow(self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self.receiver.mdi.closeActiveSubWindow() 


        self.receiver.sourceList.populateDataSources(self._lids)

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentTakeDataSource(self.receiver, self.slot) 




## Command which reloads the datasources from the current datasource directory into the datasource list
class DataSourceReloadList(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It reloads the datasources from the current datasource directory into the datasource list
    def execute(self):
        if QMessageBox.question(self.receiver, "DataSource - Reload List",
                                "All unsaved datasources will be lost. Would you like to proceed ?".encode(),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes ) == QMessageBox.No :
            return


        subwindows = self.receiver.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                if isinstance(subwindow.widget(), CommonDataSourceDlg):
                    self.receiver.mdi.setActiveSubWindow(subwindow)
                    self.receiver.mdi.closeActiveSubWindow()
                    
        self.receiver.sourceList.datasources = {} 
        self.receiver.loadDataSources()

        print "EXEC dsourceReloadList"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceReloadList"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceReloadList(self.receiver, self.slot) 








## Command which changes the current component in the list
class ComponentListChanged(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver,slot):
        Command.__init__(self, receiver, slot)
        ## new item
        self.item = None
        ## new directory
        self.directory = None
        ## new component name
        self.name = None

        self._cp = None
        self._oldName = None
        self._oldDirectory = None
        

    ## executes the command
    # \brief It changes the current component in the list
    def execute(self):
        if self.item is not None or self.name is not None:
            if self.name is None:
                self.name = unicode(self.item.text())
            if self._cp is None:
                self._cp, self._oldName = self.receiver.componentList.listItemChanged(self.item, self.name)
            else:
                self._cp.name = self.name
                
            self.receiver.componentList.populateComponents(self._cp.id)
            if self._cp.instance is not None:
                self._oldDirectory = self._cp.instance.directory 
                self._cp.instance.setName(self.name, self.directory)
            else:
                self._oldDirectory =  self.receiver.componentList.directory 


        cp = self.receiver.componentList.currentListComponent()
        if hasattr(cp,"id"):
            self.receiver.componentList.populateComponents(cp.id)
        else:
            self.receiver.componentList.populateComponents()
              
        print "EXEC componentChanged"


    ## unexecutes the command
    # \brief It changes back the current component in the list
    def unexecute(self):
        if self._cp is not None:
            self._cp.name = self._oldName 
            self.receiver.componentList.addComponent(self._cp, False)
            if self._cp.instance is not None:
                self._cp.instance.setName(self._oldName, self._oldDirectory)

        cp = self.receiver.componentList.currentListComponent()
        if hasattr(cp,"id"):
            self.receiver.componentList.populateComponents(cp.id)
        else:
            self.receiver.componentList.populateComponents()

        print "UNDO componentChanged"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentListChanged(self.receiver, self.slot) 
    


## Command which creates a new datasource
class DataSourceNew(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        
    ## executes the command
    # \brief It creates a new datasource
    def execute(self):
        if self._ds is None:
            self._ds = LabeledObject("", None)
        else:
            self._ds.instance = None
        self.receiver.sourceList.addDataSource(self._ds)
        print "EXEC dsourceNew"

    ## unexecutes the command
    # \brief It removes the added datasource
    def unexecute(self):
        if self._ds is not None:
            self.receiver.sourceList.removeDataSource(self._ds, False)


            if hasattr(self._ds,'instance'):
                subwindow = self.receiver.subWindow(self._ds.instance, self.receiver.mdi.subWindowList())
                if subwindow:
                    self.receiver.mdi.setActiveSubWindow(subwindow) 
                    self.receiver.mdi.closeActiveSubWindow() 

        print "UNDO dsourceNew"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceNew(self.receiver, self.slot) 






## Command which opens the dialog with the current datasource
class DataSourceEdit(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver,slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._dsEdit = None
        
        
    ## executes the command
    # \brief It opens the dialog with the current datasource
    def execute(self):
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListDataSource()
        if self._ds is None:
            QMessageBox.warning(self.receiver, "DataSource not selected", 
                                "Please select one of the datasources")            
        else:
            if self._ds.instance is None:
                #                self._dsEdit = FieldWg()  
                self._dsEdit = DataSource()
                
                self._dsEdit.ids = self._ds.id
                self._dsEdit.directory = self.receiver.sourceList.directory
                self._dsEdit.name = self.receiver.sourceList.datasources[self._ds.id].name
                self._dsEdit.createDialog()
                self._dsEdit.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                self._ds.instance = self._dsEdit 
            else:
                if not self._ds.instance.dialog:
                    self._ds.instance.createDialog()
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                self._dsEdit = self._ds.instance 
                
            if hasattr(self._dsEdit,"connectExternalActions"):     
                self._dsEdit.connectExternalActions(**self.receiver.externalDSActions)

            subwindow = self.receiver.subWindow(
                self._dsEdit, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.reconnectSaveAction() 
            else:    
                if self._ds.instance.dialog is None:
                    self._ds.instance.createDialog()

                if self._ds.instance.isDirty():
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]*" % self._ds.name)
                else:
                    self._ds.instance.dialog.setWindowTitle("%s [DataSource]" % self._ds.name)
                     
                self._ds.instance.reconnectSaveAction()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(440,480)
                self._dsEdit.dialog.show()
                #                self._dsEdit.setAttribute(Qt.WA_DeleteOnClose)
                    


            
        print "EXEC dsourceEdit"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO dsourceEdit"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceEdit(self.receiver, self.slot) 







## Command which removes the current datasource from the datasource list
class DataSourceRemove(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._ds = None
        self._wList = False
        
    ## executes the command
    # \brief It removes the current datasource from the datasource list
    def execute(self):
        
        if self._ds is not None:
            self.receiver.sourceList.removeDataSource(self._ds, False)
        else:
            self._ds = self.receiver.sourceList.currentListDataSource()
            if self._ds is None:
                QMessageBox.warning(self.receiver, "DataSource not selected", 
                                    "Please select one of the datasources")            
            else:
                self.receiver.sourceList.removeDataSource(self._ds, True)
            

        if hasattr(self._ds,"instance"):
            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self._wList = True
                self.receiver.mdi.setActiveSubWindow(subwindow)
                self.receiver.mdi.closeActiveSubWindow()
            
            
        print "EXEC dsourceRemove"

    ## unexecutes the command
    # \brief It adds the removes datasource into the datasource list
    def unexecute(self):
        if self._ds is not None:

            self.receiver.sourceList.addDataSource(self._ds, False)

            self._ds.instance.createGUI()

            subwindow = self.receiver.subWindow(
                self._ds.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
                self._ds.instance.dialog.setSaveFocus()
            else:    
                self._ds.instance.createDialog()
                self._subwindow = self.receiver.mdi.addSubWindow(self._ds.instance.dialog)
                self._subwindow.resize(640,560)
                self._ds.instance.dialog.setSaveFocus()
                self._ds.instance.dialog.show()
                    
            self._ds.instance.dialog.show()
        print "UNDO dsourceRemove"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceRemove(self.receiver, self.slot) 



## Command which performs change of  the current datasource 
class DataSourceListChanged(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        ## new item
        self.item = None
        ## new datasource name
        self.name = None
        ## new datasource directory
        self.directory = None

        self._ds = None
        self._oldName = None
        self._oldDirectory = None
        

        
    ## executes the command
    # \brief It performs change of  the current datasource 
    def execute(self):
        if self.item is not None or self.name is not None:
            if self.name is None:
                self.name = unicode(self.item.text())
            if self._ds is None:
                self._ds, self._oldName = self.receiver.sourceList.listItemChanged(self.item, self.name)
            else:
                self._ds.name = self.name
             
            self.receiver.sourceList.populateDataSources(self._ds.id)
            if self._ds.instance is not None:
                self._oldDirectory = self._ds.instance.directory 
                self._ds.instance.setName(self.name, self.directory)
            else:
                self._oldDirectory =  self.receiver.sourceList.directory 

        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()

        print "EXEC dsourceChanged"

    ## unexecutes the command
    # \brief It changes back the current datasource 
    def unexecute(self):
        if self._ds is not None:
            self._ds.name = self._oldName 
            self.receiver.sourceList.addDataSource(self._ds, False)
            if self._ds.instance is not None:
                self._ds.instance.setName(self._oldName, self._oldDirectory)


        ds = self.receiver.sourceList.currentListDataSource()
        if hasattr(ds,"id"):
            self.receiver.sourceList.populateDataSources(ds.id)
        else:
            self.receiver.sourceList.populateDataSources()

        print "UNDO dsourceChanged"



    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceListChanged(self.receiver, self.slot) 
    




## Command which is performed during closing the Component Designer
class CloseApplication(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    ## executes the command
    # \brief It is performed during closing the Component Designer
    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self.receiver.close()
            print "EXEC closeApp"

    ## executes the command
    # \brief It does nothing
    def unexecute(self):
        print "UNDO closeApp"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return CloseApplication(self.receiver, self.slot) 



## Empty undo command. It is no need to implement it 
class UndoCommand(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)


    ## executes the command
    # \brief It does nothing
    def execute(self):
        print "EXEC undo"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        pass


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return UndoCommand(self.receiver, self.slot) 

## Empty undo command. It is no need to implement it 
class RedoCommand(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)

    ## executes the command
    # \brief It does nothing
    def execute(self):
        print "EXEC redo"

    ## unexecutes the command
    # \brief It does nothing
    def unexecute(self):
        pass


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return RedoCommand(self.receiver, self.slot) 






## Abstract Command which helps in defing commands related to Component item operations
class ComponentItemCommand(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver, slot)
        self._cp = None
        self._oldstate = None
        self._index = None
        self._newstate = None

    ## helps to construct the execute component item command as a pre-executor
    # \brief It stores the old states of the current component
    def preExecute(self):
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListComponent()
        if self._cp is not None:
            if self._oldstate is None and hasattr(self._cp,"instance") \
                    and hasattr(self._cp.instance,"setState"):
                self._oldstate = self._cp.instance.getState() 
                self._index = self._cp.instance.currentIndex()

            else:
                QMessageBox.warning(self.receiver, "Component not created", 
                                    "Please edit one of the components")            
                
        else:
            QMessageBox.warning(self.receiver, "Component not selected", 
                                "Please select one of the components")            

    
    ## helps to construct the execute component item command as a post-executor
    # \brief It stores the new states of the current component
    def postExecute(self):    
        if self._cp is not None:
            if self._cp.instance is None:
                self._cp.instance = Component()
                self._cp.instance.idc = self._cp.id
                self._cp.instance.directory = self.receiver.componentList.directory
                self._cp.instance.name = self.receiver.componentList.components[self._cp.id].name

            if self._newstate is None and hasattr(self._cp.instance, "getState"):
                self._newstate = self._cp.instance.getState() 
            else:
                if hasattr(self.receiver.componentList.components[self._cp.id].instance,"setState"): 
                    self.receiver.componentList.components[self._cp.id].instance.setState(self._newstate)



                subwindow = self.receiver.subWindow(
                    self._cp.instance, self.receiver.mdi.subWindowList())

                if subwindow:
                    self.receiver.mdi.setActiveSubWindow(subwindow) 
                    self._cp.instance.reconnectSaveAction()
                else:    
                    self._cp.instance.createGUI()

                    self._cp.instance.addContextMenu(self.receiver.contextMenuActions)
                    if self._cp.instance.isDirty():
                        self._cp.instance.dialog.setWindowTitle("%s [Component]*" % self._cp.name)
                    else:
                        self._cp.instance.dialog.setWindowTitle("%s [Component]" % self._cp.name)
                     
                    self._cp.instance.reconnectSaveAction()
                    self._subwindow = self.receiver.mdi.addSubWindow(self._cp.instance.dialog)
                    self._subwindow.resize(640,560)

                    if hasattr(self._cp.instance.dialog,"show"):
                        self._cp.instance.dialog.show()

                if hasattr(self._cp.instance,"connectExternalActions"):     
                    self._cp.instance.connectExternalActions(**self.receiver.externalCPActions) 


        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()

        
    ## executes the command
    # \brief It execute pre- and post- executors
    def execute(self):
        if self._cp is None:
            self.preExecute()
    
        self.postExecute()


            
        print "EXEC componentItemCommand"

    ## helps to construct the unexecute component item command 
    # \brief It changes back the states of the current component to the old state
    def unexecute(self):
        if self._cp is not None and self._oldstate is not None:
            self.receiver.componentList.components[self._cp.id].instance.setState(self._oldstate)
            

            subwindow = self.receiver.subWindow(
                self._cp.instance, self.receiver.mdi.subWindowList())
            if subwindow:
                self.receiver.mdi.setActiveSubWindow(subwindow) 
            else:    
                if self._cp.instance is None:
                    self._cp.instance = Component()
                    self._cp.instance.idc = self._cp.id
                    self._cp.instance.directory = self.receiver.componentList.directory
                    self._cp.instance.name = self.receiver.componentList.components[self._cp.id].name
                if not self._cp.instance.dialog:
                    self._cp.instance.createGUI()
                self._subwindow = self.receiver.mdi.addSubWindow(self._cp.instance.dialog)
                self._subwindow.resize(640,560)

                self._cp.instance.dialog.show()
        self._cp.instance.reconnectSaveAction()
        if hasattr(self._cp,"id"):
            self.receiver.componentList.populateComponents(self._cp.id)
        else:
            self.receiver.componentList.populateComponents()

        print "UNDO componentItemComponent"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentItemCommand(self.receiver, self.slot) 



## Command which clears the whole current component
class ComponentClear(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)



    ## executes the command
    # \brief It clears the whole current component
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:                
                if QMessageBox.question(self.receiver, "Component - Clear",
                                        "Clear the component: %s ".encode() %  (self._cp.name),
                                        QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes ) == QMessageBox.No :
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    return


                if hasattr(self._cp,"instance"):
                    if self._cp.instance in self.receiver.mdi.subWindowList():
                        self._wList = True
                        self.receiver.mdi.setActiveSubWindow(self._cp.instance)
                    self._cp.instance.createHeader()            
                
                    newModel = ComponentModel(self._cp.instance.document, self._cp.instance._allAttributes)
                    self._cp.instance.view.setModel(newModel)

                    if hasattr(self._cp.instance,"connectExternalActions"):     
                        self._cp.instance.connectExternalActions(**self.receiver.externalCPActions) 


        self.postExecute()
            

        print "EXEC componentClear"



    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentClear(self.receiver, self.slot) 




## Command which loads sub-components into the current component tree from the file
class ComponentLoadComponentItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        ## 
        self._itemName = ""        
        
    ## executes the command
    # \brief It loads sub-components into the current component tree from the file
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None and self._cp.instance.view and  self._cp.instance.view.model():
                    if hasattr(self._cp.instance,"loadComponentItem"):
                        if not self._cp.instance.loadComponentItem(self._itemName):
                            QMessageBox.warning(self.receiver, "SubComponent not loaded", 
                                                "Please ensure that you have selected the proper items")            
                else:
                    QMessageBox.warning(self.receiver, "Component item not selected", 
                                        "Please select one of the component items")            
                        
        self.postExecute()
            
        print "EXEC componentLoadcomponentItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentLoadComponentItem(self.receiver, self.slot) 



## Command which moves the current component item into the clipboard
class ComponentRemoveItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver,slot)

        
    ## executes the command
    # \brief It moves the current component item into the clipboard
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None:
                    if hasattr(self._cp.instance,"removeSelectedItem"):
                       if not self._cp.instance.removeSelectedItem():
                           QMessageBox.warning(self.receiver, "Cutting item not possible", 
                                               "Please select another tree item") 
        self.postExecute()


            
        print "EXEC componentRemoveItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentRemoveItem(self.receiver, self.slot) 




## Command which copies the current component item into the clipboard
class ComponentCopyItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver,slot)

        
    ## executes the command
    # \brief It copies the current component item into the clipboard
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None:
                    if hasattr(self._cp.instance,"copySelectedItem"):
                        if not self._cp.instance.copySelectedItem():
                            QMessageBox.warning(self.receiver, "Copying item not possible", 
                                                "Please select another tree item") 
        self.postExecute()
            
        print "EXEC componentCopyItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentCopyItem(self.receiver, self.slot) 



## Command which pastes the component item from the clipboard into the current component tree
class ComponentPasteItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver,slot)

        
    ## executes the command
    # \brief It pastes the component item from the clipboard into the current component tree
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None:
                    if hasattr(self._cp.instance,"pasteItem"):
                        if not self._cp.instance.pasteItem():
                            QMessageBox.warning(self.receiver, "Pasting item not possible", 
                                                "Please select another tree item") 
        self.postExecute()
                            
        
        print "EXEC componentPasteItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentPasteItem(self.receiver, self.slot) 







## Command which moves the current, i.e. datasource or component item, into the clipboard
class CutItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver,slot)
        ## type of the cutting item with values: component of datasource
        self.type = None

        self._ds = DataSourceCut(receiver, slot)
        self._cp = ComponentRemoveItem(receiver, slot)

    ## executes the command
    # \brief It moves the current, i.e. datasource or component item, into the clipboard
    def execute(self):
        if self.type == 'component':
            self._cp.execute()
        elif self.type == 'datasource':
            self._ds.execute()

    ## unexecutes the command
    # \brief It adds back the current, i.e. datasource or component item
    def unexecute(self):
        if self.type == 'component':
            self._cp.unexecute()
        elif self.type == 'datasource':
            self._ds.unexecute()
        


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return CutItem(self.receiver, self.slot) 






## Command which copies the current item, i.e. datasource or component item, into the clipboard
class CopyItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver,slot)
        ## type of the coping item with values: component of datasource
        self.type = None

        self._ds = DataSourceCopy(receiver, slot)
        self._cp = ComponentCopyItem(receiver, slot)


    ## executes the command
    # \brief It copies the current item, i.e. datasource or component item, into the clipboard
    def execute(self):
        if self.type == 'component':
            self._cp.execute()
        elif self.type == 'datasource':
            self._ds.execute()


    ## unexecutes the command
    # \brief It unexecutes copy commands for datasources or components
    def unexecute(self):
        if self.type == 'component':
            self._cp.unexecute()
        elif self.type == 'datasource':
            self._ds.unexecute()
        


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return CopyItem(self.receiver, self.slot) 



## Command which pastes the current item from the clipboard into the current dialog, i.e. the current datasource or the current component item tree
class PasteItem(Command):
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver,slot)
        ## type of the pasting item with values: component of datasource
        self.type = None

        self._ds = DataSourcePaste(receiver, slot)
        self._cp = ComponentPasteItem(receiver, slot)

    ## executes the command
    # \brief It pastes the current item from the clipboard into the current dialog, i.e. the current datasource or the current component item tree
    def execute(self):
        if self.type == 'component':
            self._cp.execute()
        elif self.type == 'datasource':
            self._ds.execute()

    ## unexecutes the command
    # \brief It unexecutes paste commands for datasources or components
    def unexecute(self):
        if self.type == 'component':
            self._cp.unexecute()
        elif self.type == 'datasource':
            self._ds.unexecute()
        


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return PasteItem(self.receiver, self.slot) 




## Command which stores the current component in the comfiguration server or in the file
class ComponentCollect(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver,slot)
        self._type = None
        self._file = ComponentSave(receiver, slot)
        self._server = ServerStoreComponent(receiver, slot)

    ## executes the command
    # \brief It  stores the current component in the comfiguration server or in the file
    def execute(self):
        if self._type is None:
            
            if self.receiver.configServer and self.receiver.configServer.connected:
                self._type = 'Server'
            else:
                self._type = 'File'
        if self._type == 'File':
            self._file.execute()
        elif self._type == 'Server':
            self._server.execute()

    ## unexecutes the command
    # \brief It unexecutes ComponentCollect commands on the configuration server or on the file system
    def unexecute(self):
        if self._type == 'File':
            self._file.unexecute()
        elif self._type == 'Server':
            self._server.unexecute()
        


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentCollect(self.receiver, self.slot) 




## Command which stores the current datasource in the comfiguration server or in the file
class DataSourceCollect(Command):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        Command.__init__(self, receiver,slot)
        self._type = None
        self._file = DataSourceSave(receiver, slot)
        self._server = ServerStoreDataSource(receiver, slot)

    ## executes the command
    # \brief It stores the current datasource in the comfiguration server or in the file
    def execute(self):
        if self._type is None:
            if self.receiver.configServer and self.receiver.configServer.connected:
                self._type = 'Server'
            else:
                self._type = 'File'
        if self._type == 'File':
            self._file.execute()
        elif self._type == 'Server':
            self._server.execute()

    ## unexecutes the command
    # \brief It unexecutes DataSourceCollect commands on the configuration server or on the file system
    def unexecute(self):
        if self._type == 'File':
            self._file.unexecute()
        elif self._type == 'Server':
            self._server.unexecute()
        


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return DataSourceCollect(self.receiver, self.slot) 


## Command which merges the current component
class ComponentMerge(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        
    ## executes the command
    # \brief It merges the current component
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:                
                if hasattr(self._cp.instance,"merge"):
                    self._cp.instance.merge()
        
        self.postExecute()
            
            
        print "EXEC componentMerge"



    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentMerge(self.receiver, self.slot) 





## Command which creates a new item in the current component tree
class ComponentNewItem(ComponentItemCommand):
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        ## name of the new component item
        self.itemName = ""
        self._index = None
        self._childIndex = None
        self._child = None
                    

    ## executes the command
    # \brief It creates a new item in the current component tree
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is None:                
                    QMessageBox.warning(self.receiver, "Component Item not selected", 
                                        "Please select one of the component Items")            
                if hasattr(self._cp.instance,"addItem"):
                    self._child = self._cp.instance.addItem(self.itemName)
                    if self._child:
                        self._index = self._cp.instance.view.currentIndex()
                            
                        if  self._index.column() != 0 and self._index.row() is not None:
                            
                            self._index = self._cp.instance.view.model().index(self._index.row(), 0, self._index.parent())
                        row = self._cp.instance.dialog.getWidgetNodeRow(self._child)
                        if row is not None:
                            self._childIndex = self._cp.instance.view.model().index(row, 0, self._index)
                            self._cp.instance.view.setCurrentIndex(self._childIndex)
                            self._cp.instance.tagClicked(self._childIndex)
                    else:
                        QMessageBox.warning(self.receiver, "Creating the %s Item not possible" % self.itemName, 
                                            "Please select another tree or new item ")                                
            if self._child and self._index.isValid():
                if self._index.isValid():
                    finalIndex = self._cp.instance.view.model().index(
                        self._index.parent().row(), 2, self._index.parent().parent())
                else:
                    finalIndex = self._cp.instance.view.model().index(
                        0, 2, self._index.parent().parent())
                    
                self._cp.instance.view.model().emit(
                    SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self._index, self._index)
                self._cp.instance.view.model().emit(
                    SIGNAL("dataChanged(QModelIndex,QModelIndex)"), finalIndex, self._childIndex)

        self.postExecute()
                        
            



            
        print "EXEC componentNewItem"

#    def unexecute(self):
#        ComponentItemCommand.unexecute(self)
#        if self._cp is not None:
#            if self._cp.instance is not None:
#                if self._index is not None:
#                     self._cp.instance.view.setCurrentIndex(self._childIndex)
#                     self._cp.instance.tagClicked(self._childIndex)
#                     
#        print "UNDO componentNewItem"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentNewItem(self.receiver, self.slot) 





## Command which loads a datasource from a file into the current component tree
class ComponentLoadDataSourceItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        self._cp = None
        ## name of the new datasource item
        self.itemName = ""
        

    ## executes the command
    # \brief It loads a datasource from a file into the current component tree
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is not None and self._cp.instance.view and  self._cp.instance.view.model():
                    if hasattr(self._cp.instance,"loadDataSourceItem"):
                        if not self._cp.instance.loadDataSourceItem(self.itemName):
                            QMessageBox.warning(self.receiver, "DataSource not loaded", 
                                                "Please ensure that you have selected the proper items")            
                else:
                    QMessageBox.warning(self.receiver, "Component item not selected", 
                                        "Please select one of the component items")            
                    
                        
        self.postExecute()
            
            
        print "EXEC componentMerge"

        
    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentLoadDataSourceItem(self.receiver, self.slot) 




## Command which adds the current datasource into the current component tree
class ComponentAddDataSourceItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It adds the current datasource into the current component tree
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is None or self._cp.instance.view is None or self._cp.instance.view.model() is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Component Item not created", 
                                        "Please edit one of the component Items")            
                    return

                ds = self.receiver.sourceList.currentListDataSource()
                if ds is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(self.receiver, "DataSource not selected", 
                                        "Please select one of the datasources")            
                    return

                if ds.instance is None:
                    dsEdit = DataSource()
                    dsEdit.ids = ds.id
                    dsEdit.directory = self.receiver.sourceList.directory
                    dsEdit.name = self.receiver.sourceList.datasources[ds.id].name
                    ds.instance = dsEdit 
                else:
                    dsEdit = ds.instance 


                if hasattr(dsEdit,"connectExternalActions"):     
                    dsEdit.connectExternalActions(**self.receiver.externalDSActions)
                
                if not hasattr(ds.instance,"createNodes"):
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Component Item not created", 
                                        "Please edit one of the component Items")            
                    return

                dsNode = ds.instance.createNodes()
                if dsNode is None:
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Datasource node cannot be created", 
                                        "Problem in importing the external node")            
                    return
        
                if not hasattr(self._cp.instance,"addDataSourceItem"):
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Component Item not created", 
                                        "Please edit one of the component Items")            
                    return
                if not self._cp.instance.addDataSourceItem(dsNode):
                    QMessageBox.warning(self.receiver, "Adding the datasource item not possible", 
                                        "Please ensure that you have selected the proper items")            



        self.postExecute()
            


            
        print "EXEC componentAddDataSourceItem"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentAddDataSourceItem(self.receiver, self.slot) 




## Command which links the current datasource into the current component tree
class ComponentLinkDataSourceItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        
        
    ## executes the command
    # \brief It links the current datasource into the current component tree
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if self._cp.instance is None or self._cp.instance.view is None or self._cp.instance.view.model() is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Component Item not created", 
                                        "Please edit one of the component Items")            
                    return

                ds = self.receiver.sourceList.currentListDataSource()
                if ds is None:
                    self._oldstate = None
                    self._index = None
                    self._cp = None
                    QMessageBox.warning(self.receiver, "DataSource not selected", 
                                        "Please select one of the datasources")            
                    return

                if ds.instance is None:
                    dsEdit = DataSource()
                    dsEdit.ids = ds.id
                    dsEdit.directory = self.receiver.sourceList.directory
                    dsEdit.name = self.receiver.sourceList.datasources[ds.id].name
                    ds.instance = dsEdit 
                else:
                    dsEdit = ds.instance 

                if not hasattr(ds.instance,"dataSourceName") or not ds.instance.dataSourceName:
                    self._cp = None
                    QMessageBox.warning(self.receiver, "DataSource wihtout name", 
                                        "Please define datasource name")            
                    return

                    

                if hasattr(dsEdit,"connectExternalActions"):     
                    dsEdit.connectExternalActions(**self.receiver.externalDSActions)
                
                if not hasattr(ds.instance,"createNodes"):
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Component Item not created", 
                                        "Please edit one of the component Items")            
                    return

        
                if not hasattr(self._cp.instance,"linkDataSourceItem"):
                    self._cp = None
                    QMessageBox.warning(self.receiver, "Component Item not created", 
                                        "Please edit one of the component Items")            
                    return
                if not self._cp.instance.linkDataSourceItem(dsEdit.dataSourceName):
                    QMessageBox.warning(self.receiver, "Linking the datasource item not possible", 
                                        "Please ensure that you have selected the proper items")            



        self.postExecute()
            


            
        print "EXEC componentLinkDataSourceItem"

    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentLinkDataSourceItem(self.receiver, self.slot) 


## Command which applies the changes from the form for the current component item
class ComponentApplyItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        self._index = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current component item
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if hasattr(self._cp, "instance") and hasattr(self._cp.instance,"applyItem"):

                    if not self._cp.instance.applyItem():
                        QMessageBox.warning(self.receiver, "Applying item not possible", 
                                            "Please select another tree item") 


        self.postExecute()

            
        print "EXEC componentApplyItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentApplyItem(self.receiver, self.slot) 







## Command which move the current component item up
class ComponentMoveUpItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        self._index = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current component item
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if hasattr(self._cp, "instance") and hasattr(self._cp.instance,"moveUpItem"):

                    if self._cp.instance.moveUpItem() is None:
                        QMessageBox.warning(self.receiver, "Moving item up not possible", 
                                            "Please select another tree item") 


        self.postExecute()

            
        print "EXEC componentMoveUpItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentMoveUpItem(self.receiver, self.slot) 






## Command which move the current component item down
class ComponentMoveDownItem(ComponentItemCommand):

    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot):
        ComponentItemCommand.__init__(self, receiver, slot)
        self._index = None
        
        
    ## executes the command
    # \brief It applies the changes from the form for the current component item
    def execute(self):
        if self._cp is None:
            self.preExecute()
            if self._cp is not None:
                if hasattr(self._cp, "instance") and hasattr(self._cp.instance,"moveDownItem"):

                    if self._cp.instance.moveDownItem() is None:
                        QMessageBox.warning(self.receiver, "Moving item down not possible", 
                                            "Please select another tree item") 


        self.postExecute()

            
        print "EXEC componentMoveDownItem"


    ## clones the command
    # \returns clone of the current instance
    def clone(self):
        return ComponentMoveDownItem(self.receiver, self.slot) 







        

if __name__ == "__main__":
    import sys

