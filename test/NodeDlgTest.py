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

from ndtsconfigtool.DomTools import DomTools




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

    def replaceText(self, node, index,  model, text):
        self.stack.append("replaceText")
        self.stack.append(node)
        self.stack.append(index)
        self.stack.append(model)
        self.stack.append(text)

        
    

class TestView(object):
    def __init__(self):
        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 
         
        self.__rnd = random.Random(self.__seed)
        print "VIEW SEED", self.__seed

        self.sindex = None
        self.eindex = None


        self.doc = QDomDocument()
        self.nname = "definition"
        self.qdn = self.doc.createElement(self.nname)
        self.doc.appendChild(self.qdn)
        self.nkids =  self.__rnd.randint(1, 10) 
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
    ##  Qt-application
    app = None

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
         
        self.__rnd = random.Random(self.__seed)


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        
        print "SEED =", self.__seed 
        
        if not NodeDlgTest.app:
            NodeDlgTest.app = QApplication([])


    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."


    def checkMessageBox(self):
        self.assertEqual(QApplication.activeWindow(),None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()

    def myAction(self):
        self.performed = True

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
        self.assertTrue(isinstance(form.dts, DomTools))


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
        self.assertTrue(isinstance(form.dts, DomTools))

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
        form.show()
        self.assertEqual(form.connectExternalActions(),None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems, [])
        self.assertTrue(isinstance(form.ui,Ui_NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertTrue(isinstance(form.dts, DomTools))


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
    def test_replaceText_notext(self):
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
        form.dts = dts
        form.node =vw.qdn

        form.replaceText(di)
        

        self.assertEqual(dts.stack[0],"replaceText")
        self.assertEqual(dts.stack[1],vw.qdn)
        self.assertEqual(dts.stack[2],di)
        self.assertEqual(dts.stack[3],vw.model())
        self.assertEqual(dts.stack[4],None)


        dts.stack = []
        
        text = "My Supper Text"
        form.replaceText(di,text)
        

        self.assertEqual(dts.stack[0],"replaceText")
        self.assertEqual(dts.stack[1],vw.qdn)
        self.assertEqual(dts.stack[2],di)
        self.assertEqual(dts.stack[3],vw.model())
        self.assertEqual(dts.stack[4],text)

        self.assertEqual(form.result(),0)
        


if __name__ == '__main__':
    unittest.main()
