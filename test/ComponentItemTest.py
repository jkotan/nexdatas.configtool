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
## \file ComponentItemTest.py
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
from PyQt4.QtGui import (QApplication, QMessageBox, QPushButton)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject
from PyQt4.QtXml import QDomNode, QDomDocument

from ndtsconfigtool.ComponentItem import ComponentItem



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class ComponentItemTest(unittest.TestCase):

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
        ## action status
        self.performed = False


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
        


    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."



    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        qdn = QDomNode()
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        ci = ComponentItem(qdn)

        self.assertEqual(ci.node,qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.child(0),None)
        self.assertEqual(ci.child(1),None)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_with_dom(self):
        fun = sys._getframe().f_code.co_name
        doc = QDomDocument()
        qdn = doc.createElement("definition")
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])


        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
        self.assertEqual(ci.node,qdn)
        self.assertEqual(ci.childNumber(),0)
        for k in range(nkids):
            self.assertEqual(ci.child(k).node, kds[k])
            self.assertEqual(ci.child(k).parent.node, qdn)



if __name__ == '__main__':
    unittest.main()
