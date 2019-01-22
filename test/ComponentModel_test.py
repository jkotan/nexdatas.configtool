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
# \file ComponentModelTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time

from PyQt5.QtCore import (
    Qt, QAbstractItemModel, QModelIndex,)
from PyQt5.QtXml import QDomDocument

from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.ComponentItem import ComponentItem


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

if sys.version_info > (3,):
    long = int
    unicode = str


# test fixture
class ComponentModelTest(unittest.TestCase):

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
        # action status
        self.performed = False

        try:
            self.__seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = long(time.time() * 256)
        #  self.__seed = 105186230414225794971485160270620812570

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            qdn.appendChild(kds[-1])

        allAttr = False
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        self.assertEqual(cd.parent, None)
        self.assertEqual(cd.childNumber(), 0)
        self.assertEqual(cd.node.nodeName(), "#document")

        ci = cd.child(0)
        self.assertEqual(ci.parent, cd)
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(), 0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            self.assertTrue(isinstance(ci.child(k), ComponentItem))
            self.assertTrue(isinstance(ci.child(k).parent, ComponentItem))
            self.assertEqual(ci.child(k).childNumber(), k)
            self.assertEqual(ci.child(k).node, kds[k])
            self.assertEqual(ci.child(k).parent.node, qdn)
            self.assertEqual(ci.child(k).node.nodeName(), "kid%s" % k)
            self.assertEqual(ci.child(k).parent, ci)

    # constructor test
    # \brief It tests default settings
    def test_headerData(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            qdn.appendChild(kds[-1])

        allAttr = False
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        hd = cm.headerData(0, Qt.Horizontal)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Name')
        hd = cm.headerData(0, Qt.Horizontal, Qt.DisplayRole)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Name')

        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Type')
        hd = cm.headerData(1, Qt.Horizontal, Qt.DisplayRole)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Type')

        hd = cm.headerData(2, Qt.Horizontal)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Value')
        hd = cm.headerData(2, Qt.Horizontal, Qt.DisplayRole)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Value')

        hd = cm.headerData(3, Qt.Horizontal)
        self.assertEqual(hd, None)
        hd = cm.headerData(3, Qt.Horizontal, Qt.DisplayRole)

        hd = cm.headerData(-1, Qt.Horizontal)
        self.assertEqual(hd, None)
        hd = cm.headerData(-1, Qt.Horizontal, Qt.DisplayRole)
        self.assertEqual(hd, None)

        cm.setAttributeView(True)

        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Attributes')
        hd = cm.headerData(1, Qt.Horizontal, Qt.DisplayRole)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Attributes')

        cm.setAttributeView(False)

        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Type')
        hd = cm.headerData(1, Qt.Horizontal, Qt.DisplayRole)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Type')

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        hd = cm.headerData(1, Qt.Horizontal)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Attributes')
        hd = cm.headerData(1, Qt.Horizontal, Qt.DisplayRole)
        self.assertTrue(isinstance(hd, str))
        self.assertEqual(hd, 'Attributes')

    # constructor test
    # \brief It tests default settings
    def test_data(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            qdn.appendChild(kds[-1])

        allAttr = False
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        dt = cm.data(QModelIndex())
        self.assertEqual(dt, None)

        for role in range(1, 5):
            dt = cm.data(cm.rootIndex, role)
            self.assertEqual(dt, None)

        dt = cm.data(cm.rootIndex)
        self.assertTrue(isinstance(dt, (unicode, str)))
        self.assertEqual(dt, '#document')

        dt = cm.data(cm.rootIndex, Qt.DisplayRole)
        self.assertTrue(isinstance(dt, (unicode, str)))
        self.assertEqual(dt, '#document')

    # constructor test
    # \brief It tests default settings
    def test_data_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = False
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        ci = cd.child(0)
        for n in range(nkids):
            # kd =
            ci.child(n)

            ki0 = cm.index(n, 0, di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, 'kid%s: myname%s' % (n, n))

            ki1 = cm.index(n, 1, di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), 'mytype%s' % n)

            ki2 = cm.index(n, 2, di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), '')

            ki2 = cm.index(n, -1, di)
            dt = cm.data(ki2)
            # self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, None)

            ki2 = cm.index(n, 3, di)
            dt = cm.data(ki2)
            # self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, None)

    def test_data_name_attr(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = False
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        ci = cd.child(0)
        for n in range(nkids):
            # kd =
            ci.child(n)

            cm.setAttributeView(False)

            ki0 = cm.index(n, 0, di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, 'kid%s: myname%s' % (n, n))

            ki1 = cm.index(n, 1, di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), 'mytype%s' % n)

            ki2 = cm.index(n, 2, di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), '')

            ki2 = cm.index(n, -1, di)
            dt = cm.data(ki2)
            # self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, None)

            ki2 = cm.index(n, 3, di)
            dt = cm.data(ki2)
            # self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, None)

            cm.setAttributeView(True)

            ki0 = cm.index(n, 0, di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, 'kid%s: myname%s' % (n, n))

            ki1 = cm.index(n, 1, di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, (unicode, str)))

            s1 = set(str(dt).strip().split(" "))
            s2 = set(('units="myunits%s" type="mytype%s" name="myname%s"' %
                      (n, n, n)).split(" "))

            self.assertEqual(s1, s2)

            ki2 = cm.index(n, 2, di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), '')

    def test_data_name_attr_true(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        ci = cd.child(0)
        for n in range(nkids):
            # kd =
            ci.child(n)

            ki0 = cm.index(n, 0, di)
            dt = cm.data(ki0)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, 'kid%s: myname%s' % (n, n))

            ki1 = cm.index(n, 1, di)
            dt = cm.data(ki1)
            self.assertTrue(isinstance(dt, (unicode, str)))
            s1 = set(str(dt).strip().split(" "))
            s2 = set(('units="myunits%s" type="mytype%s" name="myname%s"' %
                      (n, n, n)).split(" "))

            self.assertEqual(s1, s2)
            ki2 = cm.index(n, 2, di)
            dt = cm.data(ki2)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), '')

    def test_data_name_text(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

        # print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        self.assertEqual(cm.headerData(0, Qt.Vertical), None)

        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        # ci =
        cd.child(0)
        for n in range(nkids):
            allAttr = not allAttr
            cm.setAttributeView(allAttr)
            ki = cm.index(n, 0, di)

            ti = cm.index(0, 0, ki)
            dt = cm.data(ti)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(dt, '#text')

            ti = cm.index(0, 1, ki)
            dt = cm.data(ti)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), '')

            ti = cm.index(0, 2, ki)
            dt = cm.data(ti)
            self.assertTrue(isinstance(dt, (unicode, str)))
            self.assertEqual(str(dt).strip(), 'Text  %s' % n)

    def test_flags(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        self.assertEqual(cm.flags(QModelIndex()), Qt.ItemIsEnabled)
        ri = cm.rootIndex
        self.assertEqual(
            cm.flags(ri),
            Qt.ItemFlags(QAbstractItemModel.flags(cm, ri) |
                         Qt.ItemIsEnabled | Qt.ItemIsSelectable))
        di = cm.index(0, 0, ri)
        self.assertEqual(
            cm.flags(di),
            Qt.ItemFlags(QAbstractItemModel.flags(cm, di) |
                         Qt.ItemIsEnabled | Qt.ItemIsSelectable))
        for n in range(nkids):
            allAttr = not allAttr
            cm.setAttributeView(allAttr)
            ki = cm.index(n, 0, di)
            self.assertEqual(
                cm.flags(ki),
                Qt.ItemFlags(QAbstractItemModel.flags(cm, ki) |
                             Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            ki = cm.index(n, 1, di)
            self.assertEqual(
                cm.flags(ki),
                Qt.ItemFlags(QAbstractItemModel.flags(cm, ki) |
                             Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            ki = cm.index(n, 2, di)
            self.assertEqual(
                cm.flags(ki),
                Qt.ItemFlags(QAbstractItemModel.flags(cm, ki) |
                             Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            ki = cm.index(n, 3, di)
            self.assertEqual(cm.flags(ki), Qt.ItemIsEnabled)

            ki = cm.index(n, 0, di)
            ti = cm.index(0, 0, ki)
            self.assertEqual(
                cm.flags(ti),
                Qt.ItemFlags(QAbstractItemModel.flags(cm, ti) |
                             Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            ti = cm.index(0, 1, ki)
            self.assertEqual(
                cm.flags(ti),
                Qt.ItemFlags(QAbstractItemModel.flags(cm, ti) |
                             Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            ti = cm.index(0, 2, ki)
            self.assertEqual(
                cm.flags(ti),
                Qt.ItemFlags(QAbstractItemModel.flags(cm, ti) |
                             Qt.ItemIsEnabled | Qt.ItemIsSelectable))
            ti = cm.index(0, 3, ki)
            self.assertEqual(cm.flags(ti), Qt.ItemIsEnabled)

    def test_index(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        self.assertTrue(isinstance(di, QModelIndex))
        self.assertEqual(di.row(), 0)
        self.assertEqual(di.column(), 0)
        self.assertEqual(di.internalPointer().node, qdn)
        self.assertEqual(di.internalPointer().parent.node, doc)

        iv = cm.index(0, 0)
        self.assertTrue(isinstance(iv, QModelIndex))
        self.assertEqual(iv.row(), 0)
        self.assertEqual(iv.column(), 0)
        self.assertEqual(iv, di)
        self.assertEqual(iv.internalPointer(), di.internalPointer())

        iv = cm.index(0, 0, QModelIndex())
        self.assertTrue(isinstance(iv, QModelIndex))
        self.assertEqual(iv.row(), 0)
        self.assertEqual(iv.column(), 0)
        self.assertEqual(iv, di)
        self.assertEqual(iv.internalPointer(), di.internalPointer())

        for n in range(nkids):
            allAttr = not allAttr
            cm.setAttributeView(allAttr)

            ki = cm.index(n, 0, di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(), n)
            self.assertEqual(ki.column(), 0)
            self.assertEqual(ki.internalPointer().node, kds[n])
            self.assertEqual(ki.internalPointer().parent.node, qdn)

            ki = cm.index(n, 1, di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(), n)
            self.assertEqual(ki.column(), 1)
            self.assertEqual(ki.internalPointer().node, kds[n])
            self.assertEqual(ki.internalPointer().parent.node, qdn)

            ki = cm.index(n, 2, di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(), n)
            self.assertEqual(ki.column(), 2)
            self.assertEqual(ki.internalPointer().node, kds[n])
            self.assertEqual(ki.internalPointer().parent.node, qdn)

            ki = cm.index(n, 3, di)
            self.assertTrue(isinstance(ki, QModelIndex))
            self.assertEqual(ki.row(), -1)
            self.assertEqual(ki.column(), -1)
            self.assertEqual(ki.internalPointer(), None)

            ki = cm.index(n, 0, di)
            ti = cm.index(0, 0, ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(), 0)
            self.assertEqual(ti.column(), 0)
            self.assertEqual(ti.internalPointer().node, tkds[n])
            self.assertEqual(ti.internalPointer().parent.node, kds[n])

            ti = cm.index(0, 1, ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(), 0)
            self.assertEqual(ti.column(), 1)
            self.assertEqual(ti.internalPointer().node, tkds[n])
            self.assertEqual(ti.internalPointer().parent.node, kds[n])

            ti = cm.index(0, 2, ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(), 0)
            self.assertEqual(ti.column(), 2)
            self.assertEqual(ti.internalPointer().node, tkds[n])
            self.assertEqual(ti.internalPointer().parent.node, kds[n])

            ti = cm.index(0, 3, ki)
            self.assertTrue(isinstance(ti, QModelIndex))
            self.assertEqual(ti.row(), -1)
            self.assertEqual(ti.column(), -1)
            self.assertEqual(ti.internalPointer(), None)

    def test_parent(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        ri = cm.rootIndex
        pri = cm.parent(ri)
        self.assertTrue(isinstance(pri, QModelIndex))
        self.assertEqual(pri.row(), -1)
        self.assertEqual(pri.column(), -1)
        self.assertEqual(pri.internalPointer(), None)

        # avoids showing #document
        di = cm.index(0, 0, ri)
        pdi = cm.parent(di)
        self.assertTrue(isinstance(pdi, QModelIndex))
        self.assertEqual(pdi.row(), -1)
        self.assertEqual(pdi.column(), -1)
        self.assertEqual(pdi.internalPointer(), None)

        iv = cm.index(0, 0)
        piv = cm.parent(iv)
        self.assertTrue(isinstance(piv, QModelIndex))
        self.assertEqual(pdi.row(), -1)
        self.assertEqual(pdi.column(), -1)
        self.assertEqual(pdi.internalPointer(), None)

        for n in range(nkids):
            allAttr = not allAttr
            cm.setAttributeView(allAttr)

            ki = cm.index(n, 0, di)
            pki = cm.parent(ki)
            self.assertEqual(pki, di)

            ki = cm.index(n, 1, di)
            pki = cm.parent(ki)
            self.assertEqual(pki, di)

            ki = cm.index(n, 2, di)
            pki = cm.parent(ki)
            self.assertEqual(pki, di)

            ki = cm.index(n, 3, di)
            pki = cm.parent(ki)
            self.assertTrue(isinstance(pki, QModelIndex))
            self.assertEqual(pki.row(), -1)
            self.assertEqual(pki.column(), -1)
            self.assertEqual(pki.internalPointer(), None)

            ki = cm.index(n, 0, di)
            ti = cm.index(0, 0, ki)
            pti = cm.parent(ti)
            self.assertEqual(pti, ki)

            ti = cm.index(0, 1, ki)
            pti = cm.parent(ti)
            self.assertEqual(pti, ki)

            ti = cm.index(0, 2, ki)
            pti = cm.parent(ti)
            self.assertEqual(pti, ki)

            ti = cm.index(0, 3, ki)
            pti = cm.parent(ti)
            self.assertTrue(isinstance(pti, QModelIndex))
            self.assertEqual(pti.row(), -1)
            self.assertEqual(pti.column(), -1)
            self.assertEqual(pti.internalPointer(), None)

    def test_rowCount(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        ri = cm.rootIndex
        self.assertEqual(cm.rowCount(ri), 1)

        # avoids showing #document
        di = cm.index(0, 0, ri)
        self.assertEqual(cm.rowCount(di), nkids)

        iv = cm.index(0, 0)
        self.assertEqual(cm.rowCount(iv), nkids)

        for n in range(nkids):
            allAttr = not allAttr
            cm.setAttributeView(allAttr)

            ki = cm.index(n, 0, di)
            self.assertEqual(cm.rowCount(ki), 1)

            ki = cm.index(n, 1, di)
            self.assertEqual(cm.rowCount(ki), 0)

            ki = cm.index(n, 2, di)
            self.assertEqual(cm.rowCount(ki), 0)

            # invalid index
            ki = cm.index(n, 3, di)
            self.assertEqual(cm.rowCount(ki), 1)

            ki = cm.index(n, 0, di)
            ti = cm.index(0, 0, ki)
            self.assertEqual(cm.rowCount(ti), 0)

            ti = cm.index(0, 1, ki)
            self.assertEqual(cm.rowCount(ti), 0)

            ti = cm.index(0, 2, ki)
            self.assertEqual(cm.rowCount(ti), 0)

            ti = cm.index(0, 3, ki)
            self.assertEqual(cm.rowCount(ti), 1)

    def test_columnCount(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        ri = cm.rootIndex
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0, 0, ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0, 0)
        self.assertEqual(cm.columnCount(iv), 3)

        for n in range(nkids):
            allAttr = not allAttr
            cm.setAttributeView(allAttr)

            ki = cm.index(n, 0, di)
            self.assertEqual(cm.columnCount(ki), 3)

            ki = cm.index(n, 1, di)
            self.assertEqual(cm.columnCount(ki), 3)

            ki = cm.index(n, 2, di)
            self.assertEqual(cm.columnCount(ki), 3)

            # invalid index
            ki = cm.index(n, 3, di)
            self.assertEqual(cm.columnCount(ki), 3)

            ki = cm.index(n, 0, di)
            ti = cm.index(0, 0, ki)
            self.assertEqual(cm.columnCount(ti), 3)

            ti = cm.index(0, 1, ki)
            self.assertEqual(cm.columnCount(ti), 3)

            ti = cm.index(0, 2, ki)
            self.assertEqual(cm.columnCount(ti), 3)

            ti = cm.index(0, 3, ki)
            self.assertEqual(cm.columnCount(ti), 3)

    def test_insertItem(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        ri = cm.rootIndex
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0, 0, ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0, 0)
        self.assertEqual(cm.columnCount(iv), 3)

        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(), 0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(), k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" % k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(), 0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(
                ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        insd = self.__rnd.randint(0, nkids - 1)
        inkd = doc.createElement("insertedkid")
        self.assertTrue(not cm.insertItem(insd, inkd, QModelIndex()))

        self.assertTrue(cm.insertItem(insd, inkd, di))

        for k in range(nkids+1):
            ks = ci.child(k)
            if k == insd:
                self.assertTrue(isinstance(ks, ComponentItem))
                self.assertTrue(isinstance(ks.parent, ComponentItem))
                self.assertEqual(ks.childNumber(), k)
                self.assertEqual(ks.node, inkd)
                self.assertEqual(ks.parent.node, qdn)
                self.assertEqual(ks.node.nodeName(), "insertedkid")
                self.assertEqual(ks.parent, ci)
                continue
            kk = k if k < insd else k - 1
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(), k)
            self.assertEqual(ks.node, kds[kk])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" % kk)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(), 0)
            self.assertEqual(ks.child(0).node, tkds[kk])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(
                ks.child(0).node.toText().data(), '\nText\n %s\n' % kk)
            self.assertEqual(ks.child(0).parent, ks)

    def test_appendItem(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        ri = cm.rootIndex
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0, 0, ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0, 0)
        self.assertEqual(cm.columnCount(iv), 3)

        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(), 0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(), k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" % k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(), 0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(
                ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        inkd = doc.createElement("insertedkid")
        self.assertTrue(not cm.appendItem(inkd, QModelIndex()))

        self.assertTrue(cm.appendItem(inkd, di))

        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(), k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" % k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(), 0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(
                ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)
#            print k, ks.childNumber()
        k = nkids
        ks = ci.child(k)
        self.assertTrue(isinstance(ks, ComponentItem))
        self.assertTrue(isinstance(ks.parent, ComponentItem))
        self.assertEqual(ks.childNumber(), k)
        self.assertEqual(ks.node, inkd)
        self.assertEqual(ks.parent.node, qdn)
        self.assertEqual(ks.node.nodeName(), "insertedkid")
        self.assertEqual(ks.parent, ci)

    def test_removeItem(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)
        nkids = self.__rnd.randint(1, 10)
        kds = []
        tkds = []
        for n in range(nkids):
            kds.append(doc.createElement("kid%s" % n))
            kds[-1].setAttribute("name", "myname%s" % n)
            kds[-1].setAttribute("type", "mytype%s" % n)
            kds[-1].setAttribute("units", "myunits%s" % n)
            qdn.appendChild(kds[-1])
            tkds.append(doc.createTextNode("\nText\n %s\n" % n))
            kds[-1].appendChild(tkds[-1])

#        print doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        self.assertTrue(isinstance(cm, QAbstractItemModel))
        self.assertTrue(isinstance(cm.rootIndex, QModelIndex))
        cd = cm.rootIndex.internalPointer()
        self.assertTrue(isinstance(cd, ComponentItem))
        self.assertEqual(cm.rootIndex.row(), 0)
        self.assertEqual(cm.rootIndex.column(), 0)

        ri = cm.rootIndex
        self.assertEqual(cm.columnCount(ri), 3)

        # avoids showing #document
        di = cm.index(0, 0, ri)
        self.assertEqual(cm.columnCount(di), 3)

        iv = cm.index(0, 0)
        self.assertEqual(cm.columnCount(iv), 3)

        ci = di.internalPointer()
        self.assertEqual(ci.node, qdn)
        self.assertEqual(ci.childNumber(), 0)
        self.assertEqual(ci.node.nodeName(), nname)
        for k in range(nkids):
            ks = ci.child(k)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(), k)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" % k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(), 0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(
                ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)

        rmvd = self.__rnd.randint(0, nkids - 1)
        # rmkd =
        ci.child(rmvd)
        self.assertTrue(not cm.removeItem(rmvd, QModelIndex()))

        self.assertTrue(cm.removeItem(rmvd, di))

        for k in range(nkids):
            if k == rmvd:
                continue
            kk = k if k < rmvd else k - 1
            ks = ci.child(kk)
            self.assertTrue(isinstance(ks, ComponentItem))
            self.assertTrue(isinstance(ks.parent, ComponentItem))
            self.assertEqual(ks.childNumber(), kk)
            self.assertEqual(ks.node, kds[k])
            self.assertEqual(ks.parent.node, qdn)
            self.assertEqual(ks.node.nodeName(), "kid%s" % k)
            self.assertEqual(ks.parent, ci)
            self.assertTrue(isinstance(ks.child(0), ComponentItem))
            self.assertTrue(isinstance(ks.child(0).parent, ComponentItem))
            self.assertEqual(ks.child(0).childNumber(), 0)
            self.assertEqual(ks.child(0).node, tkds[k])
            self.assertEqual(ks.child(0).parent.node, ks.node)
            self.assertEqual(ks.child(0).node.nodeName(), "#text")
            self.assertEqual(
                ks.child(0).node.toText().data(), '\nText\n %s\n' % k)
            self.assertEqual(ks.child(0).parent, ks)


if __name__ == '__main__':
    unittest.main()
