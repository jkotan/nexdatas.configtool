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
from PyQt4.QtGui import (QApplication, QMessageBox, QTableWidgetItem)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject, QVariant
from PyQt4.QtXml import QDomNode, QDomDocument, QDomElement


from ndtsconfigtool.DefinitionDlg import DefinitionDlg
from ndtsconfigtool.AttributeDlg import AttributeDlg
from ndtsconfigtool.NodeDlg import NodeDlg

from ndtsconfigtool.ui.ui_definitiondlg import Ui_DefinitionDlg


##  Qt-application
app = None


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class DefinitionDlgTest(unittest.TestCase):

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

        ## attribute name
        self.aname = "myname"
        ## attribute value
        self.avalue = "myentry"

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
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        
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
        form.attributes = attributes

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


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
        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

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



    ## constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DefinitionDlg()
        form.show()
        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        name = "myname"
        nType = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        
        form = DefinitionDlg()
        form.show()
        form.createGUI()
 
        self.assertEqual(form.ui.nameLineEdit.text(), '') 
        self.assertEqual(form.ui.typeLineEdit.text(), '')
        self.assertEqual(form.ui.docTextEdit.toPlainText(), '')

        form = DefinitionDlg()
        form.show()
        form.name = name


        form.createGUI()
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.typeLineEdit.text(), '')
        self.assertEqual(form.ui.docTextEdit.toPlainText(), '')
        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)


        form = DefinitionDlg()
        form.show()
        form.nexusType = nType


        form.createGUI()
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())





        form = DefinitionDlg()
        form.show()
        form.doc = doc

        form.createGUI()
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)




        form = DefinitionDlg()
        form.show()
        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.attributes = attributes

        form.createGUI()
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)






    ## constructor test
    # \brief It tests default settings
    def test_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)





    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
#        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode(qdn)
        self.assertEqual(form.node, qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)


    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_noNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
#        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)



    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn) 


        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])



        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)



    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        form.populateAttributes()




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item,None)
        



    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_wrong(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        form.populateAttributes("ble")




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item,None)
        





    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)



    def attributeWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

        mb.accept()

    def attributeWidgetClose(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

#        mb.close()
        mb.reject()

#        mb.accept()



    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_addAttribute(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        self.aname = "addedAttribute"
        self.avalue = "addedAttributeValue"


        QTimer.singleShot(10, self.attributeWidgetClose)
        QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
        



        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        self.aname = "addedAttribute"
        self.avalue = "addedAttributeValue"

        QTimer.singleShot(10, self.attributeWidget)
        QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
        



        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes)+1)
        for i in range(len(attributes)+1):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            if k in attributes.keys():
                self.assertEqual(it2.text(), attributes[k])
            else:
                self.assertEqual(it2.text(), self.avalue)
                
        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)        
        self.assertEqual(item.data(Qt.UserRole).toString(),self.aname)




    def rmAttributeWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.Yes), Qt.LeftButton)

    def rmAttributeWidgetClose(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.No), Qt.LeftButton)



    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_removeAttribute(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        qdn.setAttribute("logname","mynlong%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'logname': u'mynlong%s' %nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)




        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        aname = self.__rnd.choice(attributes.keys())
        avalue = attributes[aname]
        
        
        form.populateAttributes(aname)


        QTimer.singleShot(10, self.rmAttributeWidgetClose)
        QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)
        
        self.assertEqual(self.text,"Remove attribute: %s = '%s'" % (aname,avalue))


        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)




        aname = self.__rnd.choice(attributes.keys())
        avalue = attributes[aname]
        
        
        form.populateAttributes(aname)


        QTimer.singleShot(10, self.rmAttributeWidget)
        QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)
        
        self.assertEqual(self.text,"Remove attribute: %s = '%s'" % (aname,avalue))


        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), len(attributes)-1)
        for i in range(len(attributes)-1):
            it = form.ui.attributeTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item, None)





    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_tableItemChanged(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        qdn.setAttribute("logname","mynlong%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 



        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        self.assertTrue(isinstance(form.ui, Ui_DefinitionDlg))

        form.createGUI()

        atw = form.ui.attributeTableWidget        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])
        
        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn, u'logname': u'mynlong%s' %nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems, 
                         ["group", "field", "attribute", "link", "component", "doc", "symbols"])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),0)

        
        na =  self.__rnd.randint(0, len(attributes)-1) 
        sel = attributes.keys()[na]
        form.populateAttributes(sel)


        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = atw.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])


        item = atw.item(atw.currentRow(), 0)
        self.assertEqual(item.data(Qt.UserRole).toString(), sel)

        ch = self.__rnd.randint(0, len(attributes)-1)
        atw.setCurrentCell(ch,0)
        item = atw.item(atw.currentRow(), 0)
        aname = str(item.data(Qt.UserRole).toString())

        it = QTableWidgetItem(unicode(aname))
        it.setData(Qt.DisplayRole, QVariant(aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, QVariant(aname))

        atw.setCurrentCell(ch,0)

        QTimer.singleShot(10, self.checkMessageBox)
        atw.setItem(ch,0,it)
        self.assertEqual(self.text, 
                         "To change the attribute name, please remove the attribute and add the new one")
        

        avalue = attributes[str(aname)]
                

        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = atw.item(i, 1) 
            self.assertEqual(it2.text(), attributes[k])




        it = QTableWidgetItem(unicode(aname))
        it.setData(Qt.DisplayRole, QVariant(aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, QVariant(aname))

        atw.setCurrentCell(ch,1)

        QTimer.singleShot(10, self.checkMessageBox)
        atw.setItem(ch,1,it)
        

        avalue = attributes[str(aname)]
                

        self.assertEqual(atw.columnCount(),2)
        self.assertEqual(atw.rowCount(),len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0)
            k = str(it.text())
            if k != aname:
                self.assertTrue(k in attributes.keys())
                it2 = atw.item(i, 1) 
                self.assertEqual(it2.text(), attributes[k])
            else:
                it2 = atw.item(i, 1) 
                self.assertEqual(it2.text(), QVariant(aname+"_"+attributes[aname]))


    ## constructor test
    # \brief It tests default settings
    def test_createGUI_connect(self):
        pass

if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
