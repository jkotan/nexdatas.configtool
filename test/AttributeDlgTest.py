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
## \file AttributeDlgTest.py
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

from ndtsconfigtool.AttributeDlg import AttributeDlg



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class AttributeDlgTest(unittest.TestCase):
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
        
        if not AttributeDlgTest.app:
            AttributeDlgTest.app = QApplication([])


    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = AttributeDlg()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
        self.assertTrue(form.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.valueLineEdit.text().isEmpty())
        self.assertTrue(not form.buttonBox.button(form.buttonBox.Ok).isEnabled())
        self.assertTrue(form.buttonBox.button(form.buttonBox.Cancel).isEnabled())

        name = "myname"
        value = "myentry"
        QTest.keyClicks(form.nameLineEdit, name)
        self.assertEqual(form.nameLineEdit.text(),name)
        QTest.keyClicks(form.valueLineEdit, value)
        self.assertEqual(form.valueLineEdit.text(),value)

        self.assertTrue(not form.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.valueLineEdit.text().isEmpty())
        self.assertTrue(form.buttonBox.button(form.buttonBox.Ok).isEnabled())
        self.assertTrue(form.buttonBox.button(form.buttonBox.Cancel).isEnabled())


        okWidget = form.buttonBox.button(form.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        self.assertEqual(form.name, name)
        self.assertEqual(form.value, value)

        self.assertEqual(form.result(),1)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_reject(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = AttributeDlg()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
        
        name = "myname"
        value = "myentry"
        QTest.keyClicks(form.nameLineEdit, name)
        self.assertEqual(form.nameLineEdit.text(),name)
        QTest.keyClicks(form.valueLineEdit, value)
        self.assertEqual(form.valueLineEdit.text(),value)
        clWidget = form.buttonBox.button(form.buttonBox.Cancel)
        QTest.mouseClick(clWidget, Qt.LeftButton)

        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')


        self.assertEqual(form.result(),0)
    
    def checkMessageBox(self):
        self.assertEqual(QApplication.activeWindow(),None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept_dash(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = AttributeDlg()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
        self.assertTrue(form.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.valueLineEdit.text().isEmpty())
        self.assertTrue(not form.buttonBox.button(form.buttonBox.Ok).isEnabled())
        self.assertTrue(form.buttonBox.button(form.buttonBox.Cancel).isEnabled())


        name = "-myname"
        value = "myentry"
        QTest.keyClicks(form.nameLineEdit, name)
        QTest.keyClicks(form.valueLineEdit, value)
        self.assertEqual(form.nameLineEdit.text(), name)
        self.assertEqual(form.valueLineEdit.text(), value)

        self.assertTrue(not form.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.valueLineEdit.text().isEmpty())
        self.assertTrue(form.buttonBox.button(form.buttonBox.Ok).isEnabled())
        self.assertTrue(form.buttonBox.button(form.buttonBox.Cancel).isEnabled())

        QTimer.singleShot(0, self.checkMessageBox)
        okWidget = form.buttonBox.button(form.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)


        self.assertEqual(self.title, 'Character Error') 
        self.assertEqual(self.text, "The first character of Name is '-'")

        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')


        self.assertEqual(form.result(),0)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept_chars(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        
        chars = '!"#$%&\'()*+,/;<=>?@[\\]^`{|}~'
        

        for ch in chars:
        
            form = AttributeDlg()
            self.assertEqual(form.name, '')
            self.assertEqual(form.value, '')
            self.assertTrue(form.nameLineEdit.text().isEmpty()) 
            self.assertTrue(form.valueLineEdit.text().isEmpty())
            self.assertTrue(not form.buttonBox.button(form.buttonBox.Ok).isEnabled())
            self.assertTrue(form.buttonBox.button(form.buttonBox.Cancel).isEnabled())
            
            name = "myname"
            value = "myentry"

            pos = self.__rnd.randint(0, len(name)-1) 
            name = name[:pos] + ch + name[pos:]
            
            QTest.keyClicks(form.nameLineEdit, name)
            QTest.keyClicks(form.valueLineEdit, value)
            self.assertEqual(form.nameLineEdit.text(), name)
            self.assertEqual(form.valueLineEdit.text(), value)
            
            self.assertTrue(not form.nameLineEdit.text().isEmpty()) 
            self.assertTrue(not form.valueLineEdit.text().isEmpty())
            self.assertTrue(form.buttonBox.button(form.buttonBox.Ok).isEnabled())
            self.assertTrue(form.buttonBox.button(form.buttonBox.Cancel).isEnabled())
            
            QTimer.singleShot(0, self.checkMessageBox)
            okWidget = form.buttonBox.button(form.buttonBox.Ok)
            QTest.mouseClick(okWidget, Qt.LeftButton)
            

            self.assertEqual(self.title, 'Character Error') 
            self.assertEqual(self.text, 'Name contains one of forbidden characters')
            
            self.assertEqual(form.name, '')
            self.assertEqual(form.value, '')
            
            self.assertEqual(form.result(),0)


if __name__ == '__main__':
    unittest.main()
