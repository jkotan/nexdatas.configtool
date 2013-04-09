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
## \file DefinitionDlgTest.py
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

from ndtsconfigtool.DefinitionDlg import DefinitionDlg
from ndtsconfigtool.NodeDlg import NodeDlg

from ndtsconfigtool.ui.ui_definitiondlg import Ui_DefinitionDlg


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class DefinitionDlgTest(unittest.TestCase):
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
        
        if not DefinitionDlgTest.app:
            DefinitionDlgTest.app = QApplication([])


    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."


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
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))
        self.assertTrue(isinstance(form, NodeDlg))


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        
        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myname"
        nType = "NXEntry"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.typeLineEdit, nType)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)

        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.typeLineEdit.text().isEmpty())


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        name = "myname"
        nType = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        
        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.name = name

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.nameLineEdit.setText("")

        form.name = ""
        form.nexusType = nType

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())




        form.ui.typeLineEdit.setText("")

        form.doc = doc
        form.nexusType = ""

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        form.ui.docTextEdit.setText("")

        form.name = name
        form.doc = doc
        form.nexusType = nType

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)




        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_getState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()



        name = "myname"
        nType = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }

        
        self.assertEqual(form.getState(),('','','',{}))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.name = name

        self.assertEqual(form.getState(),(name,'','',{}))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        form.name = ""
        form.nexusType = nType

        self.assertEqual(form.getState(),('',nType,'',{}))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())





        form.doc = doc
        form.nexusType = ""

        self.assertEqual(form.getState(),('', '', doc, {}))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



        form.doc = ""
        form.nexusType = ""
        
        form.attributes = attributes
        state = form.getState()

        self.assertEqual(state[0],'')
        self.assertEqual(state[1],'')
        self.assertEqual(state[2],'')
        self.assertEqual(len(state),4)
        self.assertEqual(len(state[3]),len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[3][at])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.attributes = attributes

        state = form.getState()

        self.assertEqual(state[0],name)
        self.assertEqual(state[1],nType)
        self.assertEqual(state[2],doc)
        self.assertEqual(len(state),4)
        self.assertTrue(state[3] is not attributes)
        self.assertEqual(len(state[3]),len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[3][at])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)







    ## constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()



        name = "myname"
        nType = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }

        
        self.assertEqual(form.setState(['','','',{}]), None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        self.assertEqual(form.setState([name,'','',{}]), None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.name,name) 
        self.assertEqual(form.nexusType,'') 
        self.assertEqual(form.doc,'') 
        self.assertEqual(form.attributes,{}) 

        form.name = ""

        self.assertEqual(form.setState(['',nType,'',{}]), None)
 
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name,'') 
        self.assertEqual(form.nexusType, nType) 
        self.assertEqual(form.doc,'') 
        self.assertEqual(form.attributes,{}) 

        form.nexusType = ""

        self.assertEqual(form.setState(['','',doc,{}]), None)
 
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name,'') 
        self.assertEqual(form.nexusType, '') 
        self.assertEqual(form.doc,doc) 
        self.assertEqual(form.attributes,{}) 

        form.doc = ""
        
#        form.attributes = attributes
        self.assertEqual(form.setState(['','','',attributes]), None)
 
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name,'') 
        self.assertEqual(form.nexusType, '') 
        self.assertEqual(form.doc,'') 
        self.assertEqual(form.attributes,attributes) 
        self.assertTrue(form.attributes is not attributes)



        self.assertEqual(form.setState([name,nType,doc,attributes]), None)
 
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name,name) 
        self.assertEqual(form.nexusType, nType) 
        self.assertEqual(form.doc,doc) 
        self.assertEqual(form.attributes,attributes) 
        self.assertTrue(form.attributes is not attributes)


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)





if __name__ == '__main__':
    unittest.main()
