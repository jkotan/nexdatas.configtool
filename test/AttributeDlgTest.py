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

from PyQt4.QtTest import QTest
from PyQt4.QtGui import QApplication
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from ndtsconfigtool.AttributeDlg import AttributeDlg



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class AttributeDlgTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        ##  Qt-application
        self.app = None

    ## test starter
    # \brief Common set up
    def setUp(self):
        self.app = QApplication(sys.argv)

        print "\nsetting up..."        

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
#        form.show()
#        self.app.exec_() 
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

    ## constructor test
    # \brief It tests default settings
    def test_constructor_reject(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = AttributeDlg()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
#        form.show()
#        self.app.exec_() 
        
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


#        if form.result():
#            if form.name:
#                print "Attribute: %s = \'%s\'" % ( form.name, form.value )
    



if __name__ == '__main__':
    unittest.main()
