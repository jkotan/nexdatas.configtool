#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \file ConfigurationServer.py
# Class for merging DOM component trees

try:
    import PyTango
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print "PyTango is not available: %s" % e

import PyTango

from ConnectDlg import  ConnectDlg

## merges the components
class ConfigurationServer(object):
    
    ## constructor
    def __init__(self):
        ## name of tango device
        self.device = None

        ## host name of tango device
        self.host= None

        ## port of tango device
        self.port = None
        
        ## connection status
        self.connected = False 
        
        ## device proxy
        self._proxy = None


    ## allows to store the server state    
    # \returns the state of the server
    def getState(self):
        return (self.device, self.host, self.port, self.connected)


    ## allows to store the server state    
    # \param state the state of the server
    def setState(self, state):
        (self.device, self.host, self.port, self.connected) = state

    ## connects to the configuration server
    # \brief It opens the configuration Tango device
    def connect(self):
        if self.host and self.port:
            self._proxy = PyTango.DeviceProxy("%s:%s/%s"
                                              % (self.host.encode(),
                                                 str(self.port),
                                                 self.device.encode()))
        else:
            self._proxy = PyTango.DeviceProxy(self.device.encode())
        if self._proxy:
            self._proxy.set_timeout_millis(25000)
            self._proxy.Open()
            self.connected = True


    ## opens connection to the configuration server
    # \brief It fetches parameters of tango device and calls connect() method
    def open(self):
        aform  = ConnectDlg()
        if self.device:
            aform.device = self.device
        if self.host:
            aform.host = self.host
        if self.port is not None:
            aform.port = self.port
            
        aform.createGUI()
        aform.show()
        if aform.exec_():
            self.device = aform.device
            self.host = aform.host
            self.port = aform.port
            self.connect()

            
    ## fetch all components
    # \returns dictionary with names : xml of components
    def fetchComponents(self):
        names = [] 
        comps = []
        if self._proxy and self.connected:
            names = self._proxy.AvailableComponents()
            comps = self._proxy.Components(names)
            return dict(zip(names, comps))
            


    ## fetch all datasources
    # \returns dictionary with names : xml of datasources
    def fetchDataSources(self):
        names = [] 
        ds = []
        if self._proxy and self.connected:
            names = self._proxy.AvailableDataSources()
            ds= self._proxy.DataSources(names)
            return dict(zip(names, ds))


    ## stores the component
    # \param name component name
    # \param xml XML content of the component    
    def storeComponent(self, name, xml):
        names = [] 
        ds = []
        if self._proxy and self.connected:
            self._proxy.XMLString = str(xml)
            self._proxy.StoreComponent(name)


    ## stores the datasource
    # \param name datasource name
    # \param xml XML content of the datasource
    def storeDataSource(self, name, xml):
        names = [] 
        ds = []
        if self._proxy and self.connected:
            self._proxy.XMLString = str(xml)
            self._proxy.StoreDataSource(name)
            


    ## closes connecion 
    # \brief It closes connecion to configuration server
    def close(self):
        if self._proxy and self.connected:
            self._proxy.Close()
            self.connected = False
            

if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    app = QApplication(sys.argv)
    cs = ConfigurationServer()
    cs.device = "p09/mcs/r228"
    cs.host = "haso228k.desy.de"
    cs.port = 10000
    cs.open() 
    cs.close()
    
