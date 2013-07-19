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
## \file CommonDataSourceDlgTest.py
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


from ndtsconfigtool.DataSourceDlg import CommonDataSourceDlg, DataSource
from ndtsconfigtool.ComponentModel import ComponentModel
from ndtsconfigtool.AttributeDlg import AttributeDlg
from ndtsconfigtool.NodeDlg import NodeDlg
from ndtsconfigtool.DimensionsDlg import DimensionsDlg

from ndtsconfigtool.ui.ui_datasourcedlg import Ui_DataSourceDlg


##  Qt-application
app = None


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

class FocusedWidget():
    def __init__(self):
        self.focused = False
    def setFocus(self):
        self.focused = True

        

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
class CommonDataSourceDlgTest(unittest.TestCase):

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


        self.__rnd = random.Random(self.__seed)


        self.form = None

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
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()


    def rmParamWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.Yes), Qt.LeftButton)


    def rmParamWidgetClose(self):
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



    def attributeWidgetClose(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

        mb.reject()


    def paramWidgetClose(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(),self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(),self.avalue)

        mb.reject()



    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = QMessageBox()
        dsrc = DataSource(parent)
        form = CommonDataSourceDlg(dsrc, parent)
        form.show()

        self.assertEqual(form.datasource, dsrc)
        self.assertEqual(form.dbParam, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ["record", "doc", "device", "database", "query"])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        
        self.assertEqual(form.replaceText,super(CommonDataSourceDlg,form).replaceText )
        self.assertEqual(form.removeElement,super(CommonDataSourceDlg,form).removeElement )
        self.assertEqual(form.replaceElement,super(CommonDataSourceDlg,form).replaceElement )
        self.assertTrue(form.appendElement is not super(CommonDataSourceDlg,form).appendElement )
        self.assertEqual(form.reset,super(CommonDataSourceDlg,form).reset )


    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept_setFocus(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        form = CommonDataSourceDlg(dsrc, parent)
        form.show()

        self.assertEqual(form.datasource, dsrc)
        self.assertEqual(form.dbParam, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ["record", "doc", "device", "database", "query"])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceDlg))
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        
        self.assertEqual(form.replaceText,super(CommonDataSourceDlg,form).replaceText )
        self.assertEqual(form.removeElement,super(CommonDataSourceDlg,form).removeElement )
        self.assertEqual(form.replaceElement,super(CommonDataSourceDlg,form).replaceElement )
        self.assertTrue(form.appendElement is not super(CommonDataSourceDlg,form).appendElement )
        self.assertEqual(form.reset,super(CommonDataSourceDlg,form).reset )


        form.ui.setupUi(form)
        form.show()
        
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeComboBox.currentText(), "CLIENT") 
        
        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())
        name = "myname"
        nType = "NXEntry"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)

        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)

        form.ui.savePushButton = FocusedWidget()
        self.assertTrue(not form.ui.savePushButton.focused)
        form.setSaveFocus()
        self.assertTrue(form.ui.savePushButton.focused)
        

    def enableButtons(self):   
        self.assertTrue(self.form.ui.savePushButton.isEnabled())
        self.assertTrue(self.form.ui.applyPushButton.isEnabled())
        self.assertTrue(self.form.ui.storePushButton.isEnabled())

    def disableButtons(self):    
        self.assertTrue(not self.form.ui.savePushButton.isEnabled())
        self.assertTrue(not self.form.ui.applyPushButton.isEnabled())
        self.assertTrue(not self.form.ui.storePushButton.isEnabled())

    def clientVisible(self):    
        self.assertTrue(self.form.ui.clientFrame.isVisible())
        self.assertTrue(not self.form.ui.dbFrame.isVisible())
        self.assertTrue(not self.form.ui.tangoFrame.isVisible())


    def dbVisible(self):    
        self.assertTrue(not self.form.ui.clientFrame.isVisible())
        self.assertTrue(self.form.ui.dbFrame.isVisible())
        self.assertTrue(not self.form.ui.tangoFrame.isVisible())


    def tangoVisible(self):    
        self.assertTrue(not self.form.ui.clientFrame.isVisible())
        self.assertTrue(not self.form.ui.dbFrame.isVisible())
        self.assertTrue(self.form.ui.tangoFrame.isVisible())

    def noneVisible(self):    
        self.assertTrue(not self.form.ui.clientFrame.isVisible())
        self.assertTrue(not self.form.ui.dbFrame.isVisible())
        self.assertTrue(not self.form.ui.tangoFrame.isVisible())




    ## constructor test
    # \brief It tests default settings
    def test_updateUi(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        
        self.enableButtons()
        self.form.updateUi("")
        self.enableButtons()
        tm = QTimer() 
        self.enableButtons() 
        time.sleep(0.1)

        self.form.updateUi("CLIENT")
        self.disableButtons()
        
        self.form.ui.cRecNameLineEdit.setText("name")
        self.form.updateUi("CLIENT")
        self.enableButtons()


        self.form.ui.cRecNameLineEdit.setText("")
        self.form.updateUi("CLIENT")
        self.disableButtons()


        self.form.ui.dQueryLineEdit.setText("name")
        self.form.updateUi("DB")
        self.enableButtons()




        self.form.ui.tDevNameLineEdit.setText("name")
        self.form.updateUi("TANGO")
        self.disableButtons()

        self.form.ui.tMemberNameLineEdit.setText("name")
        self.form.updateUi("TANGO")
        self.enableButtons()

        self.form.ui.tDevNameLineEdit.setText("")
        self.form.updateUi("TANGO")
        self.disableButtons()
        
        





    ## constructor test
    # \brief It tests default settings
    def test_setFrames(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.noneVisible()

        self.form.setFrames("")
        self.enableButtons()
        self.noneVisible()


        self.form.setFrames("CLIENT")
        self.clientVisible()
        self.disableButtons()
        

        self.form.ui.cRecNameLineEdit.setText("")
        self.form.setFrames("CLIENT")
        self.clientVisible()
        self.disableButtons()

        self.form.ui.cRecNameLineEdit.setText("name")
        self.form.setFrames("CLIENT")
        self.clientVisible()
        self.enableButtons()






        self.form.ui.dQueryLineEdit.setText("")
        self.form.setFrames("DB")
        self.dbVisible()
        self.disableButtons()


        self.form.ui.dQueryLineEdit.setText("name")
        self.form.setFrames("DB")
        self.dbVisible()
        self.enableButtons()



        myParam = {"DB Name":"sdfsdf",
                   "DB host":"werwer", 
                   "DB port":"werwer", 
                   "DB user":"werwer", 
                   "DB password":"werwer", 
                   "Mysql cnf":"werwer", 
                   "ORACLE mode":"werwer", 
                   "Oracle DSN":"asdasdf"}        

 


        self.form.ui.dQueryLineEdit.setText("name")
        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = myParam
        self.form.populateParameters(sel)
        self.assertEqual(self.form.dbParam,myParam)
        
        self.form.setFrames("DB")
        self.assertEqual(self.form.dbParam,myParam)
        self.dbVisible()
        self.enableButtons()
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, None)




        self.form.setFrames("TANGO")
        self.tangoVisible()
        self.disableButtons()


        self.form.ui.tDevNameLineEdit.setText("name")
        self.form.setFrames("TANGO")
        self.tangoVisible()
        self.disableButtons()

        self.form.ui.tMemberNameLineEdit.setText("name")
        self.form.setFrames("TANGO")
        self.tangoVisible()
        self.enableButtons()

        self.form.ui.tDevNameLineEdit.setText("")
        self.form.setFrames("TANGO")
        self.tangoVisible()
        self.disableButtons()
        



    ## constructor test
    # \brief It tests default settings
    def test_setFrames_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.noneVisible()


        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("CLIENT"))

        self.enableButtons()
        self.noneVisible()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("DB"))


        self.enableButtons()
        self.noneVisible()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))


        self.enableButtons()
        self.noneVisible()

        self.form.connectWidgets()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))


        self.enableButtons()
        self.noneVisible()


        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("CLIENT"))
        self.clientVisible()
        self.disableButtons()

        self.form.ui.cRecNameLineEdit.setText("")
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("CLIENT"))
        self.clientVisible()
        self.disableButtons()

        self.form.ui.cRecNameLineEdit.setText("name")

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("CLIENT"))
        self.clientVisible()
        self.enableButtons()






        self.form.ui.dQueryLineEdit.setText("")
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("DB"))
        self.dbVisible()
        self.disableButtons()


        self.form.ui.dQueryLineEdit.setText("name")
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("DB"))
        self.dbVisible()
        self.enableButtons()


        myParam = {"DB Name":"sdfsdf",
                   "DB host":"werwer", 
                   "DB port":"werwer", 
                   "DB user":"werwer", 
                   "DB password":"werwer", 
                   "Mysql cnf":"werwer", 
                   "ORACLE mode":"werwer", 
                   "Oracle DSN":"asdasdf"}        

 


        self.form.ui.dQueryLineEdit.setText("name")
        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = myParam
        self.form.populateParameters(sel)
        self.assertEqual(self.form.dbParam,myParam)
        
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("DB"))
        self.assertEqual(self.form.dbParam,myParam)
        self.dbVisible()
        self.enableButtons()
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, None)


        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))
        self.tangoVisible()
        self.disableButtons()


        self.form.ui.tDevNameLineEdit.setText("name")
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))
        self.tangoVisible()
        self.disableButtons()

        self.form.ui.tMemberNameLineEdit.setText("name")
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))
        self.tangoVisible()
        self.enableButtons()

        self.form.ui.tDevNameLineEdit.setText("")
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))
        self.tangoVisible()
        self.disableButtons()
        
        

        



    ## constructor test
    # \brief It tests default settings
    def test_cRecNameLineEdit_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.cRecNameLineEdit.setText("")
        self.enableButtons()
        
        self.form.connectWidgets()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("CLIENT"))
        self.form.ui.cRecNameLineEdit.setText("")
        self.disableButtons()
        
        self.form.ui.cRecNameLineEdit.setText("name")
        self.enableButtons()


        self.form.ui.cRecNameLineEdit.setText("")
        self.disableButtons()



    ## constructor test
    # \brief It tests default settings
    def test_dQueryLineEdit_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.dQueryLineEdit.setText("")
        self.enableButtons()
        
        self.form.connectWidgets()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("DB"))
        self.form.ui.dQueryLineEdit.setText("")
        self.disableButtons()
        
        self.form.ui.dQueryLineEdit.setText("name")
        self.enableButtons()


        self.form.ui.dQueryLineEdit.setText("")
        self.disableButtons()





    ## constructor test
    # \brief It tests default settings
    def test_tDevNameLineEdit_tMemberNameLineEdit_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.tDevNameLineEdit.setText("")
        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.tMemberNameLineEdit.setText("")
        self.enableButtons()

        
        self.form.connectWidgets()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))
        self.form.ui.tDevNameLineEdit.setText("")
        self.disableButtons()
        
        self.form.ui.tDevNameLineEdit.setText("name")
        self.disableButtons()

        self.form.ui.tMemberNameLineEdit.setText("name2")
        self.enableButtons()


        self.form.ui.tDevNameLineEdit.setText("")
        self.disableButtons()

        self.form.ui.tMemberNameLineEdit.setText("name2")
        self.disableButtons()


        self.form.ui.tMemberNameLineEdit.setText("name2")
        self.disableButtons()

        self.form.ui.tDevNameLineEdit.setText("name")
        self.enableButtons()

        






    def checkParam(self, param, table, sel = None):   

        self.assertEqual(table.columnCount(),2)
        self.assertEqual(table.rowCount(),len(param))
        for i in range(len(param)):
            it = table.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in param.keys())
            it2 = table.item(i, 1) 
            self.assertEqual(it2.text(), param[k])

        if sel is not None:    
            item = table.item(table.currentRow(), 0)
            self.assertEqual(item.data(Qt.UserRole).toString(),sel)
 


    ## constructor test
    # \brief It tests default settings
    def test_populateParameters(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.dQueryLineEdit.setText("")
        self.enableButtons()
        
        self.form.connectWidgets()

        myParam = {}        
        self.form.dbParam = myParam
        self.form.populateParameters()
        self.checkParam(myParam, self.form.ui.dParameterTableWidget)


        myParam = {"user":"sdfsdf","sdfsd":"werwer", "asdas":"asdasdf"}        
        self.form.dbParam = myParam
        self.form.populateParameters()
        self.checkParam(myParam, self.form.ui.dParameterTableWidget)


        myParam = {"user":"sdfsdf","sdfsd":"werwer", "asdas":"asdasdf"}        
        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = myParam
        self.form.populateParameters(sel)
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, sel)


        myParam = {"DB name":"sdfsdf",
                   "DB host":"werwer", 
                   "DB port":"werwer", 
                   "DB user":"werwer", 
                   "DB password":"werwer", 
                   "Mysql cnf":"werwer", 
                   "ORACLE mode":"werwer", 
                   "Oracle DSN":"asdasdf"}        

        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = myParam
        self.form.populateParameters(sel)
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, sel)


    ## constructor test
    # \brief It tests default settings
    def test_populateParameters_addremoveParamter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.dQueryLineEdit.setText("")
        self.enableButtons()
        
        self.form.connectWidgets()


        myParam = {
#            "DB name":"sdfsdf",
            "DB host":"wer", 
            "DB port":"wwer", 
            "DB user":"erwer", 
            "DB password":"weer", 
            "Mysql cnf":"weer", 
            "ORACLE mode":"wwer", 
            "Oracle DSN":"aasdf"}        
        
        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = dict(myParam)
        self.form.populateParameters(sel)
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, sel)



        QTest.mouseClick(self.form.ui.dAddPushButton, Qt.LeftButton)
        
        table = self.form.ui.dParameterTableWidget

        item = table.item(table.currentRow(), 0)
        self.checkParam(dict(myParam,**{"DB name":""}), 
                        self.form.ui.dParameterTableWidget, item.data(Qt.UserRole).toString())
        self.checkParam(dict(myParam,**{"DB name":""}), 
                        self.form.ui.dParameterTableWidget, "DB name")
        self.assertEqual(self.form.dbParam, dict(myParam,**{"DB name":""}))
        
        QTimer.singleShot(10, self.rmParamWidgetClose)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)

        self.checkParam(dict(myParam,**{"DB name":""}), 
                        self.form.ui.dParameterTableWidget, "DB name")
        self.assertEqual(self.form.dbParam, dict(myParam,**{"DB name":""}))

        QTimer.singleShot(10, self.rmParamWidget)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)

        self.checkParam(myParam, self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(myParam))




        QTest.mouseClick(self.form.ui.dAddPushButton, Qt.LeftButton)
        
        table = self.form.ui.dParameterTableWidget

        ch = table.currentRow()
        item = table.item(ch, 0)

        pname = str(item.data(Qt.UserRole).toString())


        it = QTableWidgetItem(unicode(pname))
        it.setData(Qt.DisplayRole, QVariant("Myname2"))
        it.setData(Qt.UserRole, QVariant(pname))


        table.setItem(ch,0,it)

        self.checkParam(dict(myParam,**{"DB name":"Myname2"}), 
                        self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(myParam,**{"DB name":"Myname2"}))
        
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)
        table.setCurrentCell(ch,0)

        self.checkParam(dict(myParam,**{"DB name":"Myname2"}), 
                        self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(myParam,**{"DB name":"Myname2"}))

        QTimer.singleShot(10, self.rmParamWidgetClose)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)

        self.checkParam(dict(myParam,**{"DB name":"Myname2"}), 
                        self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(myParam,**{"DB name":"Myname2"}))

        QTimer.singleShot(10, self.rmParamWidget)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)

        self.checkParam(myParam, self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(myParam))






    ## constructor test
    # \brief It tests default settings
    def test_populateParameters_changeParamter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.dQueryLineEdit.setText("")
        self.enableButtons()
        
        self.form.connectWidgets()


        myParam = {
            "DB name":"sdfsdf",
            "DB host":"wer", 
            "DB port":"wwer", 
            "DB user":"erwer", 
            "DB password":"weer", 
            "Mysql cnf":"weer", 
            "ORACLE mode":"wwer", 
            "Oracle DSN":"aasdf"}        
        
        table = self.form.ui.dParameterTableWidget

        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = dict(myParam)
        self.form.populateParameters(sel)
        self.checkParam(myParam, table, sel)

        if sel == "DB password":
            QTimer.singleShot(10, self.checkMessageBox)
        self.form.ui.dParamComboBox.setCurrentIndex(self.form.ui.dParamComboBox.findText(str(sel)))
        
        ch = table.currentRow()


        QTest.mouseClick(self.form.ui.dAddPushButton, Qt.LeftButton)
        


        item = table.item(table.currentRow(), 0)
        self.checkParam(dict(myParam,**{str(sel):myParam[sel]}), 
                        self.form.ui.dParameterTableWidget, item.data(Qt.UserRole).toString())
        self.checkParam(dict(myParam,**{str(sel):myParam[sel]}), 
                        self.form.ui.dParameterTableWidget, sel)
        self.assertEqual(self.form.dbParam, dict(myParam,**{str(sel):myParam[sel]}))
        
        QTimer.singleShot(10, self.rmParamWidgetClose)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)

        self.checkParam(dict(myParam,**{str(sel):myParam[sel]}), 
                        self.form.ui.dParameterTableWidget, str(sel))        
        self.assertEqual(self.form.dbParam, dict(myParam,**{str(sel):myParam[sel]}))

        QTimer.singleShot(10, self.rmParamWidget)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)
        
        rparam = dict(myParam)
        del rparam[sel]
        self.checkParam(rparam, self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(rparam))





    ## constructor test
    # \brief It tests default settings
    def test_populateParameters_changeParamter_value(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        parent = None
        dsrc = DataSource(parent)
        self.form = CommonDataSourceDlg(dsrc, parent)
        self.form.show()

        self.form.ui.setupUi(self.form)
        

        self.enableButtons()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))
        self.form.ui.dQueryLineEdit.setText("")
        self.enableButtons()
        
        self.form.connectWidgets()


        myParam = {
            "DB name":"sdfsdf",
            "DB host":"wer", 
            "DB port":"wwer", 
            "DB user":"erwer", 
            "DB password":"weer", 
            "Mysql cnf":"weer", 
            "ORACLE mode":"wwer", 
            "Oracle DSN":"aasdf"}        
        
        table = self.form.ui.dParameterTableWidget

        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        sel = "DB password"
        self.form.dbParam = dict(myParam)
        self.form.populateParameters(sel)
        self.checkParam(myParam, table, sel)

        if sel == "DB password":
            QTimer.singleShot(10, self.checkMessageBox)
        self.form.ui.dParamComboBox.setCurrentIndex(self.form.ui.dParamComboBox.findText(str(sel)))
        
        ch = table.currentRow()


        QTest.mouseClick(self.form.ui.dAddPushButton, Qt.LeftButton)
        
        item = table.item(ch, 0)

        pname = str(item.data(Qt.UserRole).toString())


        it = QTableWidgetItem(unicode(pname))
        it.setData(Qt.DisplayRole, QVariant("Myname2"))
        it.setData(Qt.UserRole, QVariant(pname))

        table.setItem(ch,0,it)


        self.checkParam(dict(myParam,**{str(sel):"Myname2"}), 
                        self.form.ui.dParameterTableWidget, None)
        self.checkParam(dict(myParam,**{str(sel):"Myname2"}), 
                        self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(myParam,**{str(sel):"Myname2"}))
        
        table.setCurrentCell(ch,0)
        QTimer.singleShot(10, self.rmParamWidgetClose)
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)

        self.checkParam(dict(myParam,**{str(sel):"Myname2"}), 
                        self.form.ui.dParameterTableWidget, str(sel))        
        self.assertEqual(self.form.dbParam, dict(myParam,**{str(sel):"Myname2"}))

        QTimer.singleShot(10, self.rmParamWidget)
        it = table.item(table.currentRow(),0)
        
        QTest.mouseClick(self.form.ui.dRemovePushButton, Qt.LeftButton)
        
        rparam = dict(myParam)
        del rparam[sel]
        self.checkParam(rparam, self.form.ui.dParameterTableWidget, None)
        self.assertEqual(self.form.dbParam, dict(rparam))












if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
