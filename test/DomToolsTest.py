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
## \file DomToolsTest.py
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
from ndtsconfigtool.DomTools import DomTools



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class DomToolsTest(unittest.TestCase):

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
        self.__seed = 19735062335824498925800919817530668364


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



    def test_getFirstElement(self):
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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)

        dts = DomTools()


        for k in range(nkids):
            ks = ci.child(k)
            el = dts.getFirstElement(qdn,  "kid%s" %  k)
            self.assertEqual(el, kds[k])
            el = dts.getFirstElement(doc,  "kid%s" %  k)
            self.assertEqual(el, kds[k])




    def test_getText(self):
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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)

        dts = DomTools()


        for k in range(nkids):
            ks = ci.child(k)
            tx = dts.getText(ks.node)
            self.assertEqual(tx, "\nText\n %s\n" %  k)
            tx = dts.getText(qdn)
            self.assertEqual(tx, "")


    def test_replaceText(self):
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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)

        dts = DomTools()


        for k in range(nkids):
            ki = cm.index(k,0,di)
            ks = ci.child(k)
            text = "New %s" % k
            dts.replaceText(ks.node, ki, cm, text)
            tx = dts.getText(ks.node)
            self.assertEqual(tx, text)
            dts.replaceText(ks.node, ki, cm)
            tx = dts.getText(ks.node)
            self.assertEqual(tx, "")
            dts.replaceText(ks.node, ki, cm, text)
            tx = dts.getText(ks.node)
            self.assertEqual(tx, text)



    def test_removeNode_noparent(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dts = DomTools()

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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        rmvd =  self.__rnd.randint(0,nkids-1) 
        rmkd = ci.child(rmvd)

        dts.removeNode(rmvd, QModelIndex(),cm)


        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)



    def test_removeNode_nonode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dts = DomTools()

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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        rmvd =  self.__rnd.randint(0,nkids-1) 
        rmkd = ci.child(rmvd)

        dts.removeNode(qdn, di, cm)


        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)


    def test_removeNode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        dts = DomTools()

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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        rmvd =  self.__rnd.randint(0,nkids-1) 
        rmkd = ci.child(rmvd)
        rmkd2 = ci.child(rmvd)


        dts.removeNode(rmkd.node, di, cm)

        for k in range(nkids):
            if k == rmvd:
                continue
            kk = k if k < rmvd else k-1
            ks = ci.child(kk)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),kk)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)


    def test_insertItem(self):
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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        insd =  self.__rnd.randint(0,nkids-1) 
        inkd = doc.createElement("insertedkid")
        self.assertTrue(not cm.insertItem(insd, inkd, QModelIndex()))


        self.assertTrue(cm.insertItem(insd, inkd, di))


        for k in range(nkids+1):
            ks = ci.child(k)
            if k == insd:
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node, inkd)
                self.assertEqual(ks.parent.node, qdn)
                self.assertEqual(ks.node.nodeName(), "insertedkid")
                self.assertEqual(ks.parent, ci)
                continue
            kk = k if k < insd else k-1
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[kk])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  kk)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[kk])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % kk)
            self.assertEqual(ks.child(0).parent, ks)





    def test_appendItem(self):
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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        inkd = doc.createElement("insertedkid")
        self.assertTrue(not cm.appendItem(inkd, QModelIndex()))


        self.assertTrue(cm.appendItem(inkd, di))


        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)
#            print k,ks.childNumber()
        k = nkids   
        ks = ci.child(k)
        self.assertTrue(isinstance(ks, ComponentItem))
        self.assertTrue(isinstance(ks.parent, ComponentItem))
        self.assertEqual(ks.childNumber(),k)
        self.assertEqual(ks.node, inkd)
        self.assertEqual(ks.parent.node, qdn)
        self.assertEqual(ks.node.nodeName(), "insertedkid")
        self.assertEqual(ks.parent, ci)





    def test_removeItem(self):
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
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0,0,ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0,0)
        self.assertEqual(cm.columnCount(iv), 3)
        
        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        rmvd =  self.__rnd.randint(0,nkids-1) 
        rmkd = ci.child(rmvd)
        self.assertTrue(not cm.removeItem(rmvd, QModelIndex()))


        self.assertTrue(cm.removeItem(rmvd, di))


        for k in range(nkids):
            if k == rmvd:
                continue
            kk = k if k < rmvd else k-1
            ks = ci.child(kk)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),kk)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

if __name__ == '__main__':
    unittest.main()
