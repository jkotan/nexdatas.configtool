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
# \package nxsconfigtool nexdatas
# \file DimensionsDlg.py
# Dimensions dialog class

""" dimensions widget """

from PyQt5.QtCore import (Qt, )
from PyQt5.QtWidgets import (QTableWidgetItem, QMessageBox, QDialog)
from PyQt5 import uic

import os
import sys

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "dimensionsdlg.ui"))

if sys.version_info > (3,):
    unicode = str
    long = int


# dialog defining a dimensions tag
class DimensionsDlg(QDialog):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DimensionsDlg, self).__init__(parent)

        # dimensions rank
        self.rank = 0
        # dimensions lengths
        self.lengths = []

        # user interface
        self.ui = _formclass()

        # allowed subitems
        self.subItems = ["dim"]

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):

        try:
            if self.rank is not None and int(self.rank) >= 0:
                self.rank = int(self.rank)
                for i, ln in enumerate(self.lengths):
                    if ln:
                        if '$var.' not in ln and '$datasources.' not in ln:
                            iln = int(ln)
                            self.lengths[i] = ln
                            if iln < 1:
                                self.lengths[i] = None
                        else:
                            self.lengths[i] = ln
                    else:
                        self.lengths[i] = None
        except Exception:
            self.rank = 1
            self.lengths = []

        if not self.lengths:
            self.lengths = []

        self.ui.setupUi(self)

        self.ui.rankSpinBox.setValue(self.rank)

        self.ui.dimTableWidget.itemChanged.connect(
            self.__tableItemChanged)

        self.ui.dimTableWidget.setSortingEnabled(False)
        self.__populateLengths()
        self.ui.rankSpinBox.setFocus()

        self.ui.rankSpinBox.valueChanged[int].connect(self.__valueChanged)

    # takes a name of the current dim
    # \returns name of the current dim
    def __currentTableDim(self):
        return self.ui.dimTableWidget.currentRow()

    # changes the current value of the dim
    # \brief It changes the current value of the dim
    # and informs the user about wrong values
    def __tableItemChanged(self, item):
        row = self.__currentTableDim()

        if row not in range(len(self.lengths)):
            return
        column = self.ui.dimTableWidget.currentColumn()
        if column == 0:
            try:
                if item.text():
                    if '$var' not in str(item.text()) and  \
                            '$datasources' not in str(item.text()):
                        iln = int(item.text())
                        if iln < 1:
                            raise ValueError("Non-positive length value")
                    ln = str(item.text())
                    self.lengths[row] = ln
                else:
                    self.lengths[row] = None
            except Exception:
                QMessageBox.warning(
                    self, "Value Error", "Wrong value of the edited length")

        self.__populateLengths()

    # calls updateUi when the name text is changing
    # \param text the edited text
    def __valueChanged(self):
        self.rank = int(self.ui.rankSpinBox.value())
        self.__populateLengths(self.rank - 1)

    # fills in the dim table
    # \param selectedDim selected dim
    def __populateLengths(self, selectedDim=None):
        selected = None
        self.ui.dimTableWidget.clear()
        self.ui.dimTableWidget.setRowCount(self.rank)

        while self.rank > len(self.lengths):
            self.lengths.append(None)

        headers = ["Length"]
        self.ui.dimTableWidget.setColumnCount(len(headers))
        self.ui.dimTableWidget.setHorizontalHeaderLabels(headers)
        self.ui.dimTableWidget.setVerticalHeaderLabels(
            [unicode(el + 1) for el in range(self.rank)])
        for row, ln in enumerate(self.lengths):
            if ln:
                item = QTableWidgetItem(unicode(ln))
            else:
                item = QTableWidgetItem("")
            item.setData(Qt.UserRole, (long(row)))
            if selectedDim is not None and selectedDim == row:
                selected = item
            self.ui.dimTableWidget.setItem(row, 0, item)
        self.ui.dimTableWidget.resizeColumnsToContents()
        self.ui.dimTableWidget.horizontalHeader().setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.dimTableWidget.setCurrentItem(selected)
            self.ui.dimTableWidget.editItem(selected)

    # accepts input text strings
    # \brief It copies the dimensions name and type from lineEdit widgets
    #        and accept the dialog
    def accept(self):
        while len(self.lengths) > self.rank:
            self.lengths.pop()
        QDialog.accept(self)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # dimensions form
    form = DimensionsDlg()
    form.rank = 2
    form.lengths = [25, 27]
#    form.lengths = [None, 3]
    form.createGUI()
    form.show()
    app.exec_()

    if form.result():
        if form.rank:
            logger.info("Dimensions: rank = %s" % (form.rank))
        if form.lengths:
            logger.info("Lengths:")
            for mrow, mln in enumerate(form.lengths):
                logger.info(" %s: %s " % (mrow + 1, mln))
