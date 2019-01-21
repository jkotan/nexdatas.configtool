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
# \file DefinitionDlgTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import (QApplication, QMessageBox, QTableWidgetItem,
                             QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtXml import QDomDocument

from nxsconfigtool.DefinitionDlg import DefinitionDlg
from nxsconfigtool.ComponentModel import ComponentModel
from nxsconfigtool.AttributeDlg import AttributeDlg
from nxsconfigtool.NodeDlg import NodeDlg

# from nxsconfigtool.ui.ui_definitiondlg import Ui_DefinitionDlg
from nxsconfigtool.DomTools import DomTools

#  Qt-application
app = None

if sys.version_info > (3,):
    unicode = str
    long = int

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


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


# test fixture
class DefinitionDlgTest(unittest.TestCase):

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

        # action status
        self.performed = False

        try:
            self.__seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = long(time.time() * 256)
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

    def checkMessageBox(self):
        #   self.assertEqual(QApplication.activeWindow(), None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        #   print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()

    def rmAttributeWidget(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
#        print "CLASS", mb
#        print "CLASS2", aw
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.Yes), Qt.LeftButton)

    def rmAttributeWidgetClose(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
        self.text = mb.text()
        self.title = mb.windowTitle()

        QTest.mouseClick(mb.button(QMessageBox.No), Qt.LeftButton)

    def attributeWidget(self):
        # aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(), self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(), self.avalue)

        mb.accept()

    def attributeWidgetClose(self):
        # aw =
        QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, AttributeDlg))

        QTest.keyClicks(mb.ui.nameLineEdit, self.aname)
        self.assertEqual(mb.ui.nameLineEdit.text(), self.aname)
        QTest.keyClicks(mb.ui.valueLineEdit, self.avalue)
        self.assertEqual(mb.ui.valueLineEdit.text(), self.avalue)

#        mb.close()
        mb.reject()

#        mb.accept()

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertTrue(isinstance(form, NodeDlg))
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        self.assertEqual(form.replaceText,
                         super(DefinitionDlg, form).replaceText)
        self.assertEqual(form.removeElement,
                         super(DefinitionDlg, form).removeElement)
        self.assertEqual(form.replaceElement,
                         super(DefinitionDlg, form).replaceElement)
        self.assertEqual(form.appendElement,
                         super(DefinitionDlg, form).appendElement)
        self.assertEqual(form.reset, super(DefinitionDlg, form).reset)

    # constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute",
                          "link", "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())

        self.assertTrue(form.ui.applyPushButton.isEnabled())
        self.assertTrue(form.ui.resetPushButton.isEnabled())

        name = "myname"
        content = "$components.default"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(), name)
        QTest.keyClicks(form.ui.contentTextEdit, content)
        self.assertEqual(form.ui.contentTextEdit.toPlainText(), content)

        self.assertTrue(bool(form.ui.nameLineEdit.text()))
        self.assertTrue(bool(form.ui.contentTextEdit.toPlainText()))

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        #        form.apply()
        #        self.assertEqual(form.name, name)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_updateForm(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute",
                          "link", "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        name = "myname"
        content = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr": "myvalue", "myattr2": "myvalue2",
                      "myattr3": "myvalue3"}

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.name = name

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.updateForm(), None)

        self.assertEqual(form.ui.nameLineEdit.text(), name)
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.ui.nameLineEdit.setText("")

        form.name = ""
        form.content = content

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertEqual(form.ui.contentTextEdit.toPlainText(), content)
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.ui.contentTextEdit.setText("")

        form.doc = doc
        form.content = ""

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.updateForm(), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        form.ui.docTextEdit.setText("")

        form.name = name
        form.doc = doc
        form.content = content
        form.attributes = attributes

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.updateForm(), None)

        self.assertEqual(form.ui.contentTextEdit.toPlainText(), content)
        self.assertEqual(form.ui.nameLineEdit.text(), name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_getState(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(
            form.subItems,
            ["group", "field", "attribute", "link", "component", "doc",
             "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        name = "myname"
        content = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr": "myvalue", "myattr2": "myvalue2",
                      "myattr3": "myvalue3"}

        self.assertEqual(form.getState(), ('', '', '', {}))

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.name = name

        self.assertEqual(form.getState(), (name, '', '', {}))

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.name = ""
        form.content = content

        self.assertEqual(form.getState(), ('', content, '', {}))

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.doc = doc
        form.content = ""

        self.assertEqual(form.getState(), ('', '', doc, {}))

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.doc = ""
        form.content = ""

        form.attributes = attributes
        state = form.getState()

        self.assertEqual(state[0], '')
        self.assertEqual(state[1], '')
        self.assertEqual(state[2], '')
        self.assertEqual(len(state), 4)
        self.assertEqual(len(state[3]), len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[3][at])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form.name = name
        form.doc = doc
        form.content = content
        form.attributes = attributes

        state = form.getState()

        self.assertEqual(state[0], name)
        self.assertEqual(state[1], content)
        self.assertEqual(state[2], doc)
        self.assertEqual(len(state), 4)
        self.assertTrue(state[3] is not attributes)
        self.assertEqual(len(state[3]), len(attributes))
        for at in attributes:
            self.assertEqual(attributes[at], state[3][at])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setState(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(
            form.subItems,
            ["group", "field", "attribute",
             "link", "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        name = "myname"
        content = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr": "myvalue", "myattr2": "myvalue2",
                      "myattr3": "myvalue3"}

        self.assertEqual(form.setState(['', '', '', {}]), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.setState([name, '', '', {}]), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.name, name)
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})

        form.name = ""

        self.assertEqual(form.setState(['', content, '', {}]), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())
        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, content)
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})

        form.content = ""

        self.assertEqual(form.setState(['', '', doc, {}]), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.attributes, {})

        form.doc = ""

#        form.attributes = attributes
        self.assertEqual(form.setState(['', '', '', attributes]), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, attributes)
        self.assertTrue(form.attributes is not attributes)

        self.assertEqual(form.setState([name, content, doc, attributes]), None)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.name, name)
        self.assertEqual(form.content, content)
        self.assertEqual(form.doc, doc)
        self.assertEqual(form.attributes, attributes)
        self.assertTrue(form.attributes is not attributes)

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        form.createGUI()

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        name = "myname"
        content = "NXEntry"
        doc = "My documentation: \n ble ble ble "
        attributes = {"myattr": "myvalue", "myattr2": "myvalue2",
                      "myattr3": "myvalue3"}

        form = DefinitionDlg()
        form.show()
        form.createGUI()

        self.assertEqual(form.ui.nameLineEdit.text(), '')
        self.assertEqual(form.ui.contentTextEdit.toPlainText(), '')
        self.assertEqual(form.ui.docTextEdit.toPlainText(), '')

        form = DefinitionDlg()
        form.show()
        form.name = name

        form.createGUI()

        self.assertEqual(form.ui.nameLineEdit.text(), name)
        self.assertEqual(form.ui.contentTextEdit.toPlainText(), '')
        self.assertEqual(form.ui.docTextEdit.toPlainText(), '')
        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        form = DefinitionDlg()
        form.show()
        form.content = content

        form.createGUI()

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertEqual(form.ui.contentTextEdit.toPlainText(), content)
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        form = DefinitionDlg()
        form.show()
        form.doc = doc

        form.createGUI()

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        form = DefinitionDlg()
        form.show()
        form.name = name
        form.doc = doc
        form.content = content
        form.attributes = attributes

        form.createGUI()

        self.assertEqual(form.ui.contentTextEdit.toPlainText(), content)
        self.assertEqual(form.ui.nameLineEdit.text(), name)
        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        self.assertEqual(form.ui.docTextEdit.toPlainText(), doc)

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)

#        form.apply()
#        self.assertEqual(form.name, name)
#        self.assertEqual(form.content, content)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.attributes, {u'shortname': u'mynshort%s' % nn,
                              u'type': u'mytype%s' % nn,
                              u'unit': u'myunits%s' % nn})
        self.assertEqual(
            form.subItems,
            ["group", "field", "attribute", "link", "component", "doc",
             "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_parameter(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
#        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(
            form.subItems,
            ["group", "field", "attribute", "link", "component", "doc",
             "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(
            form.subItems,
            ["group", "field", "attribute", "link", "component", "doc",
             "symbols"])

        form.setFromNode(qdn)
        self.assertEqual(form.node, qdn)

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(
            form.attributes,
            {u'shortname': u'mynshort%s' % nn,
             u'type': u'mytype%s' % nn, u'unit': u'myunits%s' % nn})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_noNode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
#        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

    # constructor test
    # \brief It tests default settings
    def test_setFromNode_clean(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        # dks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        doc.appendChild(qdn)

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

    # constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn,
                      u'type': u'mytype%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        form.populateAttributes()

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item, None)

    # constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_wrong(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        attributes = {
            u'shortname': u'mynshort%s' % nn, u'type': u'mytype%s' % nn,
            u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        form.populateAttributes("ble")

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item, None)

    # constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn,
                      u'type': u'mytype%s' % nn, u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        na = self.__rnd.randint(0, len(attributes)-1)
        sel = attributes.keys()[na]
        form.populateAttributes(sel)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)

        self.assertEqual(item.data(Qt.UserRole), sel)

    # constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_addAttribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute",
                          "link", "component", "doc", "symbols"])

        form.setFromNode()

        attributes = {u'shortname': u'mynshort%s' % nn,
                      u'type': u'mytype%s' % nn,
                      u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        na = self.__rnd.randint(0, len(attributes)-1)
        sel = attributes.keys()[na]
        form.populateAttributes(sel)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)

        self.assertEqual(item.data(Qt.UserRole), sel)

        self.aname = "addedAttribute"
        self.avalue = "addedAttributeValue"

        QTimer.singleShot(10, self.attributeWidgetClose)
        QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)

        self.assertEqual(item.data(Qt.UserRole), sel)

        self.aname = "addedAttribute"
        self.avalue = "addedAttributeValue"

        QTimer.singleShot(10, self.attributeWidget)
        QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes)+1)
        for i in range(len(attributes)+1):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            if k in attributes.keys():
                self.assertEqual(it2.text(), attributes[k])
            else:
                self.assertEqual(it2.text(), self.avalue)

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item.data(Qt.UserRole), self.aname)

    # constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_removeAttribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        qdn.setAttribute("logname", "mynlong%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        form.setFromNode()

        attributes = {u'type': u'mytype%s' % nn,
                      u'shortname': u'mynshort%s' % nn,
                      u'logname': u'mynlong%s' % nn,
                      u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link",
                          "component", "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(form.ui.attributeTableWidget.rowCount(), 0)

        na = self.__rnd.randint(0, len(attributes)-1)
        sel = attributes.keys()[na]
        form.populateAttributes(sel)

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)

        self.assertEqual(item.data(Qt.UserRole), sel)

        aname = self.__rnd.choice(attributes.keys())
        # avalue =
        attributes[aname]

        form.populateAttributes(aname)

        #        QTimer.singleShot(10, self.rmAttributeWidget)
        QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)

        #        self.assertEqual(self.text, "Remove attribute: %s = ' %s'" %
        #   (aname, avalue))

        self.assertEqual(form.ui.attributeTableWidget.columnCount(), 2)
        self.assertEqual(
            form.ui.attributeTableWidget.rowCount(), len(attributes)-1)
        for i in range(len(attributes)-1):
            it = form.ui.attributeTableWidget.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = form.ui.attributeTableWidget.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = form.ui.attributeTableWidget.item(
            form.ui.attributeTableWidget.currentRow(), 0)
        self.assertEqual(item, None)

    # constructor test
    # \brief It tests default settings
    def test_populateAttribute_setFromNode_selected_tableItemChanged(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        qdn.setAttribute("logname", "mynlong%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link",
                          "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.createGUI()

        atw = form.ui.attributeTableWidget
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link",
                          "component", "doc", "symbols"])

        form.setFromNode()

        attributes = {u'type': u'mytype%s' % nn, u'shortname':
                      u'mynshort%s' % nn, u'logname': u'mynlong%s' % nn,
                      u'unit': u'myunits%s' % nn}

        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            "".join(["\nText\n %s\n" % n for n in range(ndcs)]).strip())
        self.assertEqual(form.attributes, attributes)
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])

        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.contentTextEdit.toPlainText())
        self.assertTrue(not form.ui.docTextEdit.toPlainText())

        self.assertEqual(atw.columnCount(), 2)
        self.assertEqual(atw.rowCount(), 0)

        na = self.__rnd.randint(0, len(attributes)-1)
        sel = attributes.keys()[na]
        form.populateAttributes(sel)

        self.assertEqual(atw.columnCount(), 2)
        self.assertEqual(atw.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = atw.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        item = atw.item(atw.currentRow(), 0)
        self.assertEqual(item.data(Qt.UserRole), sel)

        ch = self.__rnd.randint(0, len(attributes)-1)
        atw.setCurrentCell(ch, 0)
        item = atw.item(atw.currentRow(), 0)
        aname = str(item.data(Qt.UserRole))

        it = QTableWidgetItem(unicode(aname))
        it.setData(Qt.DisplayRole, (aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, (aname))

        atw.setCurrentCell(ch, 0)

        QTimer.singleShot(10, self.checkMessageBox)
        atw.setItem(ch, 0, it)
        self.assertEqual(
            self.text,
            "To change the attribute name, please remove the attribute "
            "and add the new one")

        # avalue =
        attributes[str(aname)]

        self.assertEqual(atw.columnCount(), 2)
        self.assertEqual(atw.rowCount(), len(attributes))
        for i in range(len(attributes)):
            it = atw.item(i, 0)
            k = str(it.text())
            self.assertTrue(k in attributes.keys())
            it2 = atw.item(i, 1)
            self.assertEqual(it2.text(), attributes[k])

        it = QTableWidgetItem(unicode(aname))
        it.setData(Qt.DisplayRole, (aname+"_"+attributes[aname]))
        it.setData(Qt.UserRole, (aname))

        atw.setCurrentCell(ch, 1)

        atw.setItem(ch, 1, it)

        # avalue =
        attributes[str(aname)]

        self.assertEqual(atw.columnCount(), 2)
        self.assertEqual(atw.rowCount(), len(attributes))
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

    # constructor test
    # \brief It tests default settings
    def test_updateNode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit": "newunit", "longname": "newlogname"}
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, form.name)
                cnt += 1
            else:
                self.assertEqual(vl, form.attributes[str(nm)])
        self.assertEqual(len(form.attributes), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, form.doc)

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

        form.name = nname
        form.content = ntype
        form.attributes.clear()
        for at in attrs.keys():
            form.attributes[at] = attrs[at]
        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
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
            else:
                self.assertEqual(vl, attrs[str(nm)])
        self.assertEqual(len(attrs), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, mdoc)

    # constructor test
    # \brief It tests default settings
    def test_updateNode_withindex(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link",
                          "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit": "newunit", "longname": "newlogname"}
        mdoc = "New text \nNew text"

        attributeMap = form.node.attributes()

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, form.name)
                cnt += 1
            else:
                self.assertEqual(vl, form.attributes[str(nm)])
        self.assertEqual(len(form.attributes), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, form.doc)

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

        form.name = nname
        form.content = ntype
        form.attributes.clear()
        for at in attrs.keys():
            form.attributes[at] = attrs[at]
        form.doc = mdoc

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
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
            else:
                self.assertEqual(vl, attrs[str(nm)])
        self.assertEqual(len(attrs), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, mdoc)

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

    # constructor test
    # \brief It tests default settings
    def test_apply(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link", "component",
                          "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        attributeMap = form.node.attributes()

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, form.name)
                cnt += 1
            else:
                self.assertEqual(vl, form.attributes[str(nm)])
        self.assertEqual(len(form.attributes), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, form.doc)

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit": "newunit", "longname": "newlogname",
                 "mynew": "newvalue"}
        mdoc = "New text New text"

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.ui.nameLineEdit.setText(nname)
        form.ui.contentTextEdit.setText(ntype)

        form.ui.docTextEdit.setText(str(mdoc))
        form.ui.docTextEdit.setText(str(mdoc))

        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0, 1)
            item = form.ui.attributeTableWidget.item(
                form.ui.attributeTableWidget.currentRow(), 0)
            print(item.text())

#            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)

        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i, 1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        form.apply()

        self.assertEqual(form.name, nname)
        self.assertEqual(form.content, ntype)
        self.assertEqual(form.doc, mdoc)
        self.assertEqual(form.attributes, attrs)

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
            else:
                self.assertEqual(vl, attrs[str(nm)])
        self.assertEqual(len(attrs), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, mdoc)

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

    # constructor test
    # \brief It tests default settings
    def test_reset(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link",
                          "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        attributeMap = form.node.attributes()

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, form.name)
                cnt += 1
            else:
                self.assertEqual(vl, form.attributes[str(nm)])
        self.assertEqual(len(form.attributes), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, form.doc)

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit": "newunit", "longname": "newlogname",
                 "mynew": "newvalue"}
        mdoc = "New text New text"

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.ui.nameLineEdit.setText(nname)
        form.ui.contentTextEdit.setText(ntype)

        form.ui.docTextEdit.setText(str(mdoc))
        form.ui.docTextEdit.setText(str(mdoc))

        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0, 1)
            item = form.ui.attributeTableWidget.item(
                form.ui.attributeTableWidget.currentRow(), 0)
            print(item.text())

#            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)

        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i, 1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        form.reset()

        ats = {u'shortname': u'mynshort%s' % nn, u'type': u'mytype%s' % nn,
               u'unit': u'myunits%s' % nn}
        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            ("".join(["\nText\n %s\n" % i for i in range(ndcs)])).strip())
        self.assertEqual(form.attributes,  ats)

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, "myname%s" % nn)
                cnt += 1
            else:
                self.assertEqual(vl, ats[str(nm)])
        self.assertEqual(len(ats), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            ("".join(["\nText\n %s\n" % i for i in range(ndcs)])).strip())

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

    # constructor test
    # \brief It tests default settings
    def test_reset_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dks = []
        cks = []
        doc = QDomDocument()
        nname = "definition"
        qdn = doc.createElement(nname)
        nn = self.__rnd.randint(0, 9)
        qdn.setAttribute("name", "myname%s" % nn)
        qdn.setAttribute("type", "mytype%s" % nn)
        qdn.setAttribute("unit", "myunits%s" % nn)
        qdn.setAttribute("shortname", "mynshort%s" % nn)
        cks.append(doc.createTextNode("$components.some%s\n" % nn))
        qdn.appendChild(cks[-1])

        doc.appendChild(qdn)
        dname = "doc"
        mdoc = doc.createElement(dname)
        qdn.appendChild(mdoc)
        ndcs = self.__rnd.randint(0, 10)
        for n in range(ndcs):
            dks.append(doc.createTextNode("\nText\n %s\n" % n))
            mdoc.appendChild(dks[-1])

        form = DefinitionDlg()
        form.show()
        form.node = qdn
        self.assertEqual(form.name, '')
        self.assertEqual(form.content, '')
        self.assertEqual(form.doc, '')
        self.assertEqual(form.attributes, {})
        self.assertEqual(form.subItems,
                         ["group", "field", "attribute", "link",
                          "component", "doc", "symbols"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")

        form.setFromNode()
        form.createGUI()

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        attributeMap = form.node.attributes()

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, form.name)
                cnt += 1
            else:
                self.assertEqual(vl, form.attributes[str(nm)])
        self.assertEqual(len(form.attributes), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""

        self.assertEqual(olddoc, form.doc)

        nname = "newname"
        ntype = "newtype"
        attrs = {"unit": "newunit", "longname": "newlogname",
                 "mynew": "newvalue"}
        mdoc = "New text New text"

        form.root = doc

        allAttr = True
        cm = ComponentModel(doc, allAttr)
        ri = cm.rootIndex
        di = cm.index(0, 0, ri)
        form.view = TestView(cm)
        form.view.testIndex = di

        form.ui.nameLineEdit.setText(nname)
        form.ui.contentTextEdit.setText(ntype)

        form.ui.docTextEdit.setText(str(mdoc))
        form.ui.docTextEdit.setText(str(mdoc))

        for r in form.attributes:
            form.ui.attributeTableWidget.setCurrentCell(0, 1)
            item = form.ui.attributeTableWidget.item(
                form.ui.attributeTableWidget.currentRow(), 0)
            print(item.text())

#            QTimer.singleShot(10, self.rmAttributeWidget)
            QTest.mouseClick(form.ui.removePushButton, Qt.LeftButton)

        i = 0
        for r in attrs:
            form.ui.attributeTableWidget.setCurrentCell(i, 1)
            self.aname = r
            self.avalue = attrs[r]
            QTimer.singleShot(10, self.attributeWidget)
            QTest.mouseClick(form.ui.addPushButton, Qt.LeftButton)
            i += 1

        QTest.mouseClick(form.ui.resetPushButton, Qt.LeftButton)

        ats = {u'shortname': u'mynshort%s' % nn, u'type': u'mytype%s' % nn,
               u'unit': u'myunits%s' % nn}
        self.assertEqual(form.name, "myname%s" % nn)
        self.assertEqual(form.content, "$components.some%s" % nn)
        self.assertEqual(
            form.doc,
            ("".join(["\nText\n %s\n" % i for i in range(ndcs)])).strip())
        self.assertEqual(form.attributes,  ats)

        cnt = 0
        for i in range(attributeMap.count()):
            nm = attributeMap.item(i).nodeName()
            vl = attributeMap.item(i).nodeValue()
            if nm == "name":
                self.assertEqual(vl, "myname%s" % nn)
                cnt += 1
            else:
                self.assertEqual(vl, ats[str(nm)])
        self.assertEqual(len(ats), attributeMap.count() - cnt)

        mydoc = form.node.firstChildElement(str("doc"))
        text = DomTools.getText(mydoc)
        olddoc = unicode(text).strip() if text else ""
        self.assertEqual(
            olddoc,
            ("".join(["\nText\n %s\n" % i for i in range(ndcs)])).strip())

        text = DomTools.getText(form.node)
        oldcont = unicode(text).strip() if text else ""

        self.assertEqual(oldcont, form.content)

    def myAction(self):
        self.performed = True

    # constructor test

    # constructor test
    # \brief It tests default settings
    def test_connect_actions(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)
#        self.assertTrue(isinstance(DomTools, DomTools))

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertEqual(form.externalApply, None)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        # form.ui = Ui_DefinitionDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.ui.linkDSPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertEqual(form.externalApply, None)
        self.assertEqual(form.externalDSLink, None)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        # form.ui = Ui_DefinitionDlg()
        form.ui.applyPushButton = QPushButton(form)
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.createGUI()
        form.show()
        self.assertEqual(
            form.connectExternalActions(None, self.myAction), None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_connect_actions_with_action_link_and_apply_button(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DefinitionDlg()
        form.createGUI()
        form.show()
        self.assertEqual(form.connectExternalActions(self.myAction, None),
                         None)
        self.assertEqual(form.node, None)
        self.assertEqual(form.root, None)
        self.assertEqual(form.view, None)
        self.assertEqual(form.ui.__class__.__name__, "Ui_DefinitionDlg")
        self.assertEqual(form.externalApply, self.myAction)
        self.assertEqual(form.externalDSLink, None)
        self.performed = False

        QTest.mouseClick(form.ui.applyPushButton, Qt.LeftButton)
        self.assertEqual(self.performed, True)

        self.assertEqual(form.result(), 0)


if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
