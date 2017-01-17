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
## \package test nexdatas
## \file RichAttributeDlgTest.py
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
from PyQt4.QtGui import (QApplication, QMessageBox, QTableWidgetItem, QPushButton)
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject, QVariant, QString
from PyQt4.QtXml import QDomNode, QDomDocument, QDomElement


from nxsconfigtool.RichAttributeDlg import RichAttributeDlg
from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.AttributeDlg import AttributeDlg
from nxsconfigtool.NodeDlg import NodeDlg
from nxsconfigtool.DimensionsDlg import DimensionsDlg

from nxsconfigtool.ui.ui_richattributedlg import Ui_RichAttributeDlg
from nxsconfigtool.DomTools import DomTools


##  Qt-application
app = None


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

class TestView(object):
    def __init__(self, model):
        self.testIndex = None
        self.testModel = model
        self.stack = []

    def currentIndex(self):
        return self.testIndex 

    def model(self):
        return self.testModel

    def expand(self, index):
        self.stack.append("expand")
        self.stack.append(index)

## test fixture
class RichAttributeDlgTest(unittest.TestCase):

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

        self.dimensions = [1, 2, 3, 4]

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

    def checkMessageBox(self):
#        self.assertEqual(QApplication.activeWindow(),None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()


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


    def attributeWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

        mb.accept()



    def dimensionsWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, DimensionsDlg))
        self.assertTrue(hasattr(mb, "ui"))

        mb.ui.rankSpinBox.setValue(len(self.dimensions))
        
        for r in range(len(self.dimensions)):
            mb.ui.dimTableWidget.setCurrentCell(r,0)
            it = QTableWidgetItem(unicode(self.dimensions[r]))
            mb.ui.dimTableWidget.setItem(r,0,it)

#        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
#        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
#        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
#        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

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
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'] )
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        
        self.assertEqual(form.replaceText,super(RichAttributeDlg,form).replaceText )
        self.assertEqual(form.removeElement,super(RichAttributeDlg,form).removeElement )
        self.assertEqual(form.replaceElement,super(RichAttributeDlg,form).replaceElement )
        self.assertTrue(form.appendElement is not super(RichAttributeDlg,form).appendElement )
        self.assertEqual(form.reset,super(RichAttributeDlg,form).reset )


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
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
    def test_constructor_accept_long(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,  ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myfield"
        nType = "NX_DATE_TIME"
        value = "14:45"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.typeLineEdit, nType)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)

        QTest.keyClicks(form.ui.valueLineEdit, value)
        self.assertEqual(form.ui.valueLineEdit.text(), value)


        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

     
        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.valueLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        


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
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'] )
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        name = "myname"
        nType = "NXEntry"
        nType2 = "NX_INT64"
        value = "14:45"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        nn =  self.__rnd.randint(1, 9) 

        dimensions = [self.__rnd.randint(1, 40)  for n in range(nn)]
        
        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.name = name

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form.nexusType = nType

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""





        form.nexusType = nType2

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText(nType2))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""
        index2 = form.ui.typeComboBox.findText('other ...')
        form.ui.typeComboBox.setCurrentIndex(index2)




        form.dimensions = dimensions

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str(dimensions))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.dimLabel.setText("[]")
        form.dimensions = []

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str([0]*len(dimensions)).replace('0','*'))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.dimLabel.setText("[]")
        form.dimensions = []
        form.rank = 0

        form.value = value

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.valueLineEdit.setText("")
        form.value = ""


        form.doc = doc

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))



        form.ui.docTextEdit.setText("")






        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.value = value
        form.attributes = attributes

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_getState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ["enumeration", "doc", "datasource", "strategy","dimensions"])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()

        name = "myname"
        nType = "NXEntry"
        units = "Tmm"
        value = "asd1234"
        doc = "My documentation: \n ble ble ble "
        rank = 3
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        dimensions = [1, 2, 3, 4]

        
        self.assertEqual(form.getState(), (u'', u'', u'', u'', 0, []))
    

        form.name = name

        self.assertEqual(form.getState(),(name,u'',u'',u'',0,[]))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.name = ""

        form.nexusType = nType
        self.assertEqual(form.getState(),('', '',nType,'',0,[]))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.nexusType = ""



        form.value = value
        self.assertEqual(form.getState(),('',value,'','',0,[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.value = ""



        form.doc = doc
        self.assertEqual(form.getState(),('','','',doc,0,[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.doc = ""





        form.rank = rank
        self.assertEqual(form.getState(),('','','','',rank,[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.rank = 0


        
        form.attributes = attributes
        state = form.getState()

        self.assertEqual(state[0],'')
        self.assertEqual(state[1],'')
        self.assertEqual(state[2],'')
        self.assertEqual(state[3],'')
        self.assertEqual(state[4],0)
        self.assertEqual(state[5],[])
        self.assertEqual(len(state),6)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.attributes = {}


        form.dimensions = dimensions
        state = form.getState()

        self.assertEqual(state[0],'')
        self.assertEqual(state[1],'')
        self.assertEqual(state[2],'')
        self.assertEqual(state[3],'')
        self.assertEqual(state[4],0)
        self.assertEqual(len(state),6)
        self.assertEqual(len(state[5]),len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[5][i])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.dimensions = []


        form.name = name
        form.nexusType = nType
        form.value = value
        form.doc = doc
        form.rank = rank
        form.dimensions = dimensions

        state = form.getState()

        self.assertEqual(state[0],name)
        self.assertEqual(state[1],value)
        self.assertEqual(state[2],nType)
        self.assertEqual(state[3],doc)
        self.assertEqual(state[4],rank)
        self.assertEqual(len(state),6)
        self.assertEqual(len(state[5]),len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[5][i])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)







    ## constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()


        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()


        name = "myname"
        nType = "NXEntry"
        units = "Tmm"
        value = "asd1234"
        doc = "My documentation: \n ble ble ble "
        rank = 3
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        dimensions = [1, 2, 3, 4]

        
        self.assertEqual(form.setState(['','','','',0,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])


        self.assertEqual(form.setState([name,'','','',0,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, name)
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])

        form.name = ""



        self.assertEqual(form.setState(['','',nType,'',0,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, nType)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])

        form.nexusType = ''





        self.assertEqual(form.setState(['',value,'','',0,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, value)
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])

        form.value = ''





        self.assertEqual(form.setState(['','','',doc,0,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])

        form.doc = ''






        self.assertEqual(form.setState(['','','','',rank,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, rank) 
        self.assertEqual(form.dimensions, [])

        form.rank = 0




        self.assertEqual(form.setState(['','','','',0,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])

        form.attributes = {}



        self.assertEqual(form.setState(['','','','',0,dimensions]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, dimensions)

        form.dimensions = {}

        self.assertEqual(form.setState([name,value,nType,doc,rank,dimensions]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, name)
        self.assertEqual(form.nexusType, nType)
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.value, value)
        self.assertEqual(form.rank, rank) 
        self.assertEqual(form.dimensions, dimensions)



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def test_linkDataSource(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        name = "myname"
        nType = "NXEntry"
        units = "seconds"
        value = "14:45"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        rank =  self.__rnd.randint(1, 9) 

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rank)]
        
        form.name = name
        form.nexusType = nType
        form.value = value
        form.doc = doc
        form.dimensions = dimensions
        form.rank = rank
        form.dsLabel = 'Sdatasources'

        myds = "mydsName"
        self.assertEqual(form.linkDataSource(myds),None)
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertEqual(form.ui.valueLineEdit.text(), "$%s.%s" % (form.dsLabel, myds) )




        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.createGUI(),None)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        name = "myname"
        nType = "NXEntry"
        nType2 = "NX_INT64"
        units = "seconds"
        value = "14:45"
        doc = "My documentation: \n ble ble ble "
        nn =  self.__rnd.randint(1, 9) 

        dimensions = [self.__rnd.randint(1, 40)  for n in range(nn)]
        
        self.assertEqual(form.updateForm(),None)
    

        form = RichAttributeDlg()
        form.show()
        form.name = name


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form = RichAttributeDlg()
        form.show()
        form.nexusType = nType


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""




        form = RichAttributeDlg()
        form.show()

        form.nexusType = nType2

        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText(nType2))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""
        index2 = form.ui.typeComboBox.findText('other ...')
        form.ui.typeComboBox.setCurrentIndex(index2)



        form = RichAttributeDlg()
        form.show()
        form.dimensions = dimensions


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str(dimensions))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.ui.dimLabel.setText("[]")
        form.dimensions = []

        form = RichAttributeDlg()
        form.show()

        form.rank = nn
        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str([0]*len(dimensions)).replace('0','*'))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.dimLabel.setText("[]")
        form.dimensions = []
        form.rank = 0

        form = RichAttributeDlg()
        form.show()
        form.value = value


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.valueLineEdit.setText("")
        form.value = ""


        form = RichAttributeDlg()
        form.show()
        form.doc = doc


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))



        form.ui.docTextEdit.setText("")






        form = RichAttributeDlg()
        form.show()
        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.value = value


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "attribute"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 


        rn =  self.__rnd.randint(1, 9) 
        dimensions = [str(self.__rnd.randint(1, 40)) for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 



        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')





    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 


        rn =  self.__rnd.randint(1, 9) 
        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = RichAttributeDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode(qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')



    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter_nodim(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 


        rn =  self.__rnd.randint(1, 9) 
        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
                
        qdn.appendChild(mdim) 




        form = RichAttributeDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode(qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, [None]*len(dimensions))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')







    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_nonode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        rn =  self.__rnd.randint(1, 9) 
        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = RichAttributeDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')



    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn) 




        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])



        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')








    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        rn =  self.__rnd.randint(1, 9) 
        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')





        






    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_wrong(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')


    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"


        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')









    ## constructor test
    # \brief It tests default settings
    def test_updateNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        attrs = {"longname":"newlogname"}
        mdoc = "New text \nNew text"


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 


        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.value = "My new value ble ble"


        mrnk = self.__rnd.randint(0,5)     
        mdimensions = [str(self.__rnd.randint(1, 40))  for n in range(mrnk)]
        form.rank = mrnk
        form.dimensions = mdimensions
        form.doc = mdoc

        form.root = doc
        

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.updateNode()


        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
            
        trank = atdim.namedItem("rank").nodeValue()
        self.assertEqual(mrnk, int(trank) if trank else 0)
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= mrnk )
                self.assertEqual(mdimensions[ind-1], str(vl))
            child = child.nextSibling()    

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)






    ## constructor test
    # \brief It tests default settings
    def test_updateNode_withindex(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        mdoc = "New text \nNew text"

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.value = "My new value ble ble"

        mrnk = self.__rnd.randint(0,5)     
        mdimensions = [str(self.__rnd.randint(1, 40))  for n in range(mrnk)]
        form.rank = mrnk
        form.dimensions = mdimensions
        form.doc = mdoc

        form.root = doc
        

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.updateNode(di)

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 


        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
            
        trank = atdim.namedItem("rank").nodeValue()
        self.assertEqual(mrnk, int(trank) if trank else 0)
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= mrnk )
                self.assertEqual(mdimensions[ind-1], str(vl))
            child = child.nextSibling()    

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    ## constructor test
    # \brief It tests default settings
    def test_apply(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("units","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        units = "myunits"
        attrs = {"longname":"newlogname","unit":"myunits%s" %  nn}
        mdoc = "New text \nNew text"
        mvalue = "My new value ble ble"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.value = mvalue

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.typeLineEdit.setText(ntype)
        form.ui.valueLineEdit.setText(mvalue)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        mrnk = self.__rnd.randint(0,5)     
        self.dimensions = [str(self.__rnd.randint(1, 40))  for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        form.apply()


        self.assertEqual(form.name, nname)
        self.assertEqual(form.nexusType, ntype)
        self.assertEqual(form.value, mvalue)
        self.assertEqual(form.doc, mdoc)
        self.assertEqual(form.rank, len(self.dimensions))
        self.assertEqual(form.dimensions, self.dimensions)


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, ntype)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,mdoc)
        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,mvalue)

        mydm = form.node.firstChildElement(QString("dimensions"))           

        atdim = mydm.attributes()
        trank = atdim.namedItem("rank").nodeValue()
        self.assertEqual(mrnk, int(trank) if trank else 0)
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= mrnk )
                self.assertEqual(self.dimensions[ind-1], str(vl))
            child = child.nextSibling()    


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl, ntype)
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    ## constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        mdoc = "New text \nNew text"
        mvalue = "My new value ble ble"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.value = mvalue

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.typeLineEdit.setText(ntype)
        form.ui.valueLineEdit.setText(mvalue)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        

        mrnk = self.__rnd.randint(0,5)     
        self.dimensions = [str(self.__rnd.randint(1, 40))  for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        form.reset()
        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= rn )
                self.assertEqual(dimensions[ind-1], str(vl))
            child = child.nextSibling()    





    ## constructor test
    # \brief It tests default settings
    def test_reset_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        units = "myunits"
        attrs = {"longname":"newlogname","unit":"myunits%s" %  nn}
        mdoc = "New text \nNew text"
        mvalue = "My new value ble ble"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,form.nexusType)
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.value = mvalue

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.typeLineEdit.setText(ntype)
        form.ui.valueLineEdit.setText(mvalue)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        

        mrnk = self.__rnd.randint(0,5)     
        self.dimensions = [str(self.__rnd.randint(1, 40))  for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)
        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= rn )
                self.assertEqual(dimensions[ind-1], str(vl))
            child = child.nextSibling()    











    def myAction(self):
        self.performed = True


    ## constructor test


    ## constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(DomTools, DomTools))

        self.assertEqual(form.result(),0)

    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, None)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)






    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.createGUI()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(externalDSLink=self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False



        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_sapply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)


    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_slink_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(externalDSLink=self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply,None)
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.linkDSPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = RichAttributeDlg()
        form.ui = Ui_RichAttributeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_RichAttributeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)






    ## constructor test
    # \brief It tests default settings
    def test_appendElement(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("units","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()

        attributeMap = form.node.attributes()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di



        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= rn )
                self.assertEqual(dimensions[ind-1], str(vl))
            child = child.nextSibling()    





        doc2 = QDomDocument()
        nname2 = "datasource"
        qdn2 = doc2.createElement(nname2)
        qdn2.setAttribute("name","my2name%s" %  nn)
        qdn2.setAttribute("type","my2type%s" %  nn)
        doc2.appendChild(qdn2) 



        form.appendElement(qdn2,di)


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= rn )
                self.assertEqual(dimensions[ind-1], str(vl))
            child = child.nextSibling()    



        ds = form.node.firstChildElement(QString("datasource"))           
        attributeMap2 = ds.attributes()
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap2.item(i).nodeName()
            vl = attributeMap2.item(i).nodeValue()
            print "nv",nm,vl
            if nm == "name":
                self.assertEqual(vl,  "my2name%s" %  nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,  "my2type%s" %  nn)
                cnt += 1 







    ## constructor test
    # \brief It tests default settings
    def test_appendElement_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
        qdn.setAttribute("units","myunits%s" %  nn)
        qdn.setAttribute("shortname","mynshort%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        dval = []
        nval =  self.__rnd.randint(0, 10) 
        for n in range(nval):
            dval.append(doc.createTextNode("\nVAL\n %s\n" %  n))
            qdn.appendChild(dval[-1]) 

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        rn =  self.__rnd.randint(1, 9) 

        dimensions = [str(self.__rnd.randint(1, 40))  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = RichAttributeDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])
        self.assertTrue(isinstance(form.ui, Ui_RichAttributeDlg))

        form.setFromNode()
        form.createGUI()

        attributeMap = form.node.attributes()

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di



        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['enumeration', 'doc', 'datasource', 'strategy', 'dimensions'])

        self.assertEqual(form.dimensions, dimensions)



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "type":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(QString("dimensions"))           
         
        atdim = mydm.attributes()
        self.assertEqual(rn, int(atdim.namedItem("rank").nodeValue()))
        child = mydm.firstChild()           
        while not child.isNull():
            if child.nodeName() == unicode("dim"):
                at = child.attributes()
                ind = int(at.namedItem("index").nodeValue())
                vl = int(at.namedItem("value").nodeValue())
                self.assertTrue(ind >0 )
                self.assertTrue(ind <= rn )
                self.assertEqual(dimensions[ind-1], str(vl))
            child = child.nextSibling()    


        tags = ["datasource","strategy"]
        wtext = "To add a new %s please remove the old one"
        for tg in tags:



            doc2 = QDomDocument()
            nname2 = tg
            qdn2 = doc2.createElement(nname2)
            qdn2.setAttribute("name","my2name%s" %  nn)
            qdn2.setAttribute("type","my2type%s" %  nn)
            doc2.appendChild(qdn2) 

            form.appendElement(qdn2,di)

            QTimer.singleShot(10, self.checkMessageBox)
            form.appendElement(qdn2,di)
            self.assertEqual(self.text, wtext % nname2)



        tags = ["mydatasource","mystrategy","random"]
        wtext = "To add a new %s please remove the old one"
        for tg in tags:



            doc2 = QDomDocument()
            nname2 = tg
            qdn2 = doc2.createElement(nname2)
            qdn2.setAttribute("name","my2name%s" %  nn)
            qdn2.setAttribute("type","my2type%s" %  nn)
            doc2.appendChild(qdn2) 

            form.appendElement(qdn2,di)

            form.appendElement(qdn2,di)
        

if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
