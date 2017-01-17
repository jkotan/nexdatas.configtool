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
## \file LinkDlgTest.py
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


from nxsconfigtool.LinkDlg import LinkDlg
from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.AttributeDlg import AttributeDlg
from nxsconfigtool.NodeDlg import NodeDlg
from nxsconfigtool.DimensionsDlg import DimensionsDlg

from nxsconfigtool.ui.ui_linkdlg import Ui_LinkDlg
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
class LinkDlgTest(unittest.TestCase):

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

        self.dimensions = [1,2,3,4]

        ## action status
        self.performed = False

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 

        self.__seed= 309284324384944322060160783760382990541

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
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc', 'datasource', 'strategy'] )
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        
        self.assertEqual(form.replaceText,super(LinkDlg,form).replaceText )
        self.assertEqual(form.removeElement,super(LinkDlg,form).removeElement )
        self.assertEqual(form.replaceElement,super(LinkDlg,form).replaceElement )
        self.assertTrue(form.appendElement is not super(LinkDlg,form).appendElement )
        self.assertEqual(form.reset,super(LinkDlg,form).reset )


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myname"
        target = "NXEntry/NXinstrument"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.targetLineEdit, target)
        self.assertEqual(form.ui.targetLineEdit.text(),target)

        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.targetLineEdit.text().isEmpty())


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.target, target)

        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept_long(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,  ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myfield"
        target = "/entry/instrument/"
        value = "14:45"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.targetLineEdit, target)
        self.assertEqual(form.ui.targetLineEdit.text(), target)



     
        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.target, target)

        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,['doc', 'datasource', 'strategy'] )
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        name = "myname"
        target = "NXEntry"
        target2 = "entry/instrument"
        doc = "My documentation: \n ble ble ble "

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        form.name = name

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form.target = target

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.targetLineEdit.text(), target)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.targetLineEdit.setText("")
        form.target = ""




        form.doc = doc

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        form.ui.docTextEdit.setText("")






        form.name = name
        form.doc = doc
        form.target = target

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.targetLineEdit.text(), target)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_updateForm_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,['doc', 'datasource', 'strategy'] )
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        name = "myname"
        target = "$datasources.NXEntry"
        target2 = "$datasources.instrument"
        doc = "My documentation: \n ble ble ble "

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        form.name = name

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form.target = target

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.targetLineEdit.text(), target)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.targetLineEdit.setText("")
        form.target = ""




        form.doc = doc

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)



        form.ui.docTextEdit.setText("")






        form.name = name
        form.doc = doc
        form.target = target

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.targetLineEdit.text(), target)
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
        form = LinkDlg()
        form.show()

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ["doc", 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()

        name = "myname"
        target = "NXEntry"
        doc = "My documentation: \n ble ble ble "

        
        self.assertEqual(form.getState(), (u'', u'', u''))
    

        form.name = name

        self.assertEqual(form.getState(),(name,u'',u''))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        form.name = ""

        form.target = target
        self.assertEqual(form.getState(),('', target,''))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        form.target = ""




        form.doc = doc
        self.assertEqual(form.getState(),('','',doc))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.doc = ""




        form.name = name
        form.target = target
        form.doc = doc

        state = form.getState()

        self.assertEqual(state[0],name)
        self.assertEqual(state[1],target)
        self.assertEqual(state[2],doc)

        self.assertEqual(len(state),3)
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)



     ## constructor test
    # \brief It tests default settings
    def test_getState_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ["doc", 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()

        name = "myname"
        target = "$datasources.entry"
        doc = "My documentation: \n ble ble ble "

        
        self.assertEqual(form.getState(), (u'', u'', u''))
    

        form.name = name

        self.assertEqual(form.getState(),(name,u'',u''))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        form.name = ""

        form.target = target
        self.assertEqual(form.getState(),('', target,''))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        form.target = ""




        form.doc = doc
        self.assertEqual(form.getState(),('','',doc))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.doc = ""




        form.name = name
        form.target = target
        form.doc = doc

        state = form.getState()

        self.assertEqual(state[0],name)
        self.assertEqual(state[1],target)
        self.assertEqual(state[2],doc)

        self.assertEqual(len(state),3)
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)

       





    ## constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()


        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')

        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()


        name = "myname"
        target = "NXEntry"
        doc = "My documentation: \n ble ble ble "

        
        self.assertEqual(form.setState(['','','']), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')


        self.assertEqual(form.setState([name,'','']), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name, name)
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')

        form.name = ""



        self.assertEqual(form.setState(['',target,'']), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, target)
        self.assertEqual(form.doc, '')

        form.target = ''





        self.assertEqual(form.setState(['','',doc]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, doc)

        form.doc = ''







        self.assertEqual(form.setState([name,target,doc]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        self.assertEqual(form.name, name)
        self.assertEqual(form.target, target)
        self.assertEqual(form.doc, doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def test_setState_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()


        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')

        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()


        name = "myname"
        target = "$datasources.NXEntry"
        doc = "My documentation: \n ble ble ble "

        
        self.assertEqual(form.setState(['','','']), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')


        self.assertEqual(form.setState([name,'','']), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name, name)
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')

        form.name = ""



        self.assertEqual(form.setState(['',target,'']), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, target)
        self.assertEqual(form.doc, '')

        form.target = ''





        self.assertEqual(form.setState(['','',doc]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, doc)

        form.doc = ''







        self.assertEqual(form.setState([name,target,doc]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


        self.assertEqual(form.name, name)
        self.assertEqual(form.target, target)
        self.assertEqual(form.doc, doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)










        
    ## constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form = LinkDlg()
        form.show()
        self.assertEqual(form.createGUI(),None)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        name = "myname"
        target = "NXEntry"
        target2 = "NX_INT64"
        doc = "My documentation: \n ble ble ble "

        self.assertEqual(form.updateForm(),None)
    

        form = LinkDlg()
        form.show()
        form.name = name


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form = LinkDlg()
        form.show()
        form.target = target


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.targetLineEdit.text(), target)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.targetLineEdit.setText("")
        form.target = ""







        form = LinkDlg()
        form.show()
        form.name = name
        form.doc = doc
        form.target = target


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.targetLineEdit.text(), target)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)


     ## constructor test
    # \brief It tests default settings
    def test_createGUI_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form = LinkDlg()
        form.show()
        self.assertEqual(form.createGUI(),None)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        name = "myname"
        target = "$datasources.NXEntry"
        target2 = "$datasources.NX_INT64"
        doc = "My documentation: \n ble ble ble "

        self.assertEqual(form.updateForm(),None)
    

        form = LinkDlg()
        form.show()
        form.name = name


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form = LinkDlg()
        form.show()
        form.target = target


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.targetLineEdit.text(), target)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        form.ui.targetLineEdit.setText("")
        form.target = ""







        form = LinkDlg()
        form.show()
        form.name = name
        form.doc = doc
        form.target = target


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.targetLineEdit.text(), target)
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
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","mytarget%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"



        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 




        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "mytarget%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, ['doc', 'datasource', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","mytarget%s" %  nn)
        tg =  doc.createTextNode("$datasources.mytarget%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 




        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "$datasources.mytarget%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, ['doc', 'datasource', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())





    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","target%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 





        form = LinkDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode(qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "target%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



     ## constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","mytarget%s" %  nn)
        tg =  doc.createTextNode("$datasources.mytarget%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 





        form = LinkDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode(qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "$datasources.mytarget%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())


       




    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_nonode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","target%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 





        form = LinkDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())




    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_nonode_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","target%s" %  nn)
        tg =  doc.createTextNode("$datasources.target%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 





        form = LinkDlg()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        

    ## constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn) 




        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])



        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())



        





    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","target%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 





        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "target%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())





    ## constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","target%s" %  nn)
        tg =  doc.createTextNode("$datasources.target%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 





        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "$datasources.target%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])


        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.targetLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())




        
        







    ## constructor test
    # \brief It tests default settings
    def test_updateNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","target%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "targete"
        mdoc = "New text \nNew text"


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target
        form.value = "My new value ble ble"


        form.doc = mdoc

        form.root = doc
        

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        form.updateNode()

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)



    ## constructor test
    # \brief It tests default settings
    def test_updateNode_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","target%s" %  nn)
        tg =  doc.createTextNode("$datasources.target%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "$datasources.targete"
        mdoc = "New text \nNew text"


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target
        form.value = "My new value ble ble"


        form.doc = mdoc

        form.root = doc
        

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di


        form.updateNode()

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        tgtext = DomTools.getText(form.node)    
        self.assertEqual(target,unicode(tgtext).strip())
        self.assertEqual(olddoc,mdoc)





        


    ## constructor test
    # \brief It tests default settings
    def test_updateNode_withindex(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","target%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "newtype"
        mdoc = "New text \nNew text"

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target
        form.value = "My new value ble ble"

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
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)

    ## constructor test
    # \brief It tests default settings
    def test_updateNode_withindex_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","target%s" %  nn)
        tg =  doc.createTextNode("$datasources.target%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "$datasources.newtype"
        mdoc = "New text \nNew text"

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)

        tgtext = DomTools.getText(form.node)    
        self.assertEqual("$datasources.target%s" %  nn, unicode(tgtext).strip())


        form.name = nname
        form.target = target
        form.value = "My new value ble ble"

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
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)

        tgtext = DomTools.getText(form.node)    
        self.assertEqual(target,unicode(tgtext).strip())





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
        qdn.setAttribute("target","target%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "newtype"
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
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target
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
        form.ui.targetLineEdit.setText(target)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        form.apply()


        self.assertEqual(form.name, nname)
        self.assertEqual(form.target, target)
        self.assertEqual(form.doc, mdoc)

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl, target)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,mdoc)
        


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl, target)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)



    ## constructor test
    # \brief It tests default settings
    def test_apply_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","target%s" %  nn)
        tg =  doc.createTextNode("$datasources.target%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "$datasources.newtype"
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
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target
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
        form.ui.targetLineEdit.setText(target)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        form.apply()


        self.assertEqual(form.name, nname)
        self.assertEqual(form.target, target)
        self.assertEqual(form.doc, mdoc)

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl, target)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,mdoc)
        


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, nname)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl, target)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)
        tgtext = DomTools.getText(form.node)    
        self.assertEqual(target,unicode(tgtext).strip())




        

    ## constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "newtype"
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.targetLineEdit.setText(target)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        


        form.reset()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])




        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        

    ## constructor test
    # \brief It tests default settings
    def test_reset_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","mytype%s" %  nn)
        tg =  doc.createTextNode("$datasources.mytype%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "$datasources.newtype"
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.targetLineEdit.setText(target)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        


        form.reset()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "$datasources.mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])




        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        tgtext = DomTools.getText(form.node)    
        self.assertEqual("$datasources.mytype%s" %  nn,unicode(tgtext).strip())
        


    ## constructor test
    # \brief It tests default settings
    def test_reset_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("target","mytype%s" %  nn)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "newtype"
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.target = target

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.targetLineEdit.setText(target)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        

    ## constructor test
    # \brief It tests default settings
    def test_reset_button_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        dks = []
        doc = QDomDocument()
        nname = "link"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
#        qdn.setAttribute("target","mytype%s" %  nn)
        tg =  doc.createTextNode("$datasources.mytype%s" %  nn)
        qdn.appendChild(tg)
        doc.appendChild(qdn) 
        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 


        form = LinkDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.target, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        target = "$datasources.newtype"
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,form.name)
                cnt += 1 
            elif nm == "target":
                self.assertEqual(vl,form.target)
                cnt += 1 


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)


        form.name = nname
        form.target = target

        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di




        form.ui.nameLineEdit.setText(nname)
        form.ui.targetLineEdit.setText(target)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.target, "$datasources.mytype%s" %  nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.subItems, 
                         ['doc', 'datasource', 'strategy'])


        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl,  "myname%s" %  nn)
                cnt += 1 
            elif nm == "target":
                self.assertTrue(False)
                self.assertEqual(vl,  "mytype%s" %  nn)
                cnt += 1 

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        tgtext = DomTools.getText(form.node)    
        self.assertEqual("$datasources.mytype%s" %  nn,unicode(tgtext).strip())
        
         




    def myAction(self):
        self.performed = True


    ## constructor test


    ## constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(DomTools, DomTools))

        self.assertEqual(form.result(),0)

    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_LinkDlg))
        self.assertEqual(form.externalApply, None)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
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
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
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
        form = LinkDlg()
        form.createGUI()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(externalDSLink=self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False



        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
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
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
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
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(externalDSLink=self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
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
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.targetLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_apply_button_noname_ds(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.targetLineEdit, "$datasources.namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
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
        form = LinkDlg()
        form.ui = Ui_LinkDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.targetLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_LinkDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)







if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
