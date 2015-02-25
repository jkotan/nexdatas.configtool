#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file CommonDataSourceTest.py
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


from PyQt4.QtGui import (QApplication)

from nxsconfigtool.DataSource import CommonDataSource
from nxsconfigtool.NodeDlg import NodeDlg

##  Qt-application
app = None

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class CommonDataSourceTest(unittest.TestCase):

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
#        self.__seed =335783554629280825854815889576355181078
#        self.__seed =56405821691954067238837069340540387163

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
    def ttest_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        cds = CommonDataSource()
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
        



    ## constructor test
    # \brief It tests default settings
    def ttest_set_get_clean_State(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        cds = CommonDataSource()
        nn =  self.__rnd.randint(0, 10) 

        dataSourceType = 'TANGO%s' % nn
        dataSourceName = 'mot_01%s' %nn
        doc = u'Documentation: motor %s' %nn

        clientRecordName = 'MyRecord%s' %nn

        tangoDeviceName = 'mydevice%s' %nn
        tangoMemberName = 'position%s' %nn
        tangoMemberType = 'attribute%s' %nn
        tangoHost = 'haso.desy.de%s' %nn
        tangoGroup = 'group%s' %nn
        tangoPort = '100%s' %nn
        tangoEncoding = 'UTF%s' %nn

        dbType = 'ORACLE%s' %nn
        dbDataFormat = 'SPECTRUM%s' %nn
        dbQuery = "SELET name from device limit %s" %nn
        dbParameters = {}
        for i in range(nn):
            dbParameters["param%s" % i] = "value%s" %i

        peResult = "ds.result%s" %nn 
        peInput =  "ds.source%s ds.source1%s ds.source2%s" %(nn,nn,nn)
        peScript = "import math\n ds.result= sin(ds.x)"
        peDataSources = {}
        for i in range(nn):
            peDataSources["param%s" % i] = "<datasource%s/>" %i
            
        cds.setState((dataSourceType,
                      doc,
                      clientRecordName, 
                      tangoDeviceName,
                      tangoMemberName,
                      tangoMemberType,
                      tangoHost,
                      tangoPort,
                      tangoEncoding,
                      tangoGroup,
                      dbType,
                      dbDataFormat,
                      dbQuery,
                      dbParameters,
                      peResult,
                      peInput,
                      peScript,
                      peDataSources,
                      dataSourceName
                      ))
        

        self.assertEqual(cds.dataSourceType, dataSourceType)
        self.assertEqual(cds.doc, doc)

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, dataSourceName)
        self.assertEqual(cds.clientRecordName, clientRecordName)
        self.assertEqual(cds.tangoDeviceName, tangoDeviceName)
        self.assertEqual(cds.tangoMemberName, tangoMemberName)
        self.assertEqual(cds.tangoMemberType, tangoMemberType)
        self.assertEqual(cds.tangoHost, tangoHost)
        self.assertEqual(cds.tangoPort, tangoPort)
        self.assertEqual(cds.tangoEncoding, tangoEncoding)

        self.assertEqual(cds.dbType, dbType)
        self.assertEqual(cds.dbDataFormat, dbDataFormat)
        self.assertEqual(cds.dbQuery, dbQuery)
        self.assertEqual(cds.dbParameters, dbParameters)

        self.assertEqual(cds.peResult, peResult)
        self.assertEqual(cds.peInput, peInput)
        self.assertEqual(cds.peScript, peScript)
        self.assertEqual(cds.peDataSources, peDataSources)


        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, False)

        self.assertEqual(cds.ids, None)

        
        self.assertEqual(cds.tree, False)
        

        state = cds.getState()

    


        self.assertEqual(cds.dataSourceType, dataSourceType)
        self.assertEqual(cds.doc, doc)

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, dataSourceName)
        self.assertEqual(cds.clientRecordName, clientRecordName)
        self.assertEqual(cds.tangoDeviceName, tangoDeviceName)
        self.assertEqual(cds.tangoMemberName, tangoMemberName)
        self.assertEqual(cds.tangoMemberType, tangoMemberType)
        self.assertEqual(cds.tangoHost, tangoHost)
        self.assertEqual(cds.tangoPort, tangoPort)
        self.assertEqual(cds.tangoEncoding, tangoEncoding)

        self.assertEqual(cds.dbType, dbType)
        self.assertEqual(cds.dbDataFormat, dbDataFormat)
        self.assertEqual(cds.dbQuery, dbQuery)
        self.assertEqual(cds.dbParameters, dbParameters)

        self.assertEqual(cds.peResult, peResult)
        self.assertEqual(cds.peInput, peInput)
        self.assertEqual(cds.peScript, peScript)
        self.assertEqual(cds.peDataSources, peDataSources)


        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, False)
        self.assertEqual(cds.ids, None)
        self.assertEqual(cds.tree, False)
        
        cds.clear()

        self.assertEqual(cds.applied, False)
        self.assertEqual(cds.ids, None)
        self.assertEqual(cds.tree, False)
        
        cds.applied = True
        cds.ids = nn
        cds.tree = True

        cds.clear()


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

        self.assertEqual(cds.peResult, 'ds.result')
        self.assertEqual(cds.peInput, '')
        self.assertEqual(cds.peScript, '')
        self.assertEqual(cds.peDataSources, {})

        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, True)
        self.assertEqual(cds.ids, nn)        
        self.assertEqual(cds.tree, True)


        cds.setState(state)

    


        self.assertEqual(cds.dataSourceType, dataSourceType)
        self.assertEqual(cds.doc, doc)

        self.assertTrue(isinstance(cds.dialog, NodeDlg))
        self.assertEqual(cds.dataSourceName, dataSourceName)
        self.assertEqual(cds.clientRecordName, clientRecordName)
        self.assertEqual(cds.tangoDeviceName, tangoDeviceName)
        self.assertEqual(cds.tangoMemberName, tangoMemberName)
        self.assertEqual(cds.tangoMemberType, tangoMemberType)
        self.assertEqual(cds.tangoHost, tangoHost)
        self.assertEqual(cds.tangoPort, tangoPort)
        self.assertEqual(cds.tangoEncoding, tangoEncoding)

        self.assertEqual(cds.dbType, dbType)
        self.assertEqual(cds.dbDataFormat, dbDataFormat)
        self.assertEqual(cds.dbQuery, dbQuery)
        self.assertEqual(cds.dbParameters, dbParameters)

        self.assertEqual(cds.peResult, peResult)
        self.assertEqual(cds.peInput, peInput)
        self.assertEqual(cds.peScript, peScript)
        self.assertEqual(cds.peDataSources, peDataSources)

        self.assertEqual(cds.externalSave, None)
        self.assertEqual(cds.externalStore, None)
        self.assertEqual(cds.externalClose, None)
        self.assertEqual(cds.externalApply, None)

        self.assertEqual(cds.applied, True)
        self.assertEqual(cds.ids, nn)
        self.assertEqual(cds.tree, True)
        
        

if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
