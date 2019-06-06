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
# \file ConfigurationServer.py
# Class for connecting to configuration server

""" Provides connects to configuration server"""

import logging
import time

from .ConnectDlg import ConnectDlg


try:
    import PyTango
    # if module PyTango avalable
    PYTANGO_AVAILABLE = True
    logger = logging.getLogger("nxsdesigner")
except ImportError as e:
    PYTANGO_AVAILABLE = False
    logger = logging.getLogger("nxsdesigner")
    logger.info("PyTango is not available: %s" % e)


# configuration server
class ConfigurationServer(object):

    # constructor
    def __init__(self):
        # name of tango device
        self.device = None

        # host name of tango device
        self.host = None

        # port of tango device
        self.port = None

        # connection status
        self.connected = False

        # device proxy
        self._proxy = None

    # sets server from string
    # \param device string
    def setServer(self, device):
        logger.debug(device)
        ahost = device.split(":")
        if len(ahost) > 1:
            self.host = ahost[0]
            adev = ahost[1].split("/")
            if len(adev) > 1:
                try:
                    self.port = int(adev[0])
                except Exception:
                    self.port = 10000
                self.device = "/".join(adev[1:])
            else:
                self.device = adev[0]
                self.port = 10000
        else:
            self.device = device
            self.host = 'localhost'
            self.port = 10000

    # allows to store the server state
    # \returns the state of the server
    def getState(self):
        return (self.device, self.host, self.port, self.connected)

    # allows to store the server state
    # \param state the state of the server
    def setState(self, state):
        (self.device, self.host, self.port, self.connected) = state

    def getDeviceName(self):
        if self.host and self.port:
            return "%s:%s/%s" % (str(self.host),
                                 str(self.port),
                                 str(self.device))
        else:
            return str(self.device)

    # connects to the configuration server
    # \brief It opens the configuration Tango device
    def connect(self):
        self._proxy = PyTango.DeviceProxy(self.getDeviceName())
        if self._proxy:
            found = False
            cnt = 0
            while not found and cnt < 1000:
                if cnt > 1:
                    time.sleep(0.01)
                try:
                    if self._proxy.state() != PyTango.DevState.RUNNING:
                        found = True
                except Exception:

                    time.sleep(0.01)
                    found = False
                cnt += 1

            if found:
                self._proxy.set_timeout_millis(25000)
                self._proxy.set_source(PyTango.DevSource.DEV)
                self._proxy.command_inout("Open")
                self.connected = True
            else:
                raise Exception("Cannot connect to: %s" % str(self.device))

    # opens connection to the configuration server
    # \brief It fetches parameters of tango device and calls connect() method
    def open(self):
        aform = ConnectDlg()
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

    # fetch all components
    # \returns dictionary with names : xml of components
    def fetchComponents(self):
        names = []
        comps = []
        if self._proxy and self.connected:
            names = self._proxy.command_inout("AvailableComponents")

            try:
                comps = self._proxy.command_inout("Components", names)
            except Exception:
                comps = []
                for n in names:
                    try:
                        xml = self._proxy.command_inout("Components", [n])
                        comps.append(xml[0])
                    except Exception:
                        comps.append("")
            return dict(zip(names, comps))

    # fetch all datasources
    # \returns dictionary with names : xml of datasources
    def fetchDataSources(self):
        names = []
        ds = []
        if self._proxy and self.connected:
            names = self._proxy.command_inout("AvailableDataSources")
            try:
                ds = self._proxy.command_inout("DataSources", names)
            except Exception:
                ds = []
                for n in names:
                    try:
                        xml = self._proxy.command_inout("DataSources", [n])
                        ds.extend(xml)
                    except Exception:
                        ds.append("")

            return dict(zip(names, ds))

    # stores the component
    # \param name component name
    # \param xml XML content of the component
    def storeComponent(self, name, xml):
        if self._proxy and self.connected:
            self._proxy.XMLString = str(xml)
            self._proxy.command_inout("StoreComponent", str(name))

    # stores the datasource
    # \param name datasource name
    # \param xml XML content of the datasource
    def storeDataSource(self, name, xml):
        if self._proxy and self.connected:
            self._proxy.XMLString = str(xml)
            self._proxy.command_inout("StoreDataSource", str(name))

    # stores the component
    # \param name component name
    def deleteComponent(self, name):
        if self._proxy and self.connected:
            self._proxy.command_inout("DeleteComponent", str(name))

    # stores the datasource
    # \param name datasource name
    def deleteDataSource(self, name):
        if self._proxy and self.connected:
            self._proxy.command_inout("DeleteDataSource", str(name))

    # set the given component mandatory
    # \param name component name
    def setMandatory(self, name):
        if self._proxy and self.connected:
            self._proxy.command_inout("SetMandatoryComponents",
                                      [str(name)])

    # get the mandatory components
    # returns list of the mandatory components
    def getMandatory(self):
        if self._proxy and self.connected:
            return self._proxy.command_inout("MandatoryComponents")

    # unset the given component mandatory
    # \param name component name
    def unsetMandatory(self, name):
        if self._proxy and self.connected:
            self._proxy.command_inout("UnsetMandatoryComponents", [str(name)])

    # closes connecion
    # \brief It closes connecion to configuration server
    def close(self):
        if self._proxy and self.connected:
            if self._proxy.state() == PyTango.DevState.OPEN:
                self._proxy.command_inout("Close")
                self.connected = False


# test function
def test():
    import sys
    from PyQt5.QtGui import QApplication

    app = QApplication(sys.argv)
    cs = ConfigurationServer()
    cs.device = "p09/mcs/r228"
    cs.host = "haso228k.desy.de"
    cs.port = 10000
    cs.open()
    cs.close()
    app.exit()


if __name__ == "__main__":
    test()
