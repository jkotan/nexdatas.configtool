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
## \file ComponentModelTest.py
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
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject, QAbstractItemModel, QModelIndex, QVariant
from PyQt4.QtXml import QDomNode, QDomDocument

from ndtsconfigtool.ComponentModel import ComponentModel
from ndtsconfigtool.ComponentItem import ComponentItem



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class ComponentModelTest(unittest.TestCase):

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
#        self.__seed = 105186230414225794971485160270620812570


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
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])

            
        allAttr = False    
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        self.assertEqual(cd.parent, None)
        self.assertEqual(cd.childNumber(),0)
        self.assertEqual(cd.node.nodeName(), "#document")
        
        ci = cd.child(0)
        self.assertEqual(ci.parent, cd)
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            self.assertTrue(isinstance(ci.child(k), ComponentItem))
            self.assertTrue(isinstance(ci.child(k).parent, ComponentItem))
            self.assertEqual(ci.child(k).childNumber(),k)
            self.assertEqual(ci.child(k).node, kds[k])
            self.assertEqual(ci.child(k).parent.node, qdn)
            self.assertEqual(ci.child(k).node.nodeName(), "kid%s" %  k)
            self.assertEqual(ci.child(k).parent, ci)




    ## constructor test
    # \brief It tests default settings
    def test_headerData(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])

            
        allAttr = False    
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        hd = cm.headerData(0, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Name')
        hd = cm.headerData(0, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Name')


        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Type')
        hd = cm.headerData(1, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Type')


        hd = cm.headerData(2, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Value')
        hd = cm.headerData(2, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Value')


        hd = cm.headerData(3, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), '')
        hd = cm.headerData(3, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), '')


        hd = cm.headerData(-1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), '')
        hd = cm.headerData(-1, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), '')

        
        cm.setAttributeView(True)

        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Attributes')
        hd = cm.headerData(1, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Attributes')

        cm.setAttributeView(False)

        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Type')
        hd = cm.headerData(1, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Type')
        

        allAttr = True
        cm = ComponentModel(doc,allAttr)
        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Attributes')
        hd = cm.headerData(1, Qt.Horizontal,Qt.DisplayRole)
        self.assertTrue(isinstance(hd, QVariant))        
        self.assertEqual(hd.toString(), 'Attributes')


    ## constructor test
    # \brief It tests default settings
    def test_data(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])

            
        allAttr = False    
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        dt = cm.data(QModelIndex())
        self.assertTrue(isinstance(dt, QVariant))        
        self.assertEqual(dt.toString(), '')

        for role in range(1,5):
            dt = cm.data(cm.rootIndex,role)
            self.assertTrue(isinstance(dt, QVariant))        
            self.assertEqual(dt.toString(), '')



        dt = cm.data(cm.rootIndex)
        self.assertTrue(isinstance(dt, QVariant))         
        self.assertEqual(dt.toString(), '#document')

        dt = cm.data(cm.rootIndex, Qt.DisplayRole)
        self.assertTrue(isinstance(dt, QVariant))         
        self.assertEqual(dt.toString(), '#document')


    ## constructor test
    # \brief It tests default settings
    def test_data_name(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            kds[-1].setAttribute("name","myname%s" %  n)
            kds[-1].setAttribute("type","mytype%s" %  n)
            kds[-1].setAttribute("units","myunits%s" %  n)
            qdn.appendChild(kds[-1]) 
            tkds.append(doc.createTextNode("\nText\n %s\n" %  n))
            kds[-1].appendChild(tkds[-1]) 

#        print doc.toString()    
            
        allAttr = False    
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)
        
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        ci = cd.child(0)
        for n in range(nkids):
            kd = ci.child(n)


            ki0 = cm.index(n,0,di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(dt.toString(), 'kid%s: myname%s' % (n,n))


            ki1 = cm.index(n,1,di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), 'mytype%s' % n)


            ki2 = cm.index(n,2,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')
 

            ki2 = cm.index(n,-1,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')
 

            ki2 = cm.index(n,3,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')
            





    def test_data_name_attr(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            kds[-1].setAttribute("name","myname%s" %  n)
            kds[-1].setAttribute("type","mytype%s" %  n)
            kds[-1].setAttribute("units","myunits%s" %  n)
            qdn.appendChild(kds[-1]) 
            tkds.append(doc.createTextNode("\nText\n %s\n" %  n))
            kds[-1].appendChild(tkds[-1]) 

#        print doc.toString()    
            
        allAttr = False    
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)
        
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        ci = cd.child(0)
        for n in range(nkids):
            kd = ci.child(n)

            cm.setAttributeView(False)

            ki0 = cm.index(n,0,di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(dt.toString(), 'kid%s: myname%s' % (n,n))


            ki1 = cm.index(n,1,di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), 'mytype%s' % n)


            ki2 = cm.index(n,2,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')
 

            ki2 = cm.index(n,-1,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')
 

            ki2 = cm.index(n,3,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')
            
            cm.setAttributeView(True)


            ki0 = cm.index(n,0,di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(dt.toString(), 'kid%s: myname%s' % (n,n))


            ki1 = cm.index(n,1,di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), 'units="myunits%s" type="mytype%s" name="myname%s"' % (n,n,n))


            ki2 = cm.index(n,2,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')



    def test_data_name_attr_true(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            kds[-1].setAttribute("name","myname%s" %  n)
            kds[-1].setAttribute("type","mytype%s" %  n)
            kds[-1].setAttribute("units","myunits%s" %  n)
            qdn.appendChild(kds[-1]) 
            tkds.append(doc.createTextNode("\nText\n %s\n" %  n))
            kds[-1].appendChild(tkds[-1]) 

#        print doc.toString()    
            
        allAttr = True
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)
        
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        ci = cd.child(0)
        for n in range(nkids):
            kd = ci.child(n)


            ki0 = cm.index(n,0,di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(dt.toString(), 'kid%s: myname%s' % (n,n))


            ki1 = cm.index(n,1,di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), 'units="myunits%s" type="mytype%s" name="myname%s"' % (n,n,n))

            ki2 = cm.index(n,2,di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')






    def test_data_name_text(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            kds[-1].setAttribute("name","myname%s" %  n)
            kds[-1].setAttribute("type","mytype%s" %  n)
            kds[-1].setAttribute("units","myunits%s" %  n)
            qdn.appendChild(kds[-1]) 
            tkds.append(doc.createTextNode("\nText\n %s\n" %  n))
            kds[-1].appendChild(tkds[-1]) 

#        print doc.toString()    
            
        allAttr = True
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)
        
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        ci = cd.child(0)
        for n in range(nkids): 
            allAttr = not allAttr
            cm.setAttributeView(allAttr)            
            ki = cm.index(n,0,di)

            ti = cm.index(0,0,ki)
            dt = cm.data(ti)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(dt.toString(), '#text')


            ti = cm.index(0,1,ki)
            dt = cm.data(ti)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), '')


            ti = cm.index(0,2,ki)
            dt = cm.data(ti)
            self.assertTrue(isinstance(dt, QVariant))         
            self.assertEqual(str(dt.toString()).strip(), 'Text  %s' % n)


    def test_flags(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            kds[-1].setAttribute("name","myname%s" %  n)
            kds[-1].setAttribute("type","mytype%s" %  n)
            kds[-1].setAttribute("units","myunits%s" %  n)
            qdn.appendChild(kds[-1]) 
            tkds.append(doc.createTextNode("\nText\n %s\n" %  n))
            kds[-1].appendChild(tkds[-1]) 

#        print doc.toString()    
            
        allAttr = True
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        self.assertEqual(cm.flags(QModelIndex()), Qt.ItemIsEnabled)
        ri = cm.rootIndex
        self.assertEqual(cm.flags(ri), Qt.ItemFlags(QAbstractItemModel.flags(cm,ri) |
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
        di = cm.index(0,0,ri)
        self.assertEqual(cm.flags(di), Qt.ItemFlags(QAbstractItemModel.flags(cm,di) |
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
        for n in range(nkids): 
            allAttr = not allAttr
            cm.setAttributeView(allAttr)            
            ki = cm.index(n,0,di)
            self.assertEqual(cm.flags(ki), Qt.ItemFlags(QAbstractItemModel.flags(cm,ki) |
                                                        Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
            ki = cm.index(n,1,di)
            self.assertEqual(cm.flags(ki), Qt.ItemFlags(QAbstractItemModel.flags(cm,ki) |
                                                        Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
            ki = cm.index(n,2,di)
            self.assertEqual(cm.flags(ki), Qt.ItemFlags(QAbstractItemModel.flags(cm,ki) |
                                                        Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
            ki = cm.index(n,3,di)
            self.assertEqual(cm.flags(ki), Qt.ItemIsEnabled)

            ki = cm.index(n,0,di) 
            ti = cm.index(0,0,ki)
            self.assertEqual(cm.flags(ti), Qt.ItemFlags(QAbstractItemModel.flags(cm,ti) |
                                                        Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
            ti = cm.index(0,1,ki)
            self.assertEqual(cm.flags(ti), Qt.ItemFlags(QAbstractItemModel.flags(cm,ti) |
                                                        Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
            ti = cm.index(0,2,ki)
            self.assertEqual(cm.flags(ti), Qt.ItemFlags(QAbstractItemModel.flags(cm,ti) |
                                                        Qt.ItemIsEnabled | Qt.ItemIsSelectable ))
            ti = cm.index(0,3,ki)
            self.assertEqual(cm.flags(ti), Qt.ItemIsEnabled)




    def test_index(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            kds[-1].setAttribute("name","myname%s" %  n)
            kds[-1].setAttribute("type","mytype%s" %  n)
            kds[-1].setAttribute("units","myunits%s" %  n)
            qdn.appendChild(kds[-1]) 
            tkds.append(doc.createTextNode("\nText\n %s\n" %  n))
            kds[-1].appendChild(tkds[-1]) 

#        print doc.toString()    
            
        allAttr = True
        cm = ComponentModel(doc,allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        ri = cm.rootIndex
        di = cm.index(0,0,ri)
        self.assertTrue(isinstance(di, QModelIndex))
        self.assertEqual(di.row(),0)
        self.assertEqual(di.column(),0)
        self.assertEqual(di.internalPointer().node, qdn)
        self.assertEqual(di.internalPointer().parent.node, doc)

        iv = cm.index(0,0)
        self.assertTrue(isinstance(iv, QModelIndex))
        self.assertEqual(iv.row(),0)
        self.assertEqual(iv.column(),0)
        self.assertEqual(iv, di)
        self.assertEqual(iv.internalPointer(),di.internalPointer())
        

        iv = cm.index(0,0,QModelIndex())
        self.assertTrue(isinstance(iv, QModelIndex))
        self.assertEqual(iv.row(),0)
        self.assertEqual(iv.column(),0)
        self.assertEqual(iv, di)
        self.assertEqual(iv.internalPointer(),di.internalPointer())
        
        
        for n in range(nkids): 
            allAttr = not allAttr
            cm.setAttributeView(allAttr)            

            ki = cm.index(n,0,di) 
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(),n)
            self.assertEqual(ki.column(),0)
            self.assertEqual(ki.internalPointer().node, kds[n])
            self.assertEqual(ki.internalPointer().parent.node, qdn)

            ki = cm.index(n,1,di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(),n)
            self.assertEqual(ki.column(),1)
            self.assertEqual(ki.internalPointer().node, kds[n])
            self.assertEqual(ki.internalPointer().parent.node, qdn)

            ki = cm.index(n,2,di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(),n)
            self.assertEqual(ki.column(),2)
            self.assertEqual(ki.internalPointer().node, kds[n])
            self.assertEqual(ki.internalPointer().parent.node, qdn)

            ki = cm.index(n,3,di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(),-1)
            self.assertEqual(ki.column(),-1)
            self.assertEqual(ki.internalPointer(), None)

            ki = cm.index(n,0,di) 
            ti = cm.index(0,0,ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(),0)
            self.assertEqual(ti.column(),0)
            self.assertEqual(ti.internalPointer().node, tkds[n])
            self.assertEqual(ti.internalPointer().parent.node, kds[n])


            ti = cm.index(0,1,ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(),0)
            self.assertEqual(ti.column(),1)
            self.assertEqual(ti.internalPointer().node, tkds[n])
            self.assertEqual(ti.internalPointer().parent.node, kds[n])

            ti = cm.index(0,2,ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(),0)
            self.assertEqual(ti.column(),2)
            self.assertEqual(ti.internalPointer().node, tkds[n])
            self.assertEqual(ti.internalPointer().parent.node, kds[n])

            ti = cm.index(0,3,ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(),-1)
            self.assertEqual(ti.column(),-1)
            self.assertEqual(ti.internalPointer(), None)
        

if __name__ == '__main__':
    unittest.main()
