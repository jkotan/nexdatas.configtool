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
# \file DataSourceMethodsTest.py
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
from PyQt5.QtWidgets import (QApplication, QMessageBox, QTableWidgetItem, QPushButton)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QObject
from PyQt5.QtXml import QDomNode, QDomDocument, QDomElement


from nxsconfigtool.DataSourceMethods import DataSourceMethods
from nxsconfigtool.DataSourceDlg import DataSourceDlg, CommonDataSourceDlg 
from nxsconfigtool.DataSource import DataSource, CommonDataSource
from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.AttributeDlg import AttributeDlg
from nxsconfigtool.NodeDlg import NodeDlg
from nxsconfigtool.DimensionsDlg import DimensionsDlg

# from nxsconfigtool.ui.ui_datasourcedlg import Ui_DataSourceDlg


#  Qt-application
app = None


# if 64-bit machione
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


class ClassVar(object):
    def __init__(self):
        self.tree = False
        self.dataSourceName =  ''
        self.dataSourceType = 'CLIENT'
        self.doc = ''
        self.clientRecordName =  ''
        self.tangoDeviceName =  ''
        self.tangoMemberName =  ''
        self.tangoMemberType = "attribute"
        self.tangoHost =  ''
        self.tangoPort =  ''
        self.tangoEncoding =  ''
        self.dbType = "MYSQL"
        self.dbDataFormat =  "SCALAR"
        self.dbQuery =  ''
        self.dbParameters =  {}        
        self.dbCurrentParam = 'DB name'
        self.externalSave = None
        self.externalStore = None
        self.externalClose = None
        self.externalApply = None
        self.applied = False
        self.ids = None

# test fixture
class DataSourceMethodsTest(unittest.TestCase):

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
 
        self.meth = None
        self.form = None 
        self.cds = None
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

    # Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception as e:
            error = True
        self.assertEqual(error, True)


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

    def checkMessageBox(self):
#        self.assertEqual(QApplication.activeWindow(),None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()


    def messageWidget(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.Yes), Qt.LeftButton)


    def messageWidgetClose(self):
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
    def ttest_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        dsd = DataSourceDlg()
        ds = dsd.datasource
        form = DataSourceMethods(dsd, ds)

        ds = DataSource()
        dsd = ds.dialog
        form = DataSourceMethods(dsd, ds)



    # constructor test
    # \brief It tests default settings
    def ttest_constructor_accept_setFocus(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceDlg()
        cls = form.datasource
        meth = DataSourceMethods(form, cls)

        meth.createGUI()
        
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeComboBox.currentText(), "CLIENT") 
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
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



    def check_cds(self, cds, params={}):

        cv = ClassVar()
        for key in params.keys():
            setattr(cv, key, params[key])


        self.assertEqual(cds.tree, cv.tree)
        self.assertEqual(cds.dataSourceName, cv.dataSourceName)


        self.assertEqual(cds.dataSourceType, cv.dataSourceType)
        self.assertEqual(cds.doc, cv.doc)

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.clientRecordName, cv.clientRecordName)
        self.assertEqual(cds.tangoDeviceName, cv.tangoDeviceName)
        self.assertEqual(cds.tangoMemberName, cv.tangoMemberName)
        self.assertEqual(cds.tangoMemberType, cv.tangoMemberType)
        self.assertEqual(cds.tangoHost, cv.tangoHost)
        self.assertEqual(cds.tangoPort, cv.tangoPort)
        self.assertEqual(cds.tangoEncoding, cv.tangoEncoding)

        self.assertEqual(cds.dbType, cv.dbType)
        self.assertEqual(cds.dbDataFormat, cv.dbDataFormat)
        self.assertEqual(cds.dbQuery, cv.dbQuery)
        self.assertEqual(cds.dbParameters, cv.dbParameters)

        self.assertEqual(cds.externalSave, cv.externalSave)
        self.assertEqual(cds.externalStore, cv.externalStore)
        self.assertEqual(cds.externalClose, cv.externalClose)
        self.assertEqual(cds.externalApply, cv.externalApply)

        self.assertEqual(cds.applied, cv.applied)

        self.assertEqual(cds.ids, cv.ids)



    def check_form(self, form, params={}):

        cv = ClassVar()
        for key in params.keys():
            setattr(cv, key, params[key])


        self.assertTrue(isinstance(form.ui, Ui_DataSourceDlg))
        self.assertEqual(form.ui.nameLineEdit.text(), cv.dataSourceName) 
        self.assertEqual(form.ui.docTextEdit.toPlainText(),cv.doc)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText(cv.dataSourceType))
        self.assertEqual(form.ui.cRecNameLineEdit.text(), cv.clientRecordName) 
        self.assertEqual(form.ui.tDevNameLineEdit.text(), cv.tangoDeviceName) 
        self.assertEqual(form.ui.tMemberNameLineEdit.text(), cv.tangoMemberName) 
        self.assertEqual(form.ui.tHostLineEdit.text(), cv.tangoHost) 
        self.assertEqual(form.ui.tPortLineEdit.text(), cv.tangoPort) 
        self.assertEqual(form.ui.tEncodingLineEdit.text(), cv.tangoEncoding) 
        self.assertEqual(form.ui.dTypeComboBox.currentIndex(), 
                         form.ui.dTypeComboBox.findText(cv.dbType))
        self.assertEqual(form.ui.dFormatComboBox.currentIndex(), 
                         form.ui.dFormatComboBox.findText(cv.dbDataFormat))
        self.assertEqual(form.ui.dQueryLineEdit.text(), cv.dbQuery) 
        self.assertEqual(form.ui.dParamComboBox.currentIndex(), 
                         form.ui.dParamComboBox.findText(cv.dbCurrentParam))

        self.assertEqual(form.ui.dParameterTableWidget.columnCount(),2)
        self.assertEqual(form.ui.dParameterTableWidget.rowCount(),len(cv.dbParameters))

        for i in range(len(cv.dbParameters)):
            it = form.ui.dParameterTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in cv.dbParameters.keys())
            it2 = form.ui.dParameterTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), cv.dbParameters[k])
            self.assertEqual(form.dbParam[k], cv.dbParameters[k])

        


    def check_updateForm(self, meth, form, cds, func = "updateForm", inst = None, tree = False): 
        ins = inst if inst else meth
        

        self.assertEqual(cds.dataSourceType, 'CLIENT')
        self.assertEqual(cds.doc, '')

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, u'')
        self.assertEqual(cds.clientRecordName, u'')
        self.assertEqual(cds.tangoDeviceName, u'')
        self.assertEqual(cds.tangoMemberName, u'')
        self.assertEqual(cds.tangoMemberType, u'')
        self.assertEqual(cds.tangoHost, u'')
        self.assertEqual(cds.tangoPort, u'')
        self.assertEqual(cds.tangoEncoding, u'')

        self.assertEqual(cds.dbType, 'MYSQL')
        self.assertEqual(cds.dbDataFormat, 'SCALAR')
        self.assertEqual(cds.dbQuery, "")
        self.assertEqual(cds.dbParameters, {})

        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, False)

        self.assertEqual(cds.ids, None)

        self.assertEqual(cds.tree, False)
        
        
        self.assertTrue(isinstance(form.ui, Ui_DataSourceDlg))

        meth.createGUI()
        meth.treeMode(tree)

        self.assertEqual(cds.tree, tree)


        self.assertEqual(cds.dataSourceType, 'CLIENT')
        self.assertEqual(cds.doc, '')

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, u'')
        self.assertEqual(cds.clientRecordName, u'')
        self.assertEqual(cds.tangoDeviceName, u'')
        self.assertEqual(cds.tangoMemberName, u'')
        self.assertEqual(cds.tangoMemberType, u'attribute')
        self.assertEqual(cds.tangoHost, u'')
        self.assertEqual(cds.tangoPort, u'')
        self.assertEqual(cds.tangoEncoding, u'')

        self.assertEqual(cds.dbType, 'MYSQL')
        self.assertEqual(cds.dbDataFormat, 'SCALAR')
        self.assertEqual(cds.dbQuery, "")
        self.assertEqual(cds.dbParameters, {})

        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, False)

        self.assertEqual(cds.ids, None)

        
        self.assertEqual(cds.tree, tree)
        
        self.check_form(form)




        n1 =  self.__rnd.randint(1, 9) 

        doc = "My document %s" % n1
        dataSourceType = self.__rnd.choice(["CLIENT","TANGO","DB"])
        dataSourceName =  "mydatasource%s" % n1
        clientRecordName =  "Myname%s" % n1
        tangoDeviceName =  "Mydevice %s" % n1
        tangoMemberName =  "Mymemeber %s" % n1
        tangoMemberType = self.__rnd.choice(["property","command","attribute"]) 
        tangoHost =  "haso.desy.de %s" % n1
        tangoPort =  "1000%s" % n1
        tangoEncoding =  "UTF%s" % n1
        dbType = self.__rnd.choice(["MYSQL","ORACLE","PGSQL"]) 
        dbDataFormat =  self.__rnd.choice(["SCALAR","SPECTRUM","IMAGE"]) 
        dbQuery =  "select name from device limit %s" % n1
        dbParameters =  {"DB name":"sdfsdf%s" % n1,
                         "DB host":"werwer%s" % n1, 
                         "DB port":"werwer%s" % n1, 
                         "DB user":"werwer%s" % n1, 
                         "DB password":"werwer%s" % n1, 
                         "Mysql cnf":"werwer%s" % n1, 
                         "Oracle mode":"werwer%s" % n1, 
                         "Oracle DSN":"asdasdf%s" % n1}        

        dbParameters2 =  {"DB name":"sdfsdf%s" % n1,
                         "DB user":"werwer%s" % n1, 
                         "DB password":"werwer%s" % n1, 
                         "Oracle DSN":"asdasdf%s" % n1}        


        dbCurrentParam = self.__rnd.choice(dbParameters.keys())
        
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)

        cds.doc = doc
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"doc":doc})
        form.ui.docTextEdit.setText("")
        cds.doc = ''

        cds.dataSourceType = dataSourceType
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(), None)
        self.check_form(form, {"dataSourceType":dataSourceType})
        index = form.ui.typeComboBox.findText('CLIENT')
        form.ui.typeComboBox.setCurrentIndex(index)
        cds.dataSourceType = 'CLIENT'

        cds.dataSourceName = dataSourceName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"dataSourceName":dataSourceName})
        form.ui.nameLineEdit.setText("")
        cds.dataSourceName = ''



        cds.clientRecordName = clientRecordName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"clientRecordName":clientRecordName})
        form.ui.cRecNameLineEdit.setText("")
        cds.clientRecordName = ''



        cds.tangoDeviceName = tangoDeviceName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"tangoDeviceName":tangoDeviceName})
        form.ui.tDevNameLineEdit.setText("")
        cds.tangoDeviceName = ''

        cds.tangoMemberName = tangoMemberName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"tangoMemberName":tangoMemberName})
        form.ui.tMemberNameLineEdit.setText("")
        cds.tangoMemberName = ''

        cds.tangoMemberType = tangoMemberType
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"tangoMemberType":tangoMemberType})
        index = form.ui.tMemberComboBox.findText('attribute')
        form.ui.tMemberComboBox.setCurrentIndex(index)
        cds.tangoMemberType = ''


        cds.tangoHost = tangoHost
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"tangoHost":tangoHost})
        form.ui.tHostLineEdit.setText("")
        cds.tangoHost = ''

        cds.tangoPort = tangoPort
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"tangoPort":tangoPort})
        form.ui.tPortLineEdit.setText("")
        cds.tangoPort = ''

        cds.tangoEncoding = tangoEncoding
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"tangoEncoding":tangoEncoding})
        form.ui.tEncodingLineEdit.setText("")
        cds.tangoEncoding = ''




        cds.dbType = dbType
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"dbType":dbType})
        index = form.ui.dTypeComboBox.findText('MYSQL')
        form.ui.dTypeComboBox.setCurrentIndex(index)
        cds.dbType = ''

        cds.dbDataFormat = dbDataFormat
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"dbDataFormat":dbDataFormat})
        index = form.ui.dFormatComboBox.findText('SCALAR')
        form.ui.dFormatComboBox.setCurrentIndex(index)
        cds.dbDataFormat = ''

        cds.dbQuery = dbQuery
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"dbQuery":dbQuery})
        form.ui.dQueryLineEdit.setText("")
        cds.dbQuery = ''
        
        cds.dbParameters = dict(dbParameters)
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"dbParameters":dbParameters})
        while form.ui.dParameterTableWidget.rowCount():
            form.ui.dParameterTableWidget.removeRow(0)
        form.ui.dParameterTableWidget.clear()
        cds.dbParameters = {}
        form.dbParam ={}


        cds.dbParameters = dict(dbParameters2)
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {"dbParameters":dbParameters2})
        while form.ui.dParameterTableWidget.rowCount():
            form.ui.dParameterTableWidget.removeRow(0)
        form.ui.dParameterTableWidget.clear()
        cds.dbParameters = {}
        form.dbParam ={}


        cds.doc = doc
        cds.dataSourceType = dataSourceType
        cds.dataSourceName = dataSourceName
        cds.clientRecordName = clientRecordName
        cds.tangoDeviceName = tangoDeviceName
        cds.tangoMemberName = tangoMemberName
        cds.tangoMemberType = tangoMemberType
        cds.tangoHost = tangoHost
        cds.tangoPort = tangoPort
        cds.tangoEncoding = tangoEncoding
        cds.dbType = dbType
        cds.dbDataFormat = dbDataFormat
        cds.dbQuery = dbQuery
        cds.dbParameters = dict(dbParameters)
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form, {
                "doc":doc,
                "dataSourceType":dataSourceType,
                "dataSourceName":dataSourceName,
                "clientRecordName":clientRecordName,
                "tangoDeviceName":tangoDeviceName,
                "tangoMemberName":tangoMemberName,
                "tangoMemberType":tangoMemberType,
                "tangoHost":tangoHost,
                "tangoPort":tangoPort,
                "tangoEncoding":tangoEncoding,
                "dbType":dbType,
                "dbDataFormat":dbDataFormat,
                "dbQuery":dbQuery,
                "dbParameters":dbParameters})




        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)

    



    def check_updateForm_no(self, meth, form, cds, func = "updateForm", inst = None, tree = False): 
        ins = inst if inst else meth
        

        self.assertEqual(cds.dataSourceType, 'CLIENT')
        self.assertEqual(cds.doc, '')

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, u'')
        self.assertEqual(cds.clientRecordName, u'')
        self.assertEqual(cds.tangoDeviceName, u'')
        self.assertEqual(cds.tangoMemberName, u'')
        self.assertEqual(cds.tangoMemberType, u'')
        self.assertEqual(cds.tangoHost, u'')
        self.assertEqual(cds.tangoPort, u'')
        self.assertEqual(cds.tangoEncoding, u'')

        self.assertEqual(cds.dbType, 'MYSQL')
        self.assertEqual(cds.dbDataFormat, 'SCALAR')
        self.assertEqual(cds.dbQuery, "")
        self.assertEqual(cds.dbParameters, {})

        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, False)

        self.assertEqual(cds.ids, None)

        self.assertEqual(cds.tree, False)
        
        
        self.assertTrue(isinstance(form.ui, Ui_DataSourceDlg))

        meth.createGUI()
        meth.treeMode(tree)
        self.assertEqual(cds.tree, tree)


        self.assertEqual(cds.dataSourceType, 'CLIENT')
        self.assertEqual(cds.doc, '')

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, u'')
        self.assertEqual(cds.clientRecordName, u'')
        self.assertEqual(cds.tangoDeviceName, u'')
        self.assertEqual(cds.tangoMemberName, u'')
        self.assertEqual(cds.tangoMemberType, u'attribute')
        self.assertEqual(cds.tangoHost, u'')
        self.assertEqual(cds.tangoPort, u'')
        self.assertEqual(cds.tangoEncoding, u'')

        self.assertEqual(cds.dbType, 'MYSQL')
        self.assertEqual(cds.dbDataFormat, 'SCALAR')
        self.assertEqual(cds.dbQuery, "")
        self.assertEqual(cds.dbParameters, {})

        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, False)

        self.assertEqual(cds.ids, None)

        
        self.assertEqual(cds.tree, tree)
        
        self.check_form(form)




        n1 =  self.__rnd.randint(1, 9) 

        doc = "My document %s" % n1
        dataSourceType = self.__rnd.choice(["CLIENT","TANGO","DB"])
        dataSourceName =  "mydatasource%s" % n1
        clientRecordName =  "Myname%s" % n1
        tangoDeviceName =  "Mydevice %s" % n1
        tangoMemberName =  "Mymemeber %s" % n1
        tangoMemberType = self.__rnd.choice(["property","command","attribute"]) 
        tangoHost =  "haso.desy.de %s" % n1
        tangoPort =  "1000%s" % n1
        tangoEncoding =  "UTF%s" % n1
        dbType = self.__rnd.choice(["MYSQL","ORACLE","PGSQL"]) 
        dbDataFormat =  self.__rnd.choice(["SCALAR","SPECTRUM","IMAGE"]) 
        dbQuery =  "select name from device limit %s" % n1
        dbParameters =  {"DB name":"sdfsdf%s" % n1,
                         "DB host":"werwer%s" % n1, 
                         "DB port":"werwer%s" % n1, 
                         "DB user":"werwer%s" % n1, 
                         "DB password":"werwer%s" % n1, 
                         "Mysql cnf":"werwer%s" % n1, 
                         "Oracle mode":"werwer%s" % n1, 
                         "Oracle DSN":"asdasdf%s" % n1}        

        dbParameters2 =  {"DB name":"sdfsdf%s" % n1,
                         "DB user":"werwer%s" % n1, 
                         "DB password":"werwer%s" % n1, 
                         "Oracle DSN":"asdasdf%s" % n1}        


        dbCurrentParam = self.__rnd.choice(dbParameters.keys())
        
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)

        cds.doc = doc
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.docTextEdit.setText("")
        cds.doc = ''

        cds.dataSourceType = dataSourceType
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(), None)
        self.check_form(form)
        index = form.ui.typeComboBox.findText('CLIENT')
        form.ui.typeComboBox.setCurrentIndex(index)
        cds.dataSourceType = 'CLIENT'

        cds.dataSourceName = dataSourceName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.nameLineEdit.setText("")
        cds.dataSourceName = ''



        cds.clientRecordName = clientRecordName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.cRecNameLineEdit.setText("")
        cds.clientRecordName = ''



        cds.tangoDeviceName = tangoDeviceName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.tDevNameLineEdit.setText("")
        cds.tangoDeviceName = ''

        cds.tangoMemberName = tangoMemberName
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.tMemberNameLineEdit.setText("")
        cds.tangoMemberName = ''

        cds.tangoMemberType = tangoMemberType
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        index = form.ui.tMemberComboBox.findText('attribute')
        form.ui.tMemberComboBox.setCurrentIndex(index)
        cds.tangoMemberType = ''


        cds.tangoHost = tangoHost
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.tHostLineEdit.setText("")
        cds.tangoHost = ''

        cds.tangoPort = tangoPort
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.tPortLineEdit.setText("")
        cds.tangoPort = ''

        cds.tangoEncoding = tangoEncoding
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        form.ui.tEncodingLineEdit.setText("")
        cds.tangoEncoding = ''




        cds.dbType = dbType
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        index = form.ui.dTypeComboBox.findText('MYSQL')
        form.ui.dTypeComboBox.setCurrentIndex(index)
        cds.dbType = ''

        cds.dbDataFormat = dbDataFormat
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        index = form.ui.dFormatComboBox.findText('SCALAR')
        form.ui.dFormatComboBox.setCurrentIndex(index)
        cds.dbDataFormat = ''

        cds.dbQuery = dbQuery
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        form.ui.dQueryLineEdit.setText("")
        cds.dbQuery = ''
        
        cds.dbParameters = dict(dbParameters)
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        while form.ui.dParameterTableWidget.rowCount():
            form.ui.dParameterTableWidget.removeRow(0)
        form.ui.dParameterTableWidget.clear()
        cds.dbParameters = {}
        form.dbParam ={}


        cds.dbParameters = dict(dbParameters2)
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)
        while form.ui.dParameterTableWidget.rowCount():
            form.ui.dParameterTableWidget.removeRow(0)
        form.ui.dParameterTableWidget.clear()
        cds.dbParameters = {}
        form.dbParam ={}


        cds.doc = doc
        cds.dataSourceType = dataSourceType
        cds.dataSourceName = dataSourceName
        cds.clientRecordName = clientRecordName
        cds.tangoDeviceName = tangoDeviceName
        cds.tangoMemberName = tangoMemberName
        cds.tangoMemberType = tangoMemberType
        cds.tangoHost = tangoHost
        cds.tangoPort = tangoPort
        cds.tangoEncoding = tangoEncoding
        cds.dbType = dbType
        cds.dbDataFormat = dbDataFormat
        cds.dbQuery = dbQuery
        cds.dbParameters = dict(dbParameters)
        self.check_form(form)
        self.assertEqual(getattr(ins, func)(),None)
        self.check_form(form)


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)

    


    # constructor test
    # \brief It tests default settings
    def ttest_updateForm_errors(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        meth = DataSourceMethods(None, None)
        self.myAssertRaise(Exception, meth.updateForm)


        form = CommonDataSourceDlg(None)
        cds = None
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.updateForm)

        form = None
        cds = CommonDataSource()
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.updateForm)

        form = DataSourceDlg()
        cds = form.datasource



    # constructor test
    # \brief It tests default settings
    def ttest_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds)


        cds = DataSource()
        form = cds.dialog
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds)
    


    # constructor test
    # \brief It tests default settings
    def ttest_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds, "reset")


        cds = DataSource()
        form = cds.dialog
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds, "reset")
    


    def message_and_close(self):
        QTimer.singleShot(10, self.messageWidget)
        self.meth.close()


    def messageno_and_close(self):
        QTimer.singleShot(10, self.messageWidgetClose)
        self.meth.close()

    # constructor test
    # \brief It tests default settings
    def ttest_close_yes(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm(self.meth, form, cds, "message_and_close", self)


        cds = DataSource()
        form = cds.dialog
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm(self.meth, form, cds, "message_and_close", self)



    # constructor test
    # \brief It tests default settings
    def ttest_close_yes_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm(self.meth, form, cds, "message_and_close", self, True)


        cds = DataSource()
        form = cds.dialog
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm(self.meth, form, cds, "message_and_close", self, True)


    
    def message_and_reset(self):
        QTest.mouseClick(self.form.ui.resetPushButton, Qt.LeftButton)
        


    # constructor test
    # \brief It tests default settings
    def ttest_reset_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.cds = DataSource()
        self.form = self.cds.dialog
        self.meth = DataSourceMethods(self.form, self.cds)
        self.check_updateForm(self.meth, self.form, self.cds, "message_and_reset", self)
    

        form = DataSourceDlg()
        self.cds = form.datasource
        self.meth = DataSourceMethods(self.form, self.cds)
        self.check_updateForm(self.meth, self.form, self.cds, "message_and_reset", self)


    # constructor test
    # \brief It tests default settings
    def ttest_reset_signal_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.cds = DataSource()
        self.form = self.cds.dialog
        self.meth = DataSourceMethods(self.form, self.cds)
        self.check_updateForm(self.meth, self.form, self.cds, "message_and_reset", self,True)
    

        form = DataSourceDlg()
        self.cds = form.datasource
        self.meth = DataSourceMethods(self.form, self.cds)
        self.check_updateForm(self.meth, self.form, self.cds, "message_and_reset", self, True)




    # constructor test
    # \brief It tests default settings
    def ttest_close_no(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm_no(self.meth, form, cds, "messageno_and_close", self)


        cds = DataSource()
        form = cds.dialog
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm_no(self.meth, form, cds, "messageno_and_close", self)


    # constructor test
    # \brief It tests default settings
    def ttest_close_no_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm_no(self.meth, form, cds, "messageno_and_close", self, True)


        cds = DataSource()
        form = cds.dialog
        self.meth = DataSourceMethods(form, cds)
        self.check_updateForm_no(self.meth, form, cds, "messageno_and_close", self, True)
    


    # constructor test
    # \brief It tests default settings
    def ttest_treeMode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        meth = DataSourceMethods(None, None)
        self.myAssertRaise(Exception, meth.treeMode)


        form = CommonDataSourceDlg(None)
        cds = None
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.treeMode)

        form = None
        cds = CommonDataSource()
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.treeMode)

        form = DataSourceDlg()
        cds = form.datasource
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.treeMode)

        form = DataSourceDlg()
        cds = form.datasource
        meth = DataSourceMethods(form, cds)
        meth.createGUI()
        form.show()
        self.assertEqual(cds.tree, False)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), True)
        meth.treeMode()
        self.assertEqual(cds.tree, True)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), False)
        meth.treeMode(False)
        self.assertEqual(cds.tree, False)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), True)
        meth.treeMode(True)
        self.assertEqual(cds.tree, True)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), False)


        cds = DataSource()
        form = cds.dialog
        meth = DataSourceMethods(form, cds)
        meth.createGUI()
        form.show()
        self.assertEqual(cds.tree, False)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), True)
        meth.treeMode()
        self.assertEqual(cds.tree, True)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), False)
        meth.treeMode(False)
        self.assertEqual(cds.tree, False)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), True)
        meth.treeMode(True)
        self.assertEqual(cds.tree, True)
        self.assertEqual(form.ui.closeSaveFrame.isVisible(), False)




        


    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_updataForm_errors(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        meth = DataSourceMethods(None, None)
        self.myAssertRaise(Exception, meth.updateForm)


        form = CommonDataSourceDlg(None)
        cds = None
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.createGUI)

        form = None
        cds = CommonDataSource()
        meth = DataSourceMethods(form, cds)
        self.myAssertRaise(Exception, meth.createGUI)



    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds, "createGUI")


        cds = DataSource()
        form = cds.dialog
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds, "createGUI")


    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_updateForm_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds, "createGUI", None, True)


        cds = DataSource()
        form = cds.dialog
        meth = DataSourceMethods(form, cds)
        self.check_updateForm(meth, form, cds, "createGUI", None, True)



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




    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_setFrames(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_setFrames(cds)


        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_setFrames(cds)



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
 

    # constructor test
    # \brief It tests default settings
    def check_createGUI_setFrames(self, cds):
        parent = None
        


        cds.dataSourceType = ""
        self.meth.createGUI()
        self.form.show()
        self.disableButtons()
        self.clientVisible()


        cds.dataSourceType = "CLIENT"
        self.meth.createGUI()
        self.form.show()
        self.clientVisible()
        self.disableButtons()
        
        cds.clientRecordName =""
        cds.dataSourceType = "CLIENT"
        self.meth.createGUI()
        self.form.show()
        self.clientVisible()
        self.disableButtons()

        cds.clientRecordName ="name"
        cds.dataSourceType = "CLIENT"
        self.meth.createGUI()
        self.form.show()
        self.clientVisible()
        self.enableButtons()






        cds.dbQuery =""
        cds.dataSourceType = "DB"
        self.meth.createGUI()
        self.form.show()
        self.dbVisible()
        self.disableButtons()


        cds.dbQuery ="name"
        cds.dataSourceType = "DB"
        self.meth.createGUI()
        self.form.show()
        self.dbVisible()
        self.enableButtons()



        myParam = {"DB name":"sdfsdf",
                   "DB host":"werwer", 
                   "DB port":"werwer", 
                   "DB user":"werwer", 
                   "DB password":"werwer", 
                   "Mysql cnf":"werwer", 
                   "Oracle mode":"werwer", 
                   "Oracle DSN":"asdasdf"}        

 


        cds.dbQuery ="name"
        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        cds.dbParameters = dict(myParam)
        
        cds.dataSourceType = "DB"
        self.meth.createGUI()
        self.form.show()
        self.assertEqual(self.form.dbParam,myParam)
        self.assertEqual(cds.dbParameters,myParam)
        self.dbVisible()
        self.enableButtons()
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, None)



        cds.dataSourceType = "TANGO"
        cds.tangoDeviceName = ""
        self.meth.createGUI()
        self.form.show()
        self.tangoVisible()
        self.disableButtons()


        cds.tangoDeviceName = "name"
        cds.dataSourceType = "TANGO"
        self.meth.createGUI()
        self.form.show()
        self.tangoVisible()
        self.disableButtons()

        cds.tangoMemberName = "name2"
        cds.dataSourceType = "TANGO"
        self.meth.createGUI()
        self.form.show()
        self.tangoVisible()
        self.enableButtons()

        cds.tangoDeviceName = ""
        cds.dataSourceType = "TANGO"
        self.meth.createGUI()
        self.form.show()
        self.tangoVisible()
        self.disableButtons()
        




    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_setFrames_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_setFrames_signal(cds)


        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_setFrames_signal(cds)



    # constructor test
    # \brief It tests default settings
    def check_createGUI_setFrames_signal(self, cds):

        self.meth.createGUI()
        
        self.form.show()
        

        self.disableButtons()
        self.clientVisible()

 
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("CLIENT"))

        self.disableButtons()
        self.clientVisible()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("DB"))

        self.disableButtons()
        self.dbVisible()

        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText("TANGO"))


        self.disableButtons()
        self.tangoVisible()

        self.form.connectWidgets()
        self.form.ui.typeComboBox.setCurrentIndex(self.form.ui.typeComboBox.findText(""))


        self.enableButtons()
        self.tangoVisible()


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


        myParam = {"DB name":"sdfsdf",
                   "DB host":"werwer", 
                   "DB port":"werwer", 
                   "DB user":"werwer", 
                   "DB password":"werwer", 
                   "Mysql cnf":"werwer", 
                   "Oracle mode":"werwer", 
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
        
        

    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_cRecNameLineEdit_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_cRecNameLineEdit_signal(cds)


        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_cRecNameLineEdit_signal(cds)


        



    # constructor test
    # \brief It tests default settings
    def check_createGUI_cRecNameLineEdit_signal(self, cds):

        self.meth.createGUI()
        self.form.show()


        self.disableButtons()
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




    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_dQueryLineEdit_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_dQueryLineEdit_signal(cds)


        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_dQueryLineEdit_signal(cds)


        


    # constructor test
    # \brief It tests default settings
    def check_createGUI_dQueryLineEdit_signal(self, cds):



        self.meth.createGUI()
        self.form.show()

        self.disableButtons()
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


    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_tDevNameLineEdit_tMemberNameLineEdit_signal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_tDevNameLineEdit_tMemberNameLineEdit_signal(cds)


        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_tDevNameLineEdit_tMemberNameLineEdit_signal(cds)


        



    # constructor test
    # \brief It tests default settings
    def check_createGUI_tDevNameLineEdit_tMemberNameLineEdit_signal(self, cds):
        self.meth.createGUI()
        self.form.show()

        self.disableButtons()
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

        
    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_populateParameters(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters(cds)


        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters(cds)


        




    # constructor test
    # \brief It tests default settings
    def check_createGUI_populateParameters(self ,cds):
        self.meth.createGUI()
        self.form.show()

        self.disableButtons()
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
                   "Oracle mode":"wwer", 
                   "Oracle DSN":"asdasdf"}        

        na =  self.__rnd.randint(0, len(myParam)-1) 
        sel = myParam.keys()[na]
        self.form.dbParam = myParam
        self.form.populateParameters(sel)
        self.checkParam(myParam, self.form.ui.dParameterTableWidget, sel)






    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_populateParameters_addremoveParamter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters_addremoveParamter(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters_addremoveParamter(cds)



    # constructor test
    # \brief It tests default settings
    def check_createGUI_populateParameters_addremoveParamter(self, cds):
        self.meth.createGUI()
        self.form.show()

        self.disableButtons()
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
            "Oracle mode":"wwer", 
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
        it.setData(Qt.DisplayRole, ("Myname2"))
        it.setData(Qt.UserRole, (pname))


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


    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_populateParameters_changeParamter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters_changeParamter(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters_changeParamter(cds)





    # constructor test
    # \brief It tests default settings
    def check_createGUI_populateParameters_changeParamter(self,cds):
        self.meth.createGUI()
        self.form.show()

        self.disableButtons()
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
            "Oracle mode":"wwer", 
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


    # constructor test
    # \brief It tests default settings
    def ttest_createGUI_populateParameters_changeParamter_value(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters_changeParamter_value(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_createGUI_populateParameters_changeParamter_value(cds)




    # constructor test
    # \brief It tests default settings
    def check_createGUI_populateParameters_changeParamter_value(self,cds):
        self.meth.createGUI()
        self.form.show()

        self.disableButtons()
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
            "Oracle mode":"wwer", 
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
        it.setData(Qt.DisplayRole, ("Myname2"))
        it.setData(Qt.UserRole, (pname))

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


        QTest.mouseClick(self.form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(self.form.result(),0)



    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_client(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds)

    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_client_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds, True)




    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_client_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds,False,True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds,False,True)

    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_client_tree_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds, True, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_client(cds, True, True)



    # constructor test
    # \brief It tests default settings
    def check_setFromNode_client(self, cds, tree = False, node = None):



        n1 =  self.__rnd.randint(1, 9) 

        doc = "My document %s" % n1
        dataSourceType = "CLIENT"
        dataSourceName =  "mydatasource%s" % n1
        clientRecordName =  "Myname%s" % n1

        dks = []
        doc = QDomDocument()
        nname = "datasource"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name",dataSourceName)
        qdn.setAttribute("type",dataSourceType)


        rec = doc.createElement("record")
        rec.setAttribute("name",clientRecordName)
        qdn.appendChild(rec) 

        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 
        doc.appendChild(qdn) 

        if not node:    
            self.form.node = qdn

        self.meth.createGUI()
        self.meth.treeMode(tree)
        self.form.show()
        self.check_form(self.form)
        self.check_cds(cds,{"tree":tree})
        
        
        if node:
            self.meth.setFromNode(qdn)
        else:     
            self.meth.setFromNode()

        self.check_cds(cds,{"doc":"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip(),
                            "dataSourceType":dataSourceType,
                            "dataSourceName":dataSourceName,
                            "clientRecordName":clientRecordName,
                            "tree":tree})
        self.check_form(self.form)




    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_tango(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds)

    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_tango_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds, True)




    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_tango_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds,False,True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds,False,True)

    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_tango_tree_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds, True, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_tango(cds, True, True)




    # constructor test
    # \brief It tests default settings
    def check_setFromNode_tango(self, cds, tree = False, node = None):



        n1 =  self.__rnd.randint(1, 9) 

        doc = "My document %s" % n1
        dataSourceType = "TANGO"
        dataSourceName =  "mydatasource%s" % n1


        tangoDeviceName =  'my/device/%s' % n1
        tangoMemberName =  'position%s' % n1
        tangoMemberType = self.__rnd.choice(["attribute","command","property"])
        tangoHost =  'haso%s.desy.de' % n1
        tangoPort =  '100%s' % n1
        tangoEncoding =  'UTF%s' % n1



        dks = []
        doc = QDomDocument()
        nname = "datasource"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name",dataSourceName)
        qdn.setAttribute("type",dataSourceType)


        rec = doc.createElement("record")
        rec.setAttribute("name",tangoMemberName)
        qdn.appendChild(rec) 


        dev = doc.createElement("device")
        dev.setAttribute("hostname", tangoHost)
        dev.setAttribute("port", tangoPort)
        dev.setAttribute("member", tangoMemberType)
        dev.setAttribute("name", tangoDeviceName)
        dev.setAttribute("encoding", tangoEncoding)
        qdn.appendChild(dev) 

        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 
        doc.appendChild(qdn) 

        if not node:    
            self.form.node = qdn

        self.meth.createGUI()
        self.meth.treeMode(tree)
        self.form.show()
        self.check_form(self.form)
        self.check_cds(cds,{"tree":tree})
        
        
        if node:
            self.meth.setFromNode(qdn)
        else:     
            self.meth.setFromNode()

        self.check_cds(cds,{"doc":"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip(),
                            "dataSourceType":dataSourceType,
                            "dataSourceName":dataSourceName,
                            "tangoDeviceName":tangoDeviceName,
                            "tangoMemberName":tangoMemberName,
                            "tangoMemberType":tangoMemberType,
                            "tangoHost":tangoHost,
                            "tangoPort":tangoPort,
                            "tangoEncoding":tangoEncoding,
                            "tree":tree})
        self.check_form(self.form)






    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_db(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds)


    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_db_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds, True)




    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_db_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds,False,True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds,False,True)


    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_db_tree_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds, True, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_db(cds, True, True)



    # constructor test
    # \brief It tests default settings
    def check_setFromNode_db(self, cds, tree = False, node = None):


        n1 =  self.__rnd.randint(1, 9) 

        doc = "My document %s" % n1
        dataSourceType = "DB"
        dataSourceName =  "mydatasource%s" % n1

        dbType = self.__rnd.choice(["MYSQL","ORACLE","PGSQL"]) 
        dbDataFormat =  self.__rnd.choice(["SCALAR","SPECTRUM","IMAGE"]) 
        dbQuery =  "select name from device limit %s" % n1
        dbParameters =  {"DB name":"tango%s" % n1,
                         "DB host":"haso%s.desy.de" % n1, 
                         "DB port":"100000%s" % n1, 
                         "DB user":"smith%s" % n1, 
                         "DB password":"FJFJDv%s" % n1, 
                         "Mysql cnf":"/etc/my%s.cnf" % n1, 
                         "Oracle mode":"m%s" % n1, 
                         "Oracle DSN":"(some dns%s)" % n1}        
        dbmap = {"dbname":"DB name",
                 "hostname":"DB host",
                 "port":"DB port",
                 "user":"DB user",
                 "passwd":"DB password",
                 "mycnf":"Mysql cnf",
                 "mode":"Oracle mode"
                 } 




        dks = []
        doc = QDomDocument()
        nname = "datasource"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name",dataSourceName)
        qdn.setAttribute("type",dataSourceType)
            




        db = doc.createElement("database")
        db.setAttribute("dbtype",dbType)
        for dm in dbmap.keys():
            db.setAttribute(dm,dbParameters[dbmap[dm]])
        db.appendChild(doc.createTextNode(dbParameters["Oracle DSN"]))
        qdn.appendChild(db) 

        
        qr = doc.createElement("query")
        qr.setAttribute("format", dbDataFormat)
        qr.appendChild(doc.createTextNode(dbQuery))

        qdn.appendChild(qr) 

        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

            

        doc.appendChild(qdn) 

        if not node:    
            self.form.node = qdn

        self.meth.createGUI()
        self.meth.treeMode(tree)
        self.form.show()
        self.check_form(self.form)
        self.check_cds(cds,{"tree":tree})
        
        
        if node:
            self.meth.setFromNode(qdn)
        else:     
            self.meth.setFromNode()
            
        self.check_cds(cds,{"doc":"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip(),
                            "dataSourceType":dataSourceType,
                            "dataSourceName":dataSourceName,
                            "dbType":dbType,
                            "dbDataFormat":dbDataFormat,
                            "dbQuery":dbQuery,
                            "dbParameters":dbParameters,
                            "tree":tree})
        self.check_form(self.form)
        self.form.populateParameters()


        self.check_cds(cds,{"doc":"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip(),
                            "dataSourceType":dataSourceType,
                            "dataSourceName":dataSourceName,
                            "dbType":dbType,
                            "dbDataFormat":dbDataFormat,
                            "dbQuery":dbQuery,
                            "dbParameters":dbParameters,
                            "tree":tree})
        self.check_form(self.form,{"dbParameters":dbParameters})
        item = self.form.ui.dParameterTableWidget.item(
            self.form.ui.dParameterTableWidget.currentRow(), 0)
        self.assertEqual(item,None)


        sel  = self.__rnd.choice(dbParameters.keys())
        self.form.populateParameters(sel)


        self.check_cds(cds,{"doc":"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip(),
                            "dataSourceType":dataSourceType,
                            "dataSourceName":dataSourceName,
                            "dbType":dbType,
                            "dbDataFormat":dbDataFormat,
                            "dbQuery":dbQuery,
                            "dbParameters":dbParameters,
                            "tree":tree})
        self.check_form(self.form,{"dbParameters":dbParameters})
        item = self.form.ui.dParameterTableWidget.item(
            self.form.ui.dParameterTableWidget.currentRow(), 0)
        self.assertEqual(item.data(Qt.UserRole).toString(),sel)

        self.form.populateParameters("bleble")


        self.check_cds(cds,{"doc":"".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip(),
                            "dataSourceType":dataSourceType,
                            "dataSourceName":dataSourceName,
                            "dbType":dbType,
                            "dbDataFormat":dbDataFormat,
                            "dbQuery":dbQuery,
                            "dbParameters":dbParameters,
                            "tree":tree})
        self.check_form(self.form,{"dbParameters":dbParameters})
        item = self.form.ui.dParameterTableWidget.item(
            self.form.ui.dParameterTableWidget.currentRow(), 0)
        self.assertEqual(item, None)

    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_nonode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds)


    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_nonode_tree(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds, True)




    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_nonode_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds,False,True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds,False,True)


    # constructor test
    # \brief It tests default settings
    def ttest_setFromNode_nonode_tree_node(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        self.form = DataSourceDlg()
        cds = self.form.datasource
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds, True, True)

        cds = DataSource()
        self.form = cds.dialog
        self.meth = DataSourceMethods(self.form, cds)
        self.check_setFromNode_nonode(cds, True, True)



    # constructor test
    # \brief It tests default settings
    def check_setFromNode_nonode(self, cds, tree = False, node = None):


        n1 =  self.__rnd.randint(1, 9) 

        doc = "My document %s" % n1
        dataSourceType = "DB"
        dataSourceName =  "mydatasource%s" % n1

        dbType = self.__rnd.choice(["MYSQL","ORACLE","PGSQL"]) 
        dbDataFormat =  self.__rnd.choice(["SCALAR","SPECTRUM","IMAGE"]) 
        dbQuery =  "select name from device limit %s" % n1
        dbParameters =  {"DB name":"tango%s" % n1,
                         "DB host":"haso%s.desy.de" % n1, 
                         "DB port":"100000%s" % n1, 
                         "DB user":"smith%s" % n1, 
                         "DB password":"FJFJDv%s" % n1, 
                         "Mysql cnf":"/etc/my%s.cnf" % n1, 
                         "Oracle mode":"m%s" % n1, 
                         "Oracle DSN":"(some dns%s)" % n1}        
        dbmap = {"dbname":"DB name",
                 "hostname":"DB host",
                 "port":"DB port",
                 "user":"DB user",
                 "passwd":"DB password",
                 "mycnf":"Mysql cnf",
                 "mode":"Oracle mode"
                 } 




        dks = []
        doc = QDomDocument()
        nname = "datasource"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name",dataSourceName)
        qdn.setAttribute("type",dataSourceType)
            




        db = doc.createElement("database")
        db.setAttribute("dbtype",dbType)
        for dm in dbmap.keys():
            db.setAttribute(dm,dbParameters[dbmap[dm]])
        db.appendChild(doc.createTextNode(dbParameters["Oracle DSN"]))
        qdn.appendChild(db) 

        
        qr = doc.createElement("query")
        qr.setAttribute("format", dbDataFormat)
        qr.appendChild(doc.createTextNode(dbQuery))

        qdn.appendChild(qr) 

        dname = "doc"

        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc) 
        ndcs =  self.__rnd.randint(0, 10) 
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" %  n))
            mdoc.appendChild(dks[-1]) 

            

        doc.appendChild(qdn) 


        self.meth.createGUI()
        self.meth.treeMode(tree)
        self.form.show()
        self.check_form(self.form)
        self.check_cds(cds,{"tree":tree})
        
        
        self.meth.setFromNode()
            
        self.check_form(self.form)
        self.check_cds(cds,{"tree":tree})



#TODO setFromNode nonode/populateparameters





    # constructor test
    # \brief It tests default settings
    def ttttest_updateNode(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

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
            elif nm == "units":
                self.assertEqual(vl,form.units)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.units = units
        form.value = "My new value ble ble"

        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]

        mrnk = self.__rnd.randint(0,5)     
        mdimensions = [self.__rnd.randint(1, 40)  for n in range(mrnk)]
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
            elif nm == "units":
                self.assertEqual(vl,units)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(mdimensions[ind-1], vl)
            child = child.nextSibling()    

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)






    # constructor test
    # \brief It tests default settings
    def ttttest_updateNode_withindex(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

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
            elif nm == "units":
                self.assertEqual(vl,form.units)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.units = units
        form.value = "My new value ble ble"

        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]

        mrnk = self.__rnd.randint(0,5)     
        mdimensions = [self.__rnd.randint(1, 40)  for n in range(mrnk)]
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
            elif nm == "units":
                self.assertEqual(vl,units)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(mdimensions[ind-1], vl)
            child = child.nextSibling()    

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    # constructor test
    # \brief It tests default settings
    def ttttest_apply(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

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
            elif nm == "units":
                self.assertEqual(vl,form.units)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.units = units
        form.value = mvalue

        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]
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
        form.ui.unitsLineEdit.setText(units)
        form.ui.valueLineEdit.setText(mvalue)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0,1)
            item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0) 


            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)




        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i,1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        mrnk = self.__rnd.randint(0,5)     
        self.dimensions = [self.__rnd.randint(1, 40)  for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        form.apply()


        self.assertEqual(form.name, nname)
        self.assertEqual(form.nexusType, ntype)
        self.assertEqual(form.units, units)
        self.assertEqual(form.value, mvalue)
        self.assertEqual(form.doc, mdoc)
        self.assertEqual(form.attributes, attrs)
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
            elif nm == "units":
                self.assertEqual(vl,units)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,mdoc)
        
        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,mvalue)

        mydm = form.node.firstChildElement(str("dimensions"))           

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
                self.assertEqual(self.dimensions[ind-1], vl)
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
            elif nm == "units":
                self.assertEqual(vl,units)
                cnt += 1 
            else:
                self.assertEqual(vl,attrs[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    # constructor test
    # \brief It tests default settings
    def ttttest_reset(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

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
            elif nm == "units":
                self.assertEqual(vl,form.units)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.units = units
        form.value = mvalue

        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]
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
        form.ui.unitsLineEdit.setText(units)
        form.ui.valueLineEdit.setText(mvalue)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0,1)
            item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0) 


            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)




        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i,1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        mrnk = self.__rnd.randint(0,5)     
        self.dimensions = [self.__rnd.randint(1, 40)  for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        form.reset()
        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.units, "myunits%s" % nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

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
            elif nm == "units":
                self.assertEqual(vl, "myunits%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    





    # constructor test
    # \brief It tests default settings
    def ttttest_reset_button(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

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
            elif nm == "units":
                self.assertEqual(vl,form.units)
                cnt += 1 
            else:
                self.assertEqual(vl,form.attributes[str(nm)])
        self.assertEqual(len(form.attributes),attributeMap.count() - cnt)

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,form.doc)



        form.name = nname
        form.nexusType = ntype
        form.units = units
        form.value = mvalue

        form.attributes.clear()
        for at in attrs.keys() :
            form.attributes[at] =  attrs[at]
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
        form.ui.unitsLineEdit.setText(units)
        form.ui.valueLineEdit.setText(mvalue)
        form.ui.docTextEdit.setText(str(mdoc))
        
        
        
        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0,1)
            item = form.ui.attributeTableWidget.item(form.ui.attributeTableWidget.currentRow(), 0) 


            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)




        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i,1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        mrnk = self.__rnd.randint(0,5)     
        self.dimensions = [self.__rnd.randint(1, 40)  for n in range(mrnk)]

        QTimer.singleShot(10, self.dimensionsWidget)
        QTest.mouseClick(form.ui.dimPushButton, Qt.LeftButton)

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)
        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.units, "myunits%s" % nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

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
            elif nm == "units":
                self.assertEqual(vl, "myunits%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    











    def myAction(self):
        self.performed = True


    # constructor test


    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(form.dts, DomTools))

        self.assertEqual(form.result(),0)

    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, None)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)


        self.assertEqual(form.result(),0)



    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)






    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_link_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.createGUI()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(None,self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False



        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def tttttest_connect_actions_with_action_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)





    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_and_sapply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)


    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_and_slink_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.nameLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(None,self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply,None)
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.linkDSPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)





    # constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_link_and_apply_button_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.ui = Ui_DataSourceMethods() 
        form.ui.applyPushButton = QPushButton(form)
        form.createGUI()
        QTest.keyClicks(form.ui.typeLineEdit, "namename")

        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,None),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertTrue(isinstance(form.ui,Ui_DataSourceMethods))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, False)


        self.assertEqual(form.result(),0)






    # constructor test
    # \brief It tests default settings
    def ttttest_appendElement(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.setFromNode()
        form.createGUI()

        attributeMap = form.node.attributes()
        attrs = {"longname":"newlogname","unit":"myunits%s" %  nn}

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.units, "myunits%s" % nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

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
            elif nm == "units":
                self.assertEqual(vl, "myunits%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    





        doc2 = QDomDocument()
        nname2 = "datasource"
        qdn2 = doc2.createElement(nname2)
        qdn2.setAttribute("name","my2name%s" %  nn)
        qdn2.setAttribute("type","my2type%s" %  nn)
        qdn2.setAttribute("unit2","my2units%s" %  nn)
        qdn2.setAttribute("units","my2units%s" %  nn)
        qdn2.setAttribute("shortname2","my2nshort%s" %  nn)
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
            elif nm == "units":
                self.assertEqual(vl, "myunits%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    


        ats2= {u'shortname2': u'my2nshort%s' % nn, u'unit2': u'my2units%s' % nn}

        ds = form.node.firstChildElement(str("datasource"))           
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
            elif nm == "units":
                self.assertEqual(vl, "my2units%s" % nn)
                cnt += 1 
            else:
                print ats2, nm
                self.assertEqual(vl,ats2[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)







    # constructor test
    # \brief It tests default settings
    def ttttest_appendElement_error(self):
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 


        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.setFromNode()
        form.createGUI()

        attributeMap = form.node.attributes()
        attrs = {"longname":"newlogname","unit":"myunits%s" %  nn}

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        ats= {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.units, "myunits%s" % nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

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
            elif nm == "units":
                self.assertEqual(vl, "myunits%s" % nn)
                cnt += 1 
            else:
                self.assertEqual(vl,ats[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)


        mydoc = form.node.firstChildElement(str("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval, "".join(["\nVAL\n %s\n" %  n for n in range(nval)]).strip())

        mydm = form.node.firstChildElement(str("dimensions"))           
         
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    


        tags = ["datasource","strategy"]
        wtext = "To add a new %s please remove the old one"
        for tg in tags:



            doc2 = QDomDocument()
            nname2 = tg
            qdn2 = doc2.createElement(nname2)
            qdn2.setAttribute("name","my2name%s" %  nn)
            qdn2.setAttribute("type","my2type%s" %  nn)
            qdn2.setAttribute("unit2","my2units%s" %  nn)
            qdn2.setAttribute("units","my2units%s" %  nn)
            qdn2.setAttribute("shortname2","my2nshort%s" %  nn)
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
            qdn2.setAttribute("unit2","my2units%s" %  nn)
            qdn2.setAttribute("units","my2units%s" %  nn)
            qdn2.setAttribute("shortname2","my2nshort%s" %  nn)
            doc2.appendChild(qdn2) 

            form.appendElement(qdn2,di)

            form.appendElement(qdn2,di)
        




    # constructor test
    # \brief It tests default settings
    def ttttest_populateAttribute_setFromNode_selected_addAttribute(self):
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
        qdn.setAttribute("units","mmyunits%s" %  nn)
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
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.units, 'mmyunits%s'%nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}


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








    # constructor test
    # \brief It tests default settings
    def ttttest_populateAttribute_setFromNode_selected_tableItemChanged(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        nn =  self.__rnd.randint(0, 9) 
        qdn.setAttribute("name","myname%s" %  nn)
        qdn.setAttribute("type","mytype%s" %  nn)
        qdn.setAttribute("units","mmyunits%s" %  nn)
        qdn.setAttribute("unit","myunits%s" %  nn)
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

        dimensions = [self.__rnd.randint(1, 40)  for n in range(rn)]

        mdim = doc.createElement('dimensions')
        mdim.setAttribute("rank", str(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(str("dim"))
            dim.setAttribute(str("index"), str(unicode(i+1)))
            dim.setAttribute(str("value"), str(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        atw = form.ui.attributeTableWidget        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.units, 'mmyunits%s'%nn)
        self.assertEqual(form.doc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

        self.assertEqual(form.dimensions, dimensions)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)

        attributes = {u'shortname': u'mynshort%s' % nn, u'unit': u'myunits%s' % nn}



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
        it.setData(Qt.DisplayRole, (aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, (aname))

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
        it.setData(Qt.DisplayRole, (aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, (aname))

        atw.setCurrentCell(ch,1)

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
                self.assertEqual(it2.text(), (aname+"_"+attributes[aname]))






if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
