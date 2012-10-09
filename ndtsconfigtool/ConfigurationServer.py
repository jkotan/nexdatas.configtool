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


    ## open connection to the configuration server
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
    
