#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file ComponentItemTest.py
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

from PyQt4.QtXml import QDomNode, QDomDocument

from nxsconfigtool.ComponentItem import ComponentItem



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class ComponentItemTest(unittest.TestCase):

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
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        qdn = QDomNode()
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        ci = ComponentItem(qdn)

        self.assertEqual(ci.node,qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.child(0),None)
        self.assertEqual(ci.child(1),None)


    ## constructor test
    # \brief It tests default settings
    def test_constructor_with_dom(self):
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


        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
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
    def test_constructor_with_dom_nested(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        gkds = []
        ngks = [ ]
        
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])
            ngkids =  self.__rnd.randint(1, 10) 
            gkds.append([])
            ngks.append(ngkids)
            for g in range(ngkids):
                gkds[n].append(doc.createElement("grandkid%s" %  g))
                kds[-1].appendChild(gkds[n][-1])
            

#        print doc.toString()
                
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
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
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)
            self.assertEqual(ks.child(ngks[k]),None)
            self.assertEqual(ks.child(-1),None)
        self.assertEqual(ci.child(nkids),None)
        self.assertEqual(ci.child(-1),None)
                



    ## constructor test
    # \brief It tests default settings
    def test_constructor_with_dom_nested_reverse(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 10) 
        kds = []
        gkds = []
        ngks = [ ]
        
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])
            ngkids =  self.__rnd.randint(1, 10) 
            gkds.append([])
            ngks.append(ngkids)
            for g in range(ngkids):
                gkds[n].append(doc.createElement("grandkid%s" %  g))
                kds[-1].appendChild(gkds[n][-1])
            

#        print doc.toString()
                
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(),0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in reversed(range(nkids)):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)
            self.assertEqual(ks.child(ngks[k]),None)
            self.assertEqual(ks.child(-1),None)
        self.assertEqual(ci.child(nkids),None)
        self.assertEqual(ci.child(-1),None)
                



    ## constructor test
    # \brief It tests default settings
    def test_constructor_remove_kids(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 20) 
        kds = []
        gkds = []
        ngks = [ ]
        
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])
            ngkids =  self.__rnd.randint(1, 20) 
            gkds.append([])
            ngks.append(ngkids)
            for g in range(ngkids):
                gkds[n].append(doc.createElement("grandkid%s" %  g))
                kds[-1].appendChild(gkds[n][-1])
            

#        print doc.toString()
                
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
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
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)
                

        rmvd =  self.__rnd.randint(1,nkids) - 1
        kd = ci.child(rmvd)
        self.assertEqual(ci.removeChildren(rmvd, 1), True)
        self.assertEqual(ci.removeChildren(-1, 1), False)
        self.assertEqual(ci.removeChildren(nkids, 1), False)
        qdn.removeChild(kd.node)


        for k in range(nkids):
            if k == rmvd:
                continue
            kk = k if k<rmvd else k-1
            ks = ci.child(kk)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),kk)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)






    ## constructor test
    # \brief It tests default settings
    def test_constructor_remove_more_kids(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 20) 
        kds = []
        gkds = []
        ngks = [ ]
        
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])
            ngkids =  self.__rnd.randint(1, 20) 
            gkds.append([])
            ngks.append(ngkids)
            for g in range(ngkids):
                gkds[n].append(doc.createElement("grandkid%s" %  g))
                kds[-1].appendChild(gkds[n][-1])
            

#        print doc.toString()
                
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
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
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)
                

        rmvd =  self.__rnd.randint(0, nkids-1) 
        nrm = self.__rnd.randint(1,nkids-rmvd) 
        kd = []
        for r in range(nrm):
            kd.append(ci.child(rmvd+r))
        self.assertEqual(ci.removeChildren(rmvd, nrm), True)
        for r in range(nrm):
            qdn.removeChild(kd[r].node)


        for k in range(nkids):
            if k >= rmvd and k <= rmvd + nrm:
                continue
            kk = k if k<rmvd else k-nrm
            ks = ci.child(kk)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),kk)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  k)
            self.assertEqual(ks.parent, ci)
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)



    ## constructor test
    # \brief It tests default settings
    def test_constructor_insert_kids(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 5) 
        kds = []
        gkds = []
        ngks = [ ]
        
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])
            ngkids =  self.__rnd.randint(1, 5) 
            gkds.append([])
            ngks.append(ngkids)
            for g in range(ngkids):
                gkds[n].append(doc.createElement("grandkid%s" %  g))
                kds[-1].appendChild(gkds[n][-1])
            

#        print doc.toString()
                
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
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
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)
                

        insd =  self.__rnd.randint(0,nkids) 
        inkd = doc.createElement("insertedkid")
        if insd == nkids:
            qdn.insertAfter(inkd, ci.child(nkids-1).node)
        else:
            qdn.insertBefore(inkd, ci.child(insd).node)

        self.assertEqual(ci.insertChildren(insd, 1), True)
        self.assertEqual(ci.insertChildren(-1, 1), False)
        self.assertEqual(ci.insertChildren(nkids+2, 1), False)

        
        for k in range(nkids):
            if k == insd:
                ks = ci.child(k) 
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node, inkd)
                self.assertEqual(ks.parent.node, qdn)
                self.assertEqual(ks.node.nodeName(), "insertedkid")
                self.assertEqual(ks.parent, ci)
                continue
            kk = k if k < insd else k-1
            ks = ci.child(k) 
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[kk])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  kk)
            self.assertEqual(ks.parent, ci)
            for g in range(ngks[kk]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[kk][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)




    ## constructor test
    # \brief It tests default settings
    def test_constructor_insert_more_kids(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids =  self.__rnd.randint(1, 5) 
        kds = []
        gkds = []
        ngks = [ ]
        
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" %  n))
            qdn.appendChild(kds[-1])
            ngkids =  self.__rnd.randint(1, 5) 
            gkds.append([])
            ngks.append(ngkids)
            for g in range(ngkids):
                gkds[n].append(doc.createElement("grandkid%s" %  g))
                kds[-1].appendChild(gkds[n][-1])
            

                
        ci = ComponentItem(qdn)

        self.assertEqual(ci.parent, None)
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
            for g in range(ngks[k]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[k][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)
                

        insd =  self.__rnd.randint(0,nkids) 
        nin =  self.__rnd.randint(1, 5) 
        inkd = []
        for n in range(nin):
            inkd.append(doc.createElement("insertedkid%s"% n))

            if insd == nkids+n:
                if n == 0:
                    qdn.insertAfter(inkd[n], ci.child(nkids-1).node)
                else:
                    qdn.insertAfter(inkd[n],  inkd[n-1])
            else:
                qdn.insertBefore(inkd[n], ci.child(insd).node)

        self.assertEqual(ci.insertChildren(insd, nin), True)

        
        for k in range(nkids):
            if k >= insd and k < insd + nin:
                mnin =  k - insd 
                ks = ci.child(k) 
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(),k)
                self.assertEqual(ks.node, inkd[mnin])
                self.assertEqual(ks.parent.node, qdn)
                self.assertEqual(ks.node.nodeName(), "insertedkid%s" % mnin)
                self.assertEqual(ks.parent, ci)
                continue
            kk = k if k < insd else k-nin
            ks = ci.child(k) 
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(),k)
            self.assertEqual(ks.node, kds[kk])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" %  kk)
            self.assertEqual(ks.parent, ci)
            for g in range(ngks[kk]):
                self.assertTrue(isinstance(ks.child(g), ComponentItem))
                self.assertTrue(isinstance(ks.child(g).parent, ComponentItem))
                self.assertEqual(ks.child(g).childNumber(),g)
                self.assertEqual(ks.child(g).node, gkds[kk][g])
                self.assertEqual(ks.child(g).parent.node, ks.node)
                self.assertEqual(ks.child(g).node.nodeName(), "grandkid%s" %  g)
                self.assertEqual(ks.child(g).parent, ks)

if __name__ == '__main__':
    unittest.main()
