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
## \file NodeDlgTest.py
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
from PyQt4.QtCore import Qt, QTimer, SIGNAL, QObject, QModelIndex
from PyQt4.QtXml import QDomNode, QDomDocument


from ndtsconfigtool.NodeDlg import NodeDlg
from ndtsconfigtool.ComponentModel import ComponentModel
from ndtsconfigtool.ComponentItem import ComponentItem

from ndtsconfigtool.DomTools import DomTools

##  Qt-application
app = None



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

class MyNodeDlg(NodeDlg):
    def __init__(self, parent=None):
        super(MyNodeDlg, self).__init__(parent)
        self.stack = []

    def updateForm(self):
        self.stack.append("updateForm")

    def updateNode(self, index=QModelIndex()):
        self.stack.append("updateNode")
        self.stack.append(index)


    def createGUI(self):
        self.stack.append("createGUI")
    
    def setFromNode(self, node=None):
        self.stack.append("setFromNode")
        self.stack.append(node)
        

class TestTools(object):
    def __init__(self, parent=None):
        self.stack = []

    def replaceText(self, node, index, model, text):
        self.stack.append("replaceText")
        self.stack.append(node)
        self.stack.append(index)
        self.stack.append(model)
        self.stack.append(text)


    ## appends node
    # \param node DOM node to append
    # \param parent parent node index
    # \param model Component model            
    def appendNode(self, node, parent, model):
        self.stack.append("appendNode")
        self.stack.append(node)
        self.stack.append(parent)
        self.stack.append(model)
   

    ## removes node element
    # \param element DOM node element to remove
    # \param parent parent node index      
    # \param model Component model            
    def removeElement(self, element, parent, model):
        self.stack.append("removeElement")
        self.stack.append(element)
        self.stack.append(parent)
        self.stack.append(model)


    ## replaces node element
    # \param oldElement old DOM node element 
    # \param newElement new DOM node element 
    # \param parent parent node index
    # \param model Component model            
    def replaceElement(self, oldElement, newElement, parent, model):
        self.stack.append("replaceElement")
        self.stack.append(oldElement)
        self.stack.append(newElement)
        self.stack.append(parent)
        self.stack.append(model)

   
    

class TestView(object):
    def __init__(self):
        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 
#        self.__seed = 71366247078680776091931824685320965500
        self.__rnd = random.Random(self.__seed)
        print "VIEW SEED", self.__seed

        self.sindex = None
        self.eindex = None


        self.doc = QDomDocument()
        self.nname = "definition"
        self.qdn = self.doc.createElement(self.nname)
        self.doc.appendChild(self.qdn)
        self.nkids =  self.__rnd.randint(1, 10) 
#        print "NKID", self.nkids
        self.kds = []
        self.tkds = []
        for n in range(self.nkids):
            self.kds.append(self.doc.createElement("kid%s" %  n))
            self.kds[-1].setAttribute("name","myname%s" %  n)
            self.kds[-1].setAttribute("type","mytype%s" %  n)
            self.kds[-1].setAttribute("units","myunits%s" %  n)
            self.qdn.appendChild(self.kds[-1]) 
            self.tkds.append(self.doc.createTextNode("\nText\n %s\n" %  n))
            self.kds[-1].appendChild(self.tkds[-1]) 

#        print doc.toString()    
 
        self.allAttr = False    
        self.testModel = ComponentModel(self.doc,self.allAttr)
#        self.myindex = self.setIndex(0, 0, self.testModel.rootIndex)
        self.myindex = QModelIndex()



    def setIndex(self, row, column, parent):
        self.myindex = self.testModel.index( row, column, parent)
 #       print self.myindex.column()

    def currentIndex(self):
        return self.myindex

    def model(self):
        return self.testModel

    def dataChanged(self, sindex, eindex):
        self.sindex = sindex
        self.eindex = eindex



class Ui_NodeDlg(object):
    pass


## test fixture
class NodeDlgTest(unittest.TestCase):

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
        ## 2 action status
        self.performed2 = False


        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 
#        self.__seed = 332115341842367128541506422124286219441
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

    def myAction(self):
        self.performed = True

    def myAction2(self):
        self.performed2 = True

    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.show()
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertEqual(form.ui, None)
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
        self.assertEqual(form.dsLabel, 'datasources')

        self.assertEqual(form.result(),0)


    ## constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertEqual(form.ui, None)
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        self.assertEqual(form.result(),0)

    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertEqual(form.ui, None)
        self.assertEqual(form.externalApply, None)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertTrue(isinstance(form.ui,Ui_NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertTrue(isinstance(form.ui,Ui_NodeDlg))
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
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
#        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(None,self.myAction),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertTrue(isinstance(form.ui,Ui_NodeDlg))
        self.assertEqual(form.externalDSLink, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.linkDSPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction,self.myAction2),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertTrue(isinstance(form.ui,Ui_NodeDlg))
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, self.myAction2)
        self.performed = False
        self.performed2 = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)
        self.assertEqual(self.performed2, False)
        QTest.mouseClick(form.ui.linkDSPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)
        self.assertEqual(self.performed2, True)


        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)

        vw.myindex =  ki


        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw
        
        form.reset()
        self.assertEqual(vw.sindex,vw.currentIndex())
        self.assertEqual(vw.eindex,vw.currentIndex())
        self.assertEqual(vw.eindex,vw.sindex)

        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_reset_nozero(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()    
        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        cn = self.__rnd.randint(1, 2) 
        ki = vw.model().index(n,cn,di)

        vw.myindex =  ki 
        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw
        
        form.reset()
        self.assertEqual(vw.sindex.row(),vw.currentIndex().row())
        self.assertEqual(vw.sindex.column(),0)
        self.assertEqual(vw.sindex.parent(),vw.currentIndex().parent())
        self.assertEqual(vw.eindex,vw.sindex)

        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_reset_nozero_extended(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = MyNodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()    
        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        cn = self.__rnd.randint(1, 2) 
        ki = vw.model().index(n,cn,di)

        vw.myindex =  ki 
        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw
        
        form.reset()
        self.assertEqual(vw.sindex.row(),vw.currentIndex().row())
        self.assertEqual(vw.sindex.column(),0)
        self.assertEqual(vw.sindex.parent(),vw.currentIndex().parent())
        self.assertEqual(vw.eindex,vw.sindex)

        self.assertEqual(form.stack[0],"setFromNode")
        self.assertEqual(form.stack[1],None)
        self.assertEqual(form.stack[2],"updateForm")
        self.assertEqual(form.result(),0)




    ## constructor test
    # \brief It tests default settings
    def test_replaceText(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)

        vw.myindex =  ki


        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw
        
        form.node =vw.qdn

        root = vw.model().rootIndex.internalPointer().node
        form.replaceText(di)

        ks = di.internalPointer()
        self.assertEqual(ks.node.childNodes().count(), vw.nkids)

        self.assertTrue(isinstance(ks, ComponentItem))
        self.assertTrue(isinstance(ks.parent, ComponentItem))
        self.assertEqual(ks.node, vw.qdn)
        self.assertEqual(ks.parent.node, vw.doc)
        self.assertEqual(ks.parent, ri.internalPointer())
        self.assertEqual(ks.parent.node, ri.internalPointer().node)
        self.assertEqual(ks.node.childNodes().count(), vw.nkids)

        

#        self.assertEqual(dts.stack[0],"replaceText")
#        self.assertEqual(dts.stack[1],vw.qdn)
#        self.assertEqual(dts.stack[2],di)
#        self.assertEqual(dts.stack[3],vw.model())
#        self.assertEqual(dts.stack[4],None)
        ci = di.internalPointer()


        
        text = "My Supper Text"
        form.replaceText(di,text)

        self.assertTrue(isinstance(ks, ComponentItem))
        self.assertTrue(isinstance(ks.parent, ComponentItem))
        self.assertEqual(ks.node, vw.qdn)
        self.assertEqual(ks.parent.node, vw.doc)
        self.assertEqual(ks.parent, ri.internalPointer())
        self.assertEqual(ks.parent.node, ri.internalPointer().node)
        self.assertEqual(ks.node.childNodes().count(), vw.nkids+1)
        ts = ci.child(vw.nkids)
        self.assertEqual(ts.node.nodeName(), "#text")
        self.assertEqual(ts.node.toText().data(), text)
        self.assertEqual(ts.parent, ks)
        


        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_replaceText_noview(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)

        vw.myindex =  ki


        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
#        form.view = vw
        form.view = None
        
        form.node =vw.qdn

        ks = di.internalPointer()
        self.assertEqual(ks.node.childNodes().count(), vw.nkids)
        form.replaceText(di)
        
        ks = di.internalPointer()
        self.assertEqual(ks.node.childNodes().count(), vw.nkids)

        



    ## constructor test
    # \brief It tests default settings
    def test_replaceText_nomodel(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)

        vw.myindex =  ki


        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        vw.testModel = None
        form.view = vw


        form.node =vw.qdn

        ks = di.internalPointer()
        self.assertEqual(ks.node.childNodes().count(), vw.nkids)
        form.replaceText(di)
        ks = di.internalPointer()
        self.assertEqual(ks.node.childNodes().count(), vw.nkids)
        

        



    ## constructor test
    # \brief It tests default settings
    def test_removeElement(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)

        vw.myindex =  ki


        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw
        
        dts = TestTools()
        self.dts = dts
        form.node =vw.qdn

        ci = di.internalPointer()

        for k in range(vw.nkids):
                ks = ci.child(k)
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node, vw.kds[k])
                self.assertEqual(ks.parent.node, vw.qdn)
                self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
                self.assertEqual(ks.parent, ci)
                self.assertTrue(isinstance(ks.child(0), ComponentItem))
                self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
                self.assertEqual(ks.child(0).childNumber(),0)
                self.assertEqual(ks.child(0).node, vw.tkds[k])
                self.assertEqual(ks.child(0).parent.node, ks.node)
                self.assertEqual(ks.child(0).node.nodeName(), "#text")
                self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
                self.assertEqual(ks.child(0).parent, ks)

        form.removeElement(ki.internalPointer().node ,di)

        for kk in range(vw.nkids):
            if kk < n or kk > n :
                k = kk if kk < n else kk-1
                ks = ci.child(k)
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node.nodeName(), "kid%s" %  kk)
                self.assertEqual(ks.node, vw.kds[kk])
                self.assertEqual(ks.parent.node, vw.qdn)
                self.assertEqual(ks.parent, ci)
                self.assertTrue(isinstance(ks.child(0), ComponentItem))
                self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
                self.assertEqual(ks.child(0).childNumber(),0)
                self.assertEqual(ks.child(0).node, vw.tkds[kk])
                self.assertEqual(ks.child(0).parent.node, ks.node)
                self.assertEqual(ks.child(0).node.nodeName(), "#text")
                self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % kk)
                self.assertEqual(ks.child(0).parent, ks)






    ## constructor test
    # \brief It tests default settings
    def test_replaceElement(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)
        n2 = self.__rnd.randint(0, vw.nkids-1) 
        ki2 = vw.model().index(n2,0,di)

        vw.myindex =  ki

        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw
        
        form.node =vw.qdn

        ci = di.internalPointer()
        for i in range(vw.nkids):
            ks =  ci.child(i)
            
        inkd = vw.doc.createElement("insertedkid")
        form.replaceElement(ki.internalPointer().node, inkd, di)
        
        for i in range(vw.nkids):
            ks =  di.internalPointer().child(i)
#            print "N",i, ks.node.nodeName(), ks.node


        for k in range(vw.nkids):
            if k == n:
                ks = ci.child(k)
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node.nodeName(), "insertedkid")
                self.assertEqual(ks.node, inkd)
                self.assertEqual(ks.parent.node, vw.qdn)
                self.assertEqual(ks.parent, ci)
            else:
                ks = ci.child(k)
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node, vw.kds[k])
                self.assertEqual(ks.parent.node, vw.qdn)
                self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
                self.assertEqual(ks.parent, ci)
                self.assertTrue(isinstance(ks.child(0), ComponentItem))
                self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
                self.assertEqual(ks.child(0).childNumber(),0)
                self.assertEqual(ks.child(0).node, vw.tkds[k])
                self.assertEqual(ks.child(0).parent.node, ks.node)
                self.assertEqual(ks.child(0).node.nodeName(), "#text")
                self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
                self.assertEqual(ks.child(0).parent, ks)



        self.assertEqual(form.result(),0)



    ## constructor test
    # \brief It tests default settings
    def test_appendElement(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        form = NodeDlg()
        form.ui = Ui_NodeDlg() 
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])

        vw = TestView()

        ri = vw.model().rootIndex
        di = vw.model().index(0,0,ri)
        n = self.__rnd.randint(0, vw.nkids-1) 
        ki = vw.model().index(n,0,di)
        
        vw.myindex =  ki

        inkd = vw.doc.createElement("insertedkid")

        vw.model().connect(vw.model(),SIGNAL("dataChanged(QModelIndex,QModelIndex)"),vw.dataChanged)
        form.view = vw

        form.node = vw.qdn
        

        self.assertTrue(not form.appendElement(inkd, QModelIndex()))
        
        self.assertTrue(vw.model().rowCount(),vw.nkids)
        self.assertTrue(form.appendElement(inkd, di))

        self.assertTrue(vw.model().rowCount(), vw.nkids+1)
 
        ci = di.internalPointer()

        for k in range(vw.nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, vw.kds[k])
            self.assertEqual(ks.parent.node, vw.qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(),0)
            self.assertEqual(ks.child(0).node, vw.tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)



        k = vw.nkids
        ks = ci.child(k)


        self.assertTrue(isinstance(ks, ComponentItem))
        self.assertTrue(isinstance(ks.parent, ComponentItem))
        self.assertEqual(ks.childNumber(),k)
        self.assertEqual(ks.node, inkd)
        self.assertEqual(ks.parent.node, vw.qdn)
        self.assertEqual(ks.node.nodeName(), "insertedkid")
        self.assertEqual(ks.parent, ci)
        


        vw.testModel = None

        inkd2 = vw.doc.createElement("insertedkid")
        self.assertTrue(not form.appendElement(inkd2, di))
        ci = di.internalPointer()
        



        form.view = None

        self.assertTrue(not form.appendElement(ki.internalPointer().node,di))

        self.assertEqual(form.result(),0)




if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
