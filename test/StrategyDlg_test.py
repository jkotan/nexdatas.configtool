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
# \package test nexdatas
# \file StrategyDlgTest.py
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

from PyQt5.QtTest import QTest
from PyQt5.QtGui import (QApplication, QMessageBox, QTableWidgetItem, QPushButton)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, SIGNAL, QObject, QVariant, QString
from PyQt5.QtXml import QDomNode, QDomDocument, QDomElement


from nxsconfigtool.StrategyDlg import StrategyDlg
from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.AttributeDlg import AttributeDlg
from nxsconfigtool.NodeDlg import NodeDlg
from nxsconfigtool.DimensionsDlg import DimensionsDlg

from nxsconfigtool.ui.ui_strategydlg import Ui_StrategyDlg
from nxsconfigtool.DomTools import DomTools


#  Qt-application
app = None


# if 64-bit machione
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

# test fixture
class StrategyDlgTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        # MessageBox text
        self.text = None
        # MessageBox title
        self.title = None

        # attribute name
        self.aname = "myname"
        # attribute value
        self.avalue = "myentry"

        self.dimensions = [1,2,3,4]

        # action status
        self.performed = False

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 

        self.__rnd = random.Random(self.__seed)



    # test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        
        print "SEED =", self.__seed 
        

    # test closer
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



    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()
        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        
        self.assertEqual(form.replaceText,super(StrategyDlg,form).replaceText )
        self.assertEqual(form.removeElement,super(StrategyDlg,form).removeElement )
        self.assertEqual(form.replaceElement,super(StrategyDlg,form).replaceElement )
        self.assertTrue(form.appendElement is not super(StrategyDlg,form).appendElement )
        self.assertEqual(form.reset,super(StrategyDlg,form).reset )


    # constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()
        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.createGUI()


        self.assertEqual(form.ui.modeComboBox.currentText(), "STEP")
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)

        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        
        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myname"
        nType = "NXEntry"
        QTest.keyClicks(form.ui.triggerLineEdit, name)
        self.assertEqual(form.ui.triggerLineEdit.text(),name)
        QTest.keyClicks(form.ui.postLineEdit, nType)
        self.assertEqual(form.ui.postLineEdit.text(), nType)



        self.assertEqual(form.ui.modeComboBox.currentText(), "STEP")
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertTrue(not form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)

        self.assertTrue(not form.ui.postLineEdit.text().isEmpty())


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.nexusType, nType)

        self.assertEqual(form.result(),0)






    # constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()
        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.createGUI()

        self.assertEqual(form.ui.modeComboBox.currentText(), "STEP")
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)

        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        
        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"
        
        
        self.assertEqual(form.updateForm(),None)
    

        self.assertEqual(form.ui.modeComboBox.currentText(), "STEP")
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())


        
        form.mode = mode

        self.assertEqual(form.ui.modeComboBox.currentText(), "STEP")
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())


        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), mode)
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        form.mode = "STEP"
        index = form.ui.modeComboBox.findText(unicode(form.mode))
        form.ui.modeComboBox.setCurrentIndex(index)



        form.compression = compr

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), compr)
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())
    
        form.compression = False
        form.ui.compressionCheckBox.setChecked(form.compression) 

        form.canfail = canf

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertEqual(form.ui.canFailCheckBox.isChecked(), canf)
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())
    
        form.canfail = False
        form.ui.canFailCheckBox.setChecked(form.canfail) 



        form.shuffle = shuffle

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), shuffle)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())
    
        form.shuffle = True
        form.ui.shuffleCheckBox.setChecked(form.shuffle) 




        form.rate = rate

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), rate)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())
    
        form.rate = 5
        form.ui.rateSpinBox.setValue(form.rate) 



        form.grows = grows

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), grows if grows > 0 else 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())
    
        form.grows = 0
        form.ui.growsSpinBox.setValue(form.grows) 





        form.trigger = trigger


        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.triggerLineEdit.text(), trigger) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())
    
        form.ui.triggerLineEdit.setText("")
        form.trigger = ""




        form.postrun = post


        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty())
        self.assertEqual(form.ui.postLineEdit.text(), post) 
    
        form.ui.postLineEdit.setText("")
        form.postrun = ""






        form.doc = doc

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)
    

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertEqual(form.ui.docTextEdit.toPlainText(),doc)
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        form.ui.docTextEdit.setText("")

        form.mode = mode
        form.compression = compr
        form.canfail = canf
        form.rate = rate
        form.shuffle = shuffle
        form.doc = doc
        form.trigger = trigger
        form.grows = grows
        form.postrun = post







        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        self.assertEqual(form.updateForm(),None)
    

        self.assertEqual(form.ui.modeComboBox.currentText(), mode)
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), compr)
        self.assertEqual(form.ui.canFailCheckBox.isChecked(), canf)
        self.assertEqual(form.ui.rateSpinBox.value(), rate)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), shuffle)
        self.assertEqual(form.ui.triggerLineEdit.text(), trigger) 
        self.assertEqual(form.ui.growsSpinBox.value(), grows if grows>0 else 0)
        self.assertEqual(form.ui.postLineEdit.text(), post)

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def test_getState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()

        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)




        form.createGUI()



        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"
        
        self.assertEqual(form.getState(), ('STEP', u'', u'', u'',False,5,True, False, u''))
    

        form.mode = mode

        self.assertEqual(form.getState(), (mode, u'', u'', u'',False,5,True, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.mode = "STEP"



        form.trigger = trigger

        self.assertEqual(form.getState(), ('STEP', trigger, u'', u'',False,5,True, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.trigger = ""




        form.grows = grows
        self.assertEqual(form.getState(), ('STEP', u'', grows, u'',False,5,True, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.grows = ""



        form.postrun = post
        self.assertEqual(form.getState(), ('STEP', u'', u'', post, False,5,True, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.postrun = ""




        form.compression = compr
        self.assertEqual(form.getState(), ('STEP', u'', u'', u'', compr,5,True, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.compression = False



        form.canfail = canf
        self.assertEqual(form.getState(), ('STEP', u'', u'', u'', False,5,True, canf, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.canfail = False



        form.rate = rate
        self.assertEqual(form.getState(), ('STEP', u'', u'', u'', False,rate,True, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.rate = 5



        form.shuffle = shuffle
        self.assertEqual(form.getState(), ('STEP', u'', u'', u'', False,5,shuffle, False, u''))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.shuffle = True



        form.doc = doc
        self.assertEqual(form.getState(), ('STEP', u'', u'', u'', False,5,True, False, doc))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        form.doc = u''


        form.mode = mode
        form.trigger = trigger
        form.grows = grows
        form.postrun = post
        form.compression = compr
        form.canfail = canf
        form.rate = rate
        form.shuffle = shuffle
        form.doc = doc

        self.assertEqual(form.getState(), (mode,trigger, grows,post,compr,rate, shuffle, canf, doc))
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)





    # constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()

        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)



        form.createGUI()


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"

    
        self.assertEqual(form.setState([mode,  u'', u'', u'', False, 5,True,False, u'']),None)
                         
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.mode = ""


        self.assertEqual(form.setState(['STEP',  trigger, u'', u'', False, 5,True, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.trigger = ""


        self.assertEqual(form.setState(['STEP',  u'', grows, u'', False, 5,True, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, grows)
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.grows = ""




        self.assertEqual(form.setState(['STEP',  u'', u'', post , False, 5,True, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.postrun = ""



        self.assertEqual(form.setState(['STEP',  u'', u'', u'', compr, 5,True, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.compression = False





        self.assertEqual(form.setState(['STEP',  u'', u'', u'', False, 5,True, canf, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.canfail = False





        self.assertEqual(form.setState(['STEP',  u'', u'', u'', False, rate,True, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.rate = 5



        self.assertEqual(form.setState(['STEP',  u'', u'', u'', False, 5,shuffle, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, shuffle)
        self.assertEqual(form.doc, '')

        form.shuffle = True



        self.assertEqual(form.setState(['STEP',  u'', u'', u'', False, 5,True, False, doc]),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, doc)

        form.doc = ''



        self.assertEqual(form.setState([mode, trigger, grows, post, compr, rate, shuffle, canf, doc]),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger,trigger)
        self.assertEqual(form.grows, grows)
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle, shuffle)
        self.assertEqual(form.doc, doc)

        form.doc = ''


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)







    # constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()


        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.compression, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)



        form = StrategyDlg()
        form.show()
        self.assertEqual(form.createGUI(),None)

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"


        self.assertEqual(form.updateForm(),None)

        form = StrategyDlg()
        form.show()

        form.mode = mode

        self.assertEqual(form.createGUI(),None)

        

    
        self.assertEqual(form.ui.modeComboBox.currentText(), mode)
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.mode = ""


        form = StrategyDlg()
        form.show()

        form.trigger = trigger

        self.assertEqual(form.createGUI(),None)

    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.triggerLineEdit.text(), trigger) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.compression, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.trigger = ""
 
        form = StrategyDlg()
        form.show()

        form.grows = grows

        self.assertEqual(form.createGUI(),None)


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), grows if grows >0 else 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, grows )
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.compression, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.grows = ""


        form = StrategyDlg()
        form.show()

        form.postrun = post

        self.assertEqual(form.createGUI(), None)


        self.assertEqual(form.setState(['STEP',  u'', u'', post , False, 5,True, False, u'']),None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertEqual(form.ui.postLineEdit.text(),post)



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.postrun = ""


        form = StrategyDlg()
        form.show()

        form.compression = compr

        self.assertEqual(form.createGUI(), None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), compr)
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.compression = False




        form = StrategyDlg()
        form.show()

        form.canfail = canf

        self.assertEqual(form.createGUI(), None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), False)
        self.assertEqual(form.ui.canFailCheckBox.isChecked(), canf)
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.canfail = False



        form = StrategyDlg()
        form.show()

        form.rate = rate

        self.assertEqual(form.createGUI(), None)


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), rate)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')

        form.rate = 5


        form = StrategyDlg()
        form.show()

        form.shuffle = shuffle

        self.assertEqual(form.createGUI(), None)


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), shuffle)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, shuffle)
        self.assertEqual(form.doc, '')

        form.shuffle = True



        form = StrategyDlg()
        form.show()

        form.doc = doc

        self.assertEqual(form.createGUI(), None)

    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())



        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, doc)

        form.doc = ''


        form = StrategyDlg()
        form.show()

        form.mode = mode
        form.trigger = trigger
        form.grows = grows
        form.postrun = post
        form.compression = compr
        form.canfail = canf
        form.rate = rate
        form.shuffle = shuffle
        form.doc = doc


        self.assertEqual(form.createGUI(), None)
    
        self.assertEqual(form.ui.modeComboBox.currentText(), mode)
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), compr)
        self.assertEqual(form.ui.canFailCheckBox.isChecked(),canf)
        self.assertEqual(form.ui.rateSpinBox.value(), rate)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), shuffle)
        self.assertEqual(form.ui.docTextEdit.toPlainText(),doc)
        self.assertEqual(form.ui.triggerLineEdit.text(), trigger) 
        self.assertEqual(form.ui.growsSpinBox.value(), grows if grows>0 else 0)
        self.assertEqual(form.ui.postLineEdit.text(), post)



        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger,trigger)
        self.assertEqual(form.grows, grows)
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle, shuffle)
        self.assertEqual(form.doc, doc)

        form.doc = ''
    



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)



    # constructor test
    # \brief It tests default settings
    def test_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 




        form = StrategyDlg()
        form.show()
        form.node = qdn

        form.createGUI()

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        
        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.compression, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')


        form.setFromNode()


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), False)
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), True)
        self.assertEqual(form.ui.docTextEdit.toPlainText(),'')
        self.assertEqual(form.ui.triggerLineEdit.text(), '') 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertEqual(form.ui.postLineEdit.text(), '')

        
        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger,trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr )
        self.assertEqual(form.canfail, canf )
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle, shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())








    # constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 




        form = StrategyDlg()
        form.show()

        form.createGUI()

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        
        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')


        form.setFromNode(qdn)


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), False)
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), True)
        self.assertEqual(form.ui.docTextEdit.toPlainText(),'')
        self.assertEqual(form.ui.triggerLineEdit.text(), '') 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertEqual(form.ui.postLineEdit.text(), '')

        
        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger,trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr )
        self.assertEqual(form.canfail, canf )
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle, shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())









    # constructor test
    # \brief It tests default settings
    def test_setFromNode_nonode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 




        form = StrategyDlg()
        form.show()

        form.createGUI()

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        
        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')


        form.setFromNode()


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), False)
        self.assertEqual(form.ui.canFailCheckBox.isChecked(), False)
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), True)
        self.assertEqual(form.ui.docTextEdit.toPlainText(),'')
        self.assertEqual(form.ui.triggerLineEdit.text(), '') 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertEqual(form.ui.postLineEdit.text(), '')

        
        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False )
        self.assertEqual(form.canfail, False )
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, "")








    # constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        doc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"

        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn) 

        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 




        form = StrategyDlg()
        form.show()

        form.createGUI()

        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertTrue(not form.ui.compressionCheckBox.isChecked())
        self.assertTrue(not form.ui.canFailCheckBox.isChecked())
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertTrue(form.ui.shuffleCheckBox.isChecked())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.triggerLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertTrue(form.ui.postLineEdit.text().isEmpty())

        
        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, '')


        form.setFromNode()


    
        self.assertEqual(form.ui.modeComboBox.currentText(), 'STEP')
        self.assertEqual(form.ui.compressionCheckBox.isChecked(), False)
        self.assertEqual(form.ui.canFailCheckBox.isChecked(), False)
        self.assertEqual(form.ui.rateSpinBox.value(), 5)
        self.assertEqual(form.ui.shuffleCheckBox.isChecked(), True)
        self.assertEqual(form.ui.docTextEdit.toPlainText(),'')
        self.assertEqual(form.ui.triggerLineEdit.text(), '') 
        self.assertEqual(form.ui.growsSpinBox.value(), 0)
        self.assertEqual(form.ui.postLineEdit.text(), '')

        
        self.assertEqual(form.mode, 'STEP')
        self.assertEqual(form.trigger,'')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False )
        self.assertEqual(form.canfail, False )
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle, True)
        self.assertEqual(form.doc, "")














    # constructor test
    # \brief It tests default settings
    def test_updateNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        ndoc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 




        form = StrategyDlg()
        form.show()
        form.node = qdn


        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, qdn)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        

        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,form.mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,form.trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,form.grows)
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(form.compression))
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(form.canfail))
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(form.rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(form.shuffle))
                cnt += 1 




        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"


        form.mode =  nmode
        form.compression = ncompr
        form.canfail = ncanf
        form.postrun = npost
        form.rate = nrate
        form.shuffle = nshuffle
        form.doc = nmdoc
        form.trigger = ntrigger
        form.grows = ngrows



        form.root = doc
        



        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    

        form.updateNode()

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    


        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

#        self.assertEqual(olddoc,"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(olddoc,nmdoc.strip())






    # constructor test
    # \brief It tests default settings
    def test_updateNode_withindex(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        ndoc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 


        form = StrategyDlg()
        form.show()
        form.node = qdn


        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, qdn)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)


        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"



        form.mode =  nmode
        form.compression = ncompr
        form.canfail = ncanf
        form.postrun = npost
        form.rate = nrate
        form.shuffle = nshuffle
        form.doc = nmdoc
        form.trigger = ntrigger
        form.grows = ngrows



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
            if nm == "mode":
                self.assertEqual(vl,form.mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,form.trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(form.grows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(form.compression).lower())
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(form.canfail).lower())
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(form.rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(form.shuffle).lower())
                cnt += 1 


        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    

        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,nmdoc.strip())





    # constructor test
    # \brief It tests default settings
    def test_apply(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        ndoc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 


        form = StrategyDlg()
        form.show()
        form.node = qdn




        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, qdn)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,form.mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,form.trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(form.grows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(form.compression))
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(form.canfail))
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(form.rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(form.shuffle))
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)

        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())



        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di



        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"

        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())


        form.mode =  nmode
        form.compression = ncompr
        form.canfail = ncanf
        form.postrun = npost
        form.rate = nrate
        form.shuffle = nshuffle
        form.doc = nmdoc
        form.trigger = ntrigger
        form.grows = ngrows


        
        index = form.ui.modeComboBox.findText(unicode(nmode))
        if  index > -1 :
            form.ui.modeComboBox.setCurrentIndex(index)
        form.ui.compressionCheckBox.setChecked(ncompr) 
        form.ui.canFailCheckBox.setChecked(ncanf) 
        form.ui.rateSpinBox.setValue(nrate)
        form.ui.shuffleCheckBox.setChecked(nshuffle) 
        form.ui.triggerLineEdit.setText(ntrigger) 
        form.ui.growsSpinBox.setValue(ngrows if ngrows>0 else 0) 


        form.ui.postLineEdit.setText(npost) 
        form.ui.docTextEdit.setText(nmdoc)


        form.apply()

        
        self.assertEqual(form.mode, nmode)
        self.assertEqual(form.trigger, ntrigger if nmode =='STEP' else '')
        self.assertEqual(form.grows, str(ngrows) if nmode =='STEP' and ngrows > 0  else '')
        self.assertEqual(form.postrun, npost if nmode =='POSTRUN' else '')
        self.assertEqual(form.compression, ncompr)
        self.assertEqual(form.canfail, ncanf)
        self.assertEqual(form.rate, nrate)
        self.assertEqual(form.shuffle,nshuffle)
        self.assertEqual(form.doc, nmdoc)



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,nmode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,ntrigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(ngrows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(ncompr).lower())
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(ncanf).lower())
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(nrate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(nshuffle).lower())
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,nmdoc.strip())

        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,npost if nmode =='POSTRUN' else '')

 





    # constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        ndoc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 


        form = StrategyDlg()
        form.show()
        form.node = qdn




        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, qdn)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,form.mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,form.trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(form.grows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(form.compression))
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(form.canfail))
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(form.rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(form.shuffle))
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)

        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())



        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di



        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"

        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())


        form.mode =  nmode
        form.compression = ncompr
        form.canfail = ncanf
        form.postrun = npost
        form.rate = nrate
        form.shuffle = nshuffle
        form.doc = nmdoc
        form.trigger = ntrigger
        form.grows = ngrows


        
        index = form.ui.modeComboBox.findText(unicode(nmode))
        if  index > -1 :
            form.ui.modeComboBox.setCurrentIndex(index)
        form.ui.compressionCheckBox.setChecked(ncompr) 
        form.ui.canFailCheckBox.setChecked(ncanf) 
        form.ui.rateSpinBox.setValue(nrate)
        form.ui.shuffleCheckBox.setChecked(nshuffle) 
        form.ui.triggerLineEdit.setText(ntrigger) 
        form.ui.growsSpinBox.setValue(ngrows if ngrows>0 else 0) 


        form.ui.postLineEdit.setText(npost) 
        form.ui.docTextEdit.setText(nmdoc)


        form.reset()

        
        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(grows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(compr))
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(canf))
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(shuffle))
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())

        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,post)

 





    def test_reset_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        mode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        compr = self.__rnd.choice([True, False])
        canf = self.__rnd.choice([True, False])
        rate = self.__rnd.randint(0, 9) 
        shuffle = self.__rnd.choice([True, False])
        ndoc = "My documentation: \n ble ble ble "
        trigger = "MyTrigger"
        grows = self.__rnd.randint(-1, 3) 
        post = "Pilatus300k"



        dks = []
        doc = QDomDocument()
        nname = "strategy"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("mode",mode)
        qdn.setAttribute("compression","True" if compr else "False")
        qdn.setAttribute("canfail","True" if canf else "False")
        qdn.setAttribute("rate",rate)
        qdn.setAttribute("shuffle", "True" if shuffle else "False")
        qdn.setAttribute("trigger",trigger)
        qdn.setAttribute("grows",grows)
        
        
        doc.appendChild(qdn) 
        dname = "doc"


        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

        dval = []
        dval.append(doc.createTextNode(post))
        qdn.appendChild(dval[-1]) 


        form = StrategyDlg()
        form.show()
        form.node = qdn




        self.assertEqual(form.mode, '')
        self.assertEqual(form.trigger, '')
        self.assertEqual(form.grows, '')
        self.assertEqual(form.postrun, '')
        self.assertEqual(form.compression, False)
        self.assertEqual(form.canfail, False)
        self.assertEqual(form.rate, 5)
        self.assertEqual(form.shuffle,True)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.node, qdn)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['doc'] )
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        form.setFromNode()
        form.createGUI()
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"


        attributeMap = form.node.attributes()
        
        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,form.mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,form.trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(form.grows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(form.compression))
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(form.canfail))
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(form.rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(form.shuffle))
                cnt += 1 

        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.postrun)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)

        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())



        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di



        nmode = self.__rnd.choice(['INIT','STEP', 'FINAL', 'POSTRUN'])
        ncompr = self.__rnd.choice([True, False])
        ncanf = self.__rnd.choice([True, False])
        nrate = self.__rnd.randint(0, 9) 
        nshuffle = self.__rnd.choice([True, False])
        nmdoc = "My new documentation: \n ble ble ble "
        ntrigger = "MyTrigger2"
        ngrows = self.__rnd.randint(-1, 3) 
        npost = "Pilatus1M"

        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())


        form.mode =  nmode
        form.compression = ncompr
        form.canfail = ncanf
        form.postrun = npost
        form.rate = nrate
        form.shuffle = nshuffle
        form.doc = nmdoc
        form.trigger = ntrigger
        form.grows = ngrows


        
        index = form.ui.modeComboBox.findText(unicode(nmode))
        if  index > -1 :
            form.ui.modeComboBox.setCurrentIndex(index)
        form.ui.compressionCheckBox.setChecked(ncompr) 
        form.ui.canFailCheckBox.setChecked(ncanf) 
        form.ui.rateSpinBox.setValue(nrate)
        form.ui.shuffleCheckBox.setChecked(nshuffle) 
        form.ui.triggerLineEdit.setText(ntrigger) 
        form.ui.growsSpinBox.setValue(ngrows if ngrows>0 else 0) 


        form.ui.postLineEdit.setText(npost) 
        form.ui.docTextEdit.setText(nmdoc)


        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)

        
        self.assertEqual(form.mode, mode)
        self.assertEqual(form.trigger, trigger)
        self.assertEqual(form.grows, str(grows))
        self.assertEqual(form.postrun, post)
        self.assertEqual(form.compression, compr)
        self.assertEqual(form.canfail, canf)
        self.assertEqual(form.rate, rate)
        self.assertEqual(form.shuffle,shuffle)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())



        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "mode":
                self.assertEqual(vl,mode)
                cnt += 1 
            elif nm == "trigger":
                self.assertEqual(vl,trigger)
                cnt += 1 
            elif nm == "grows":
                self.assertEqual(vl,str(grows))
                cnt += 1 
            elif nm == "compression":
                self.assertEqual(vl,str(compr))
                cnt += 1 
            elif nm == "canfail":
                self.assertEqual(vl,str(canf))
                cnt += 1 
            elif nm == "rate":
                self.assertEqual(vl,str(rate))
                cnt += 1 
            elif nm == "shuffle":
                self.assertEqual(vl,str(shuffle))
                cnt += 1 



        mydoc = form.node.firstChildElement(QString("doc"))           
        text = DomTools.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())

        
        vtext = DomTools.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,post)

 












    def myAction(self):
        self.performed = True


    # constructor test


    # constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(DomTools, DomTools))

        self.assertEqual(form.result(),0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_StrategyDlg))
        self.assertEqual(form.externalApply, None)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)


        self.assertEqual(form.result(),0)



    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)






    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.createGUI()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(externalDSLink=self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False



        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def ttest_connect_actions_with_action_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)





    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_sapply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
 #       QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)


    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_slink_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
#        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(externalDSLink=self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply,None)
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.linkDSPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
#        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)





    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = StrategyDlg()
        form.ui = Ui_StrategyDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
#        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_StrategyDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)







if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
