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
# \file DimensionsDlgTest.py
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
from PyQt5.QtWidgets import (QApplication, QMessageBox, QTableWidgetItem)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QObject


from nxsconfigtool.DimensionsDlg import DimensionsDlg
#from nxsconfigtool.ui.ui_dimensionsdlg import Ui_DimensionsDlg


#  Qt-application
app = None



# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


if sys.version_info > (3,):
    unicode = str
    long = int



# test fixture
class DimensionsDlgTest(unittest.TestCase):

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

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256)

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
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.result(), 0)


    def checkMessageBox(self):
        aw = QApplication.activeWindow()
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
#        print "AW", aw
#        print "mb", mb
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.accept()
        mb.close()


    # create GUI test
    # \brief It tests default settings
    def test_createGUI(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.ui.rankSpinBox.value(), 0)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(), 0)



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)

        form = DimensionsDlg()
        form.rank = rank
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, [None]*rank)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), "")




    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_lengths(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [str(self.__rnd.randint(1, 100)) for r in range(rank) ]
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), str(lengths[r]))



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_str_lengths_int(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = str(self.__rnd.randint(0, 6) )
        lengths = [str(self.__rnd.randint(1, 6)) for r in range(int(rank)) ]
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, int(rank))
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(), int(rank))
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(), int(rank))

        for r in range(int(rank)):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), str(lengths[r]))


    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_neg_lengths_int(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(-6, -1)
        lengths = [self.__rnd.randint(1, 100) for r in range(rank) ]
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(), 0)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(), 0)


    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_lengths_int_doc(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [str(self.__rnd.randint(1, 100)) for r in range(rank) ]
        doc = 'My Document'*self.__rnd.randint(1, 10)
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), str(lengths[r]))



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_lengths_int(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [str(self.__rnd.randint(1, 100)) for r in range(rank) ]
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), str(lengths[r]))



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_lengths_zero(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [0 for r in range(rank) ]
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [str(self.__rnd.randint(1, 100)) for r in range(rank) ]
        form = DimensionsDlg()
        form.rank = rank
        form.lengths = lengths
        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.accept()
        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), str(lengths[r]))





    # create GUI test
    # \brief It tests default settings
    def test_createGUI_rank_ui(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [self.__rnd.randint(1, 100) for r in range(rank) ]
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

#        QTest.keyClicks(form.ui.rankSpinBox, str(rank))
        form.ui.rankSpinBox.setValue(rank)
        self.assertEqual(form.ui.rankSpinBox.value(), rank)

        form.accept()
        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, [None]*rank)
        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)
        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_doc_ui(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [self.__rnd.randint(1, 100) for r in range(rank) ]
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

#        QTest.keyClicks(form.ui.rankSpinBox, str(rank))
        form.ui.rankSpinBox.setValue(rank)

        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)

        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')



        okWidget = form.ui.buttonBox.button(form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)


        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, [None]*rank)






    # create GUI test
    # \brief It tests default settings
    def test_createGUI_doc_ui_text(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [self.__rnd.randint(1, 100) for r in range(rank) ]
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

#        QTest.keyClicks(form.ui.rankSpinBox, str(rank))
        form.ui.rankSpinBox.setValue(rank)

        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)

        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')


        cancelWidget = form.ui.buttonBox.button(form.ui.buttonBox.Cancel)
        QTest.mouseClick(cancelWidget, Qt.LeftButton)


        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, [None]*rank)



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_len_ui_text(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [str(self.__rnd.randint(1, 100)) for r in range(rank) ]
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.ui.rankSpinBox.setValue(rank)
#        QTest.keyClicks(form.ui.rankSpinBox, str(rank))


        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)

        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')

        for r in range(rank):
            form.ui.dimTableWidget.setCurrentCell(r, 0)
#            QTest.keyClicks(form.ui.dimTableWidget, str(lengths[r]))
            it = QTableWidgetItem(unicode(lengths[r]))
            form.ui.dimTableWidget.setItem(r, 0,it)



        cancelWidget = form.ui.buttonBox.button(form.ui.buttonBox.Cancel)
        QTest.mouseClick(cancelWidget, Qt.LeftButton)


        self.assertEqual(form.result(), 0)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)



    # create GUI test
    # \brief It tests default settings
    def test_createGUI_len_ui_text_err(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [self.__rnd.randint(1, 100) for r in range(rank) ]
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.ui.rankSpinBox.setValue(rank)
#        QTest.keyClicks(form.ui.rankSpinBox, str(rank))


        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)

        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')


        for r in range(rank):
            QTimer.singleShot(10, self.checkMessageBox)
            form.ui.dimTableWidget.setCurrentCell(r, 0)
            it = QTableWidgetItem("blew")
            form.ui.dimTableWidget.setItem(r, 0,it)
            self.assertEqual(self.text, 'Wrong value of the edited length')


        okWidget = form.ui.buttonBox.button(form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)


        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, [None]*rank)




    # create GUI test
    # \brief It tests default settings
    def test_createGUI_len_ui_text_err_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        rank = self.__rnd.randint(1, 6)
        lengths = [str(self.__rnd.randint(1, 100)) for r in range(rank) ]
        form = DimensionsDlg()
        self.assertEqual(form.rank, 0)
        self.assertEqual(form.lengths, [])
        self.assertEqual(form.subItems, ["dim"])
        self.assertEqual(form.ui.__class__.__name__, "Ui_DimensionsDlg")

        self.assertEqual(form.createGUI(), None)
        form.show()

        form.ui.rankSpinBox.setValue(rank)
#        QTest.keyClicks(form.ui.rankSpinBox, str(rank))


        self.assertEqual(form.ui.rankSpinBox.value(),rank)
        self.assertEqual(form.ui.dimTableWidget.columnCount(), 1)
        self.assertEqual(form.ui.dimTableWidget.rowCount(),rank)

        for r in range(rank):
            it = form.ui.dimTableWidget.item(r, 0)
            self.assertEqual(it.text(), '')

        for r in range(rank):
            form.ui.dimTableWidget.setCurrentCell(r, 0)
            it = QTableWidgetItem(unicode(lengths[r]))
            form.ui.dimTableWidget.setItem(r, 0,it)

        for r in range(rank):
            QTimer.singleShot(10, self.checkMessageBox)
            form.ui.dimTableWidget.setCurrentCell(r, 0)
#            QTest.keyClicks(form.ui.dimTableWidget, str(lengths[r]))
            it = QTableWidgetItem("blew")
            form.ui.dimTableWidget.setItem(r, 0,it)
            self.assertEqual(self.text, 'Wrong value of the edited length')

        okWidget = form.ui.buttonBox.button(form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)


        self.assertEqual(form.result(), 1)

        self.assertEqual(form.rank, rank)
        self.assertEqual(form.lengths, lengths)



if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()
