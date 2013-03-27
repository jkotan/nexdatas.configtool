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
## \package test nexdatas
## \file ConnectDlgTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import binascii
import time

from PyQt4.QtTest import QTest
from PyQt4.QtGui import (QApplication, QMessageBox)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject

from ndtsconfigtool.ConnectDlg import ConnectDlg



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class ConnectDlgTest(unittest.TestCase):
    ##  Qt-application
    app = None

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        ## MessageBox text
        self.text = None
        ## MessageBox title
        self.title = None

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 
         
        self.__rnd = random.Random(self.__seed)


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        
        print "SEED =", self.__seed 
        
        if not ConnectDlgTest.app:
            ConnectDlgTest.app = QApplication([])

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        self.assertEqual(form.result(),0)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI_withhost(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        form.show()
        form.createGUI()
        self.assertTrue(form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        device = "my/device/1"
        host = "myhost.de"
        port = "10005"
        QTest.keyClicks(form.ui.deviceLineEdit, device)
        self.assertEqual(form.ui.deviceLineEdit.text(),device)

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTest.keyClicks(form.ui.hostLineEdit, host)
        self.assertEqual(form.ui.hostLineEdit.text(), host)
        QTest.keyClicks(form.ui.portLineEdit, port)
        self.assertEqual(form.ui.portLineEdit.text(), port)

        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())


        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)

        self.assertEqual(form.device, device)
        self.assertEqual(form.host, host)
        self.assertEqual(form.port, int(port))

        self.assertEqual(form.result(),1)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        form.show()
        form.createGUI()
        self.assertTrue(form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        device = "my/device/1"
        host = ""
        port = ""
        QTest.keyClicks(form.ui.deviceLineEdit, device)
        self.assertEqual(form.ui.deviceLineEdit.text(),device)

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTest.keyClicks(form.ui.hostLineEdit, host)
        self.assertEqual(form.ui.hostLineEdit.text(), host)
        QTest.keyClicks(form.ui.portLineEdit, port)
        self.assertEqual(form.ui.portLineEdit.text(), port)

        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())


        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)

        self.assertEqual(form.device, device)
        self.assertEqual(form.host, host)
        self.assertEqual(form.port, None)

        self.assertEqual(form.result(),1)


    
    def checkMessageBox(self):
        self.assertEqual(QApplication.activeWindow(), None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()



    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        form.show()
        form.createGUI()
        self.assertTrue(form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        device = " "
        host = "myhost.de"
        port = "10005"
        QTest.keyClicks(form.ui.deviceLineEdit, device)
        self.assertEqual(form.ui.deviceLineEdit.text(),device)

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTest.keyClicks(form.ui.hostLineEdit, host)
        self.assertEqual(form.ui.hostLineEdit.text(), host)
        QTest.keyClicks(form.ui.portLineEdit, port)
        self.assertEqual(form.ui.portLineEdit.text(), port)

        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTimer.singleShot(0, self.checkMessageBox)
        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)
        self.assertEqual(self.text, 'Please define the device name')
        self.assertEqual(self.title, 'Empty device name')
        

        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI_port(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        form.show()
        form.createGUI()
        self.assertTrue(form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())



        device = "my device"
        host = "myhost.de"
        port = "1d0005"
        QTest.keyClicks(form.ui.deviceLineEdit, device)
        self.assertEqual(form.ui.deviceLineEdit.text(),device)

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTest.keyClicks(form.ui.hostLineEdit, host)
        self.assertEqual(form.ui.hostLineEdit.text(), host)
        QTest.keyClicks(form.ui.portLineEdit, port)
        self.assertEqual(form.ui.portLineEdit.text(), port)

        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTimer.singleShot(0, self.checkMessageBox)
        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)
        self.assertEqual(self.text, 'Please define the port number')
        self.assertEqual(self.title, 'Wrong port number')
        

        self.assertEqual(form.device, device.strip())
        self.assertEqual(form.host, host.strip())
        self.assertEqual(form.port, None)


        self.assertEqual(form.result(),0)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI_nohost(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        form.show()
        form.createGUI()
        self.assertTrue(form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        device = "my device"
        host = ""
        port = "10005"
        QTest.keyClicks(form.ui.deviceLineEdit, device)
        self.assertEqual(form.ui.deviceLineEdit.text(),device)

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTest.keyClicks(form.ui.hostLineEdit, host)
        self.assertEqual(form.ui.hostLineEdit.text(), host)
        QTest.keyClicks(form.ui.portLineEdit, port)
        self.assertEqual(form.ui.portLineEdit.text(), port)

        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTimer.singleShot(0, self.checkMessageBox)
        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)
        self.assertEqual(self.text, 'Please define the host name')
        self.assertEqual(self.title, 'Empty host name')
        

        self.assertEqual(form.device, device.strip())
        self.assertEqual(form.host, "")
        self.assertEqual(form.port, int(port))

        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI_noport(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()
        self.assertEqual(form.device, '')
        self.assertEqual(form.host, '')
        self.assertEqual(form.port, None)

        form.show()
        form.createGUI()
        self.assertTrue(form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        device = "my device"
        host = "hasso.de"
        port = ""
        QTest.keyClicks(form.ui.deviceLineEdit, device)
        self.assertEqual(form.ui.deviceLineEdit.text(),device)

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTest.keyClicks(form.ui.hostLineEdit, host)
        self.assertEqual(form.ui.hostLineEdit.text(), host)
        QTest.keyClicks(form.ui.portLineEdit, port)
        self.assertEqual(form.ui.portLineEdit.text(), port)

        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())

        QTimer.singleShot(0, self.checkMessageBox)
        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)
        self.assertEqual(self.text, 'Please define the port')
        self.assertEqual(self.title, 'Empty port')                

#        print form.portLineEdit.hasFocus()
#        self.assertTrue(form.portLineEdit.hasFocus())

        self.assertEqual(form.device, device.strip())
        self.assertEqual(form.host, host.strip())
        self.assertEqual(form.port, None)


        self.assertEqual(form.result(),0)
        


    ## constructor test
    # \brief It tests default settings
    def test_constructor_createGUI_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = ConnectDlg()

        device = "my/device/1"
        host = "myhost.de"
        port = "10005"


        form.device = device
        form.host = host
        form.port = port

        self.assertEqual(form.device, device)
        self.assertEqual(form.host, host)
        self.assertEqual(form.port, port)

        form.show()
        form.createGUI()
        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.portLineEdit.text().isEmpty())

        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())


        self.assertEqual(form.device, device)
        self.assertEqual(form.host, host)
        self.assertEqual(form.port, port)


        self.assertTrue(not form.ui.deviceLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.hostLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.portLineEdit.text().isEmpty())
        self.assertTrue(form.ui.connectPushButton.isEnabled())
        self.assertTrue(form.ui.cancelPushButton.isEnabled())


        QTest.mouseClick(form.ui.connectPushButton, Qt.LeftButton)

        self.assertEqual(form.device, device)
        self.assertEqual(form.host, host)
        self.assertEqual(form.port, int(port))

        
        self.assertEqual(form.result(),1)

if __name__ == '__main__':
    unittest.main()
