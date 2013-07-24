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
## \file DataSourceMethodsTest.py
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


from ndtsconfigtool.DataSourceDlg import (DataSourceMethods, DataSource, 
                                          CommonDataSource, DataSourceDlg, CommonDataSourceDlg )
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


class ClassVar(object):
    def __init__(self):
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

## test fixture
class DataSourceMethodsTest(unittest.TestCase):

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



    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        
        print "SEED =", self.__seed 
        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception, e:
            error = True
        self.assertEqual(error, True)


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
        dsd = DataSourceDlg()
        ds = dsd.datasource
        form = DataSourceMethods(dsd, ds)

        ds = DataSource()
        dsd = ds.dialog
        form = DataSourceMethods(dsd, ds)



    ## constructor test
    # \brief It tests default settings
    def test_constructor_accept_setFocus(self):
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
        self.assertEqual(form.ui.dParameterTableWidget.rowCount(),len(form.dbParam))

        for i in range(len(cv.dbParameters)):
            it = form.ui.dParameterTableWidget.item(i, 0) 
            k = str(it.text())
            self.assertTrue(k in cv.dbParameters.keys())
            it2 = form.ui.dParameterTableWidget.item(i, 1) 
            self.assertEqual(it2.text(), cv.dbParameters[k])
            self.assertEqual(form.dbParam[k], cv.dbParameters[k])

        


    def check_updateForm(self, form, cds, func = "updateForm"):
        meth = DataSourceMethods(form, cds)


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

        
        self.assertEqual(cds.tree, False)
        
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
        
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form)

        cds.doc = doc
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"doc":doc})
        form.ui.docTextEdit.setText("")
        cds.doc = ''

        cds.dataSourceType = dataSourceType
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(), None)
        self.check_form(form, {"dataSourceType":dataSourceType})
        index = form.ui.typeComboBox.findText('CLIENT')
        form.ui.typeComboBox.setCurrentIndex(index)
        cds.dataSourceType = 'CLIENT'

        cds.dataSourceName = dataSourceName
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"dataSourceName":dataSourceName})
        form.ui.nameLineEdit.setText("")
        cds.dataSourceName = ''



        cds.clientRecordName = clientRecordName
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"clientRecordName":clientRecordName})
        form.ui.cRecNameLineEdit.setText("")
        cds.clientRecordName = ''



        cds.tangoDeviceName = tangoDeviceName
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"tangoDeviceName":tangoDeviceName})
        form.ui.tDevNameLineEdit.setText("")
        cds.tangoDeviceName = ''

        cds.tangoMemberName = tangoMemberName
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"tangoMemberName":tangoMemberName})
        form.ui.tMemberNameLineEdit.setText("")
        cds.tangoMemberName = ''

        cds.tangoMemberType = tangoMemberType
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"tangoMemberType":tangoMemberType})
        index = form.ui.tMemberComboBox.findText('attribute')
        form.ui.tMemberComboBox.setCurrentIndex(index)
        cds.tangoMemberType = ''


        cds.tangoHost = tangoHost
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"tangoHost":tangoHost})
        form.ui.tHostLineEdit.setText("")
        cds.tangoHost = ''

        cds.tangoPort = tangoPort
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"tangoPort":tangoPort})
        form.ui.tPortLineEdit.setText("")
        cds.tangoPort = ''

        cds.tangoEncoding = tangoEncoding
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"tangoEncoding":tangoEncoding})
        form.ui.tEncodingLineEdit.setText("")
        cds.tangoEncoding = ''




        cds.dbType = dbType
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"dbType":dbType})
        index = form.ui.dTypeComboBox.findText('MYSQL')
        form.ui.dTypeComboBox.setCurrentIndex(index)
        cds.dbType = ''

        cds.dbDataFormat = dbDataFormat
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"dbDataFormat":dbDataFormat})
        index = form.ui.dFormatComboBox.findText('SCALAR')
        form.ui.dFormatComboBox.setCurrentIndex(index)
        cds.dbDataFormat = ''

        cds.dbQuery = dbQuery
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"dbQuery":dbQuery})
        form.ui.dQueryLineEdit.setText("")
        cds.dbQuery = ''
        
        cds.dbParameters = dict(dbParameters)
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
        self.check_form(form, {"dbParameters":dbParameters})
        while form.ui.dParameterTableWidget.rowCount():
            form.ui.dParameterTableWidget.removeRow(0)
        form.ui.dParameterTableWidget.clear()
        cds.dbParameters = {}
        form.dbParam ={}


        cds.dbParameters = dict(dbParameters2)
        self.check_form(form)
        self.assertEqual(getattr(meth, func)(),None)
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
        self.assertEqual(getattr(meth, func)(),None)
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

    


    ## constructor test
    # \brief It tests default settings
    def test_updateForm_errors(self):
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



    ## constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        self.check_updateForm(form, cds)


        cds = DataSource()
        form = cds.dialog
        self.check_updateForm(form, cds)
    


    ## constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  


        form = DataSourceDlg()
        cds = form.datasource
        self.check_updateForm(form, cds, "reset")


        cds = DataSource()
        form = cds.dialog
        self.check_updateForm(form, cds, "reset")
    



        



    ## constructor test
    # \brief It tests default settings
    def tttest_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        n1 =  self.__rnd.randint(1, 9) 

        dataSourceType = self.__rnd.choice("CLIENT","TANGO","DB")
        doc = "My document %s" % n1
        clientRecordName =  "My document %s" % n1
        tangoDeviceName =  "Mydevice %s" % n1
        tangoMemberName =  "Mymemeber %s" % n1
        tangoMemberType = self.__rnd.choice("property","command","attribute") 
        tangoHost =  "haso.desy.de %s" % n1
        tangoPort =  "1000%s" % n1
        tangoEncoding =  "UTF%s" % n1
        dbType = self.__rnd.choice("MYSQL","ORACLE","PGSQL") 
        dbDataFormat =  self.__rnd.choice("SCALAR","SPECTRUM","IMAGE") 
        dbQuery =  "select name from device limit %s" % n1
        dbParameters =  {"DB name":"sdfsdf%s" % n1,
                   "DB host":"werwer%s" % n1, 
                   "DB port":"werwer%s" % n1, 
                   "DB user":"werwer%s" % n1, 
                   "DB password":"werwer%s" % n1, 
                   "Mysql cnf":"werwer%s" % n1, 
                   "Oracle mode":"werwer%s" % n1, 
                   "Oracle DSN":"asdasdf%s" % n1}        
        dataSourceName =  "mydatasource%s" % n1

        name = "myname"
        nType = "NXEntry"
        nType2 = "NX_INT64"
        units = "seconds"
        value = "14:45"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        nn =  self.__rnd.randint(1, 9) 

        dimensions = [self.__rnd.randint(1, 40)  for n in range(nn)]
        
        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.name = name

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText(nType2))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""
        index2 = form.ui.typeComboBox.findText('other ...')
        form.ui.typeComboBox.setCurrentIndex(index2)



        form.units = units

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.unitsLineEdit.setText("")
        form.units = ""


        form.dimensions = dimensions

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.rank,0)
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
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
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.updateForm(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))



        form.ui.docTextEdit.setText("")






        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.units = units
        form.value = value
        form.attributes = attributes

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())

        self.assertEqual(form.updateForm(),None)
    
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        self.assertEqual(form.ui.valueLineEdit.text(), value)
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
    def tttest_constructor_accept_long(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        
        self.assertTrue(not form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myfield"
        nType = "NX_DATE_TIME"
        units = "seconds"
        value = "14:45"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        QTest.keyClicks(form.ui.typeLineEdit, nType)
        self.assertEqual(form.ui.typeLineEdit.text(), nType)

        QTest.keyClicks(form.ui.unitsLineEdit, units)
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        QTest.keyClicks(form.ui.valueLineEdit, value)
        self.assertEqual(form.ui.valueLineEdit.text(), value)


        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

     
        self.assertTrue(not form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(not form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(not form.ui.unitsLineEdit.text().isEmpty())
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
    def tttest_getState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.units, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()

        name = "myname"
        nType = "NXEntry"
        units = "Tmm"
        value = "asd1234"
        doc = "My documentation: \n ble ble ble "
        rank = 3
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        dimensions = [1, 2, 3, 4]

        
        self.assertEqual(form.getState(),('','','','','',0,{},[]))
    

        form.name = name

        self.assertEqual(form.getState(),(name,'','','','',0,{},[]))
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.name = ""

        form.nexusType = nType
        self.assertEqual(form.getState(),('',nType,'','','',0,{},[]))

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.nexusType = ""


        form.units = units
        self.assertEqual(form.getState(),('','',units,'','',0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.units = ""

        form.value = value
        self.assertEqual(form.getState(),('','','',value,'',0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.value = ""



        form.doc = doc
        self.assertEqual(form.getState(),('','','','',doc,0,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.doc = ""





        form.rank = rank
        self.assertEqual(form.getState(),('','','','','',rank,{},[]))
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertEqual(state[4],'')
        self.assertEqual(state[5],0)
        self.assertEqual(state[7],[])
        self.assertEqual(len(state),8)
        self.assertEqual(len(state[6]),len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[6][at])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertEqual(state[4],'')
        self.assertEqual(state[5],0)
        self.assertEqual(state[6],{})
        self.assertEqual(len(state),8)
        self.assertEqual(len(state[7]),len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[7][i])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.dimensions = []


        form.name = name
        form.nexusType = nType
        form.units = units
        form.value = value
        form.doc = doc
        form.rank = rank
        form.dimensions = dimensions
        form.attributes = attributes

        state = form.getState()

        self.assertEqual(state[0],name)
        self.assertEqual(state[1],nType)
        self.assertEqual(state[2],units)
        self.assertEqual(state[3],value)
        self.assertEqual(state[4],doc)
        self.assertEqual(state[5],rank)
        self.assertEqual(len(state),8)
        self.assertTrue(state[6] is not attributes)
        self.assertEqual(len(state[6]),len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[6][at])
        self.assertEqual(len(state[7]),len(dimensions))
        for i in range(len(dimensions)):
            self.assertEqual(dimensions[i], state[7][i])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)







    ## constructor test
    # \brief It tests default settings
    def tttest_setState(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()


        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()


        name = "myname"
        nType = "NXEntry"
        units = "Tmm"
        value = "asd1234"
        doc = "My documentation: \n ble ble ble "
        rank = 3
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        dimensions = [1, 2, 3, 4]

        
        self.assertEqual(form.setState(['','','','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})


        self.assertEqual(form.setState([name,'','','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, name)
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.name = ""



        self.assertEqual(form.setState(['',nType,'','','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, nType)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.nexusType = ''




        self.assertEqual(form.setState(['','',units,'','',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.units, units)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.units = ''




        self.assertEqual(form.setState(['','','',value,'',0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertEqual(form.attributes, {})

        form.value = ''





        self.assertEqual(form.setState(['','','','',doc,0,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.units, '')

        form.doc = ''






        self.assertEqual(form.setState(['','','','','',rank,{},[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, rank) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})

        form.rank = 0




        self.assertEqual(form.setState(['','','','','',0,attributes,[]]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        self.assertEqual(form.attributes, attributes)

        form.attributes = {}



        self.assertEqual(form.setState(['','','','','',0,{},dimensions]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, dimensions)
        self.assertEqual(form.attributes, {})

        form.dimensions = {}

        self.assertEqual(form.setState([name,nType,units,value,doc,rank,attributes,dimensions]), None)
    

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        self.assertEqual(form.name, name)
        self.assertEqual(form.nexusType, nType)
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.value, value)
        self.assertEqual(form.units, units)
        self.assertEqual(form.rank, rank) 
        self.assertEqual(form.dimensions, dimensions)
        self.assertEqual(form.attributes, attributes)



        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)


        self.assertEqual(form.result(),0)





    ## constructor test
    # \brief It tests default settings
    def tttest_linkDataSource(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()
        form.createGUI()

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        form.units = units
        form.value = value
        form.doc = doc
        form.attributes = attributes
        form.dimensions = dimensions
        form.rank = rank
        form.dsLabel = 'Sdatasources'

        myds = "mydsName"
        self.assertEqual(form.linkDataSource(myds),None)
    
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertEqual(form.ui.unitsLineEdit.text(),units)
        self.assertEqual(form.ui.valueLineEdit.text(), "$%s.%s" % (form.dsLabel, myds) )



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
    def tttest_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = DataSourceMethods()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.rank, 0) 
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form = DataSourceMethods()
        form.show()
        self.assertEqual(form.createGUI(),None)

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
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
        attributes = {"myattr":"myvalue","myattr2":"myvalue2","myattr3":"myvalue3" }
        nn =  self.__rnd.randint(1, 9) 

        dimensions = [self.__rnd.randint(1, 40)  for n in range(nn)]
        
        self.assertEqual(form.updateForm(),None)
    

        form = DataSourceMethods()
        form.show()
        form.name = name


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.nameLineEdit.text(),name)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.nameLineEdit.setText("")

        form.name = ""

        form = DataSourceMethods()
        form.show()
        form.nexusType = nType


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.ui.typeLineEdit.text(), nType)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""




        form = DataSourceMethods()
        form.show()

        form.nexusType = nType2

        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText(nType2))

        form.ui.typeLineEdit.setText("")
        form.nexusType = ""
        index2 = form.ui.typeComboBox.findText('other ...')
        form.ui.typeComboBox.setCurrentIndex(index2)



        form = DataSourceMethods()
        form.show()
        form.units = units


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertEqual(form.rank,0)
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.unitsLineEdit.setText("")
        form.units = ""


        form = DataSourceMethods()
        form.show()
        form.dimensions = dimensions


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str(dimensions))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))
        form.ui.dimLabel.setText("[]")
        form.dimensions = []

        form = DataSourceMethods()
        form.show()

        form.rank = nn
        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),str([0]*len(dimensions)).replace('0','*'))
        self.assertEqual(form.rank,len(dimensions))
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.dimLabel.setText("[]")
        form.dimensions = []
        form.rank = 0

        form = DataSourceMethods()
        form.show()
        form.value = value


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))


        form.ui.valueLineEdit.setText("")
        form.value = ""


        form = DataSourceMethods()
        form.show()
        form.doc = doc


        self.assertEqual(form.createGUI(),None)
    
        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)
        self.assertTrue(form.ui.unitsLineEdit.text().isEmpty())
        self.assertTrue(form.ui.valueLineEdit.text().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(),'[]')
        self.assertEqual(form.ui.typeComboBox.currentIndex(), 
                         form.ui.typeComboBox.findText('other ...'))



        form.ui.docTextEdit.setText("")






        form = DataSourceMethods()
        form.show()
        form.name = name
        form.doc = doc
        form.nexusType = nType
        form.units = units
        form.value = value
        form.attributes = attributes


        self.assertEqual(form.createGUI(),None)
    
        self.assertEqual(form.ui.unitsLineEdit.text(), units)
        self.assertEqual(form.ui.valueLineEdit.text(), value)
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
    def tttest_setFromNode(self):
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




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
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





    ## constructor test
    # \brief It tests default settings
    def tttest_setFromNode_parameter(self):
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




        form = DataSourceMethods()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode(qdn)


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
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






    ## constructor test
    # \brief It tests default settings
    def tttest_setFromNode_nonode(self):
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




        form = DataSourceMethods()
        form.show()
        form.node = None
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])

        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)


    ## constructor test
    # \brief It tests default settings
    def tttest_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dks = []
        doc = QDomDocument()
        nname = "field"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn) 




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])



        self.assertTrue(form.ui.nameLineEdit.text().isEmpty()) 
        self.assertTrue(form.ui.typeLineEdit.text().isEmpty())
        self.assertTrue(form.ui.docTextEdit.toPlainText().isEmpty())
        self.assertEqual(form.ui.dimLabel.text(), '[]')

        self.assertEqual(form.ui.attributeTableWidget.columnCount(),2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(),0)








    ## constructor test
    # \brief It tests default settings
    def tttest_populateAttribute_setFromNode(self):
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




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.units, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.units, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        
        form.setFromNode()


        self.assertEqual(form.name, "myname%s" %  nn)
        self.assertEqual(form.value, ("".join(["\nVAL\n %s\n" %  i  for i in range(nval)])).strip())
        self.assertEqual(form.units, 'mmyunits%s'%nn)
        self.assertEqual(form.nexusType, "mytype%s" %  nn)
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
    def tttest_populateAttribute_setFromNode_selected_wrong(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {}) 
        self.assertEqual(form.units, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.subItems, 
                         ['attribute', 'datasource', 'doc', 'dimensions', 'enumeration', 'strategy'])
        self.assertTrue(isinstance(form.ui, Ui_DataSourceMethods))

        form.createGUI()
        
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.value, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.dimensions, [])
        self.assertEqual(form.units, '')
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
    def tttest_populateAttribute_setFromNode_selected(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
            mdim.appendChild(dim)
                
        qdn.appendChild(mdim) 




        form = DataSourceMethods()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.nexusType, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.units, '')
        self.assertEqual(form.value, '')
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







    ## constructor test
    # \brief It tests default settings
    def tttest_populateAttribute_setFromNode_selected_addAttribute(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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








    ## constructor test
    # \brief It tests default settings
    def tttest_populateAttribute_setFromNode_selected_tableItemChanged(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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
    def tttest_updateNode(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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

        mydoc = form.node.firstChildElement(QString("doc"))           
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
                self.assertEqual(mdimensions[ind-1], vl)
            child = child.nextSibling()    

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)






    ## constructor test
    # \brief It tests default settings
    def tttest_updateNode_withindex(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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

        mydoc = form.node.firstChildElement(QString("doc"))           
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
                self.assertEqual(mdimensions[ind-1], vl)
            child = child.nextSibling()    

        vtext = form.dts.getText(qdn)    
        oldval = unicode(vtext).strip() if vtext else ""
        self.assertEqual(oldval,form.value)

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    ## constructor test
    # \brief It tests default settings
    def tttest_apply(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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

        mydoc = form.node.firstChildElement(QString("doc"))           
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


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc,mdoc)
        
        vtext = form.dts.getText(qdn)    
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

        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc,mdoc)





    ## constructor test
    # \brief It tests default settings
    def tttest_reset(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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

        mydoc = form.node.firstChildElement(QString("doc"))           
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


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    





    ## constructor test
    # \brief It tests default settings
    def tttest_reset_button(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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

        mydoc = form.node.firstChildElement(QString("doc"))           
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


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    











    def myAction(self):
        self.performed = True


    ## constructor test


    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions(self):
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

    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action(self):
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




    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_button(self):
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



    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_button(self):
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




    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_button(self):
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






    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_link_button(self):
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




    ## constructor test
    # \brief It tests default settings
    def ttttest_connect_actions_with_action_and_apply_button(self):
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





    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_and_sapply_button(self):
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


    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_and_slink_button(self):
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




    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_and_apply_button_noname(self):
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





    ## constructor test
    # \brief It tests default settings
    def tttest_connect_actions_with_action_link_and_apply_button_noname(self):
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






    ## constructor test
    # \brief It tests default settings
    def tttest_appendElement(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
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


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
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
                self.assertEqual(dimensions[ind-1], vl)
            child = child.nextSibling()    


        ats2= {u'shortname2': u'my2nshort%s' % nn, u'unit2': u'my2units%s' % nn}

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
            elif nm == "units":
                self.assertEqual(vl, "my2units%s" % nn)
                cnt += 1 
            else:
                print ats2, nm
                self.assertEqual(vl,ats2[str(nm)])
        self.assertEqual(len(attrs),attributeMap.count() - cnt)







    ## constructor test
    # \brief It tests default settings
    def tttest_appendElement_error(self):
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
        mdim.setAttribute("rank", QString(unicode(rn)))
        
        for i in range(rn):
            dim = doc.createElement(QString("dim"))
            dim.setAttribute(QString("index"), QString(unicode(i+1)))
            dim.setAttribute(QString("value"), QString(unicode(dimensions[i])))
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


        mydoc = form.node.firstChildElement(QString("doc"))           
        text = form.dts.getText(mydoc)    
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(olddoc, "".join(["\nText\n %s\n" %  n for n in range(ndcs)]).strip())
        
        vtext = form.dts.getText(qdn)    
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
        

if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
