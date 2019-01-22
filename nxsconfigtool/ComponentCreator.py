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
# \file ComponentCreator.py
# Class for connecting to configuration server

""" Provides connects to configuration server"""

from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
from .CreatorDlg import CreatorDlg, StdCreatorDlg

import logging
import sys
# message logger
logger = logging.getLogger("nxsdesigner")

if sys.version_info > (3,):
    unicode = str

try:
    import nxstools
    from nxstools.nxscreator import (
        OnlineCPCreator, OnlineDSCreator, StandardCPCreator)
    NXSTOOLS_AVAILABLE = True
    NXSTOOLS_MASTERVER, NXSTOOLS_MINORVER, NXSTOOLS_PATCHVER = \
        nxstools.__version__.split(".")
    if int(NXSTOOLS_MASTERVER) <= 2:
        if int(NXSTOOLS_MINORVER) <= 2:
            raise ImportError("nxstools is below 2.3.0")
except ImportError as e:
    NXSTOOLS_AVAILABLE = False
    logger.info("nxstools is not available: %s" % e)


# option class
class Options(object):
    def __init__(self, server=None):
        self.server = server
        self.overwrite = True
        self.lower = True
        self.component = None
        self.cptype = None
        self.directory = None
        self.xmlpackage = None
        self.external = ""
        self.entryname = "scan"
        self.insname = "instrument"
        self.oldclientlike = False
        self.clientlike = True


# configuration server
class ComponentCreator(object):

    # constructor
    def __init__(self, configServer, parent):
        # configuration server
        self.configServer = configServer

        # online file name
        self.onlineFile = None

        # componentName
        self.componentName = None

        # created components
        self.components = {}
        # created components
        self.datasources = {}
        # available components
        self.avcomponents = []
        # parent
        self.parent = parent

    # sets onlineFile name and check if online file exists
    def checkOnlineFile(self, onlineFile):
        onlineFile = onlineFile or '/online_dir/online.xml'
        onlineFile = unicode(QFileDialog.getOpenFileName(
            self.parent, "Open Online File", onlineFile,
            "XML files (*.xml)")[0])
        if onlineFile:
            self.onlineFile = onlineFile
            return True
        else:
            self.onlineFile = None

    # creates component and datasources from online xml
    def create(self):
        self.action = None
        self.componentName = None
        self.components = {}
        self.datasources = {}
        if NXSTOOLS_AVAILABLE and self.onlineFile:
            options = Options(self.configServer.getDeviceName())

            occ = OnlineCPCreator(options, [self.onlineFile], False)
            self.avcomponents = occ.listcomponents() or []
            if self.avcomponents:
                self.action = self.selectComponent()
                options.component = self.componentName
                if self.action:
                    occ.createXMLs()
                    self.components = dict(occ.components)
                    self.datasources = dict(occ.datasources)
            else:
                QMessageBox.warning(
                    self.parent,
                    "Error in creating Component",
                    "Cannot find any known components in '%s'" %
                    self.onlineFile)

    # runs Creator widget to select the required component
    # \returns action to be performed with the components and datasources
    def selectComponent(self):
        aform = CreatorDlg(self.parent)
        if self.avcomponents:
            aform.components = list(self.avcomponents)

        action = None
        self.componentName = None
        aform.createGUI()
        aform.show()
        if aform.exec_():
            action = aform.action
            self.componentName = aform.componentName
        return action


# configuration server
class StdComponentCreator(object):

    # constructor
    def __init__(self, configServer, parent):
        # configuration server
        self.configServer = configServer

        # created components
        self.components = {}
        # created components
        self.datasources = {}
        # parent
        self.parent = parent

    # creates component and datasources from online xml
    def create(self):
        self.action = None
        self.componentName = None
        self.components = {}
        self.datasources = {}
        if NXSTOOLS_AVAILABLE:
            options = Options(self.configServer.getDeviceName())

            scpc = StandardCPCreator(options, [], False)
            self.action = self.selectComponent(scpc)
            if self.action:
                scpc.createXMLs()
                self.components = dict(scpc.components)
                self.datasources = dict(scpc.datasources)

    # runs Creator widget to select the required component
    # \returns action to be performed with the components and datasources
    def selectComponent(self, scpc):
        aform = StdCreatorDlg(scpc, self.parent)
        action = None
        aform.createGUI()
        aform.show()
        if aform.exec_():
            action = aform.action
        return action


# configuration server
class DataSourceCreator(object):

    # constructor
    def __init__(self, configServer, parent):
        # configuration server
        self.configServer = configServer

        # online file name
        self.onlineFile = None

        # componentName
        self.componentName = None

        # created components
        self.datasources = {}
        # available components
        self.avcomponents = []
        # parent
        self.parent = parent

    # sets onlineFile name and check if online file exists
    def checkOnlineFile(self, onlineFile):
        onlineFile = onlineFile or '/online_dir/online.xml'
        onlineFile = unicode(QFileDialog.getOpenFileName(
            self.parent, "Open Online File", onlineFile,
            "XML files (*.xml)")[0])
        if onlineFile:
            self.onlineFile = onlineFile
            return True
        else:
            self.onlineFile = None

    # creates component and datasources from online xml
    def create(self):
        self.action = None
        self.datasources = {}
        if NXSTOOLS_AVAILABLE and self.onlineFile:
            options = Options(self.configServer.getDeviceName())

            occ = OnlineDSCreator(options, [self.onlineFile], False)
            self.action = self.selectAction()
            if self.action:
                occ.createXMLs()
                self.datasources = dict(occ.datasources)

    # runs Creator widget to select the required component
    # \returns action to be performed with the components and datasources
    def selectAction(self):
        aform = CreatorDlg(self.parent)
        action = None
        aform.createGUI()
        aform.setWindowTitle("DataSource Creator")
        aform.ui.compFrame.hide()
        aform.resize(600, 0)
        aform.show()
        if aform.exec_():
            action = aform.action
        return action


# test function
def test():
    import sys
    from PyQt5.QtGui import QApplication

    app = QApplication(sys.argv)
    app.exit()


if __name__ == "__main__":
    test()
