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
# \file CreatorDlg.py
# Component Creator dialog class

""" server creator widget """
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5 import uic

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "creatordlg.ui"))

_stdformclass, _stdbaseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "stdcreatordlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a component creator dialog
class CreatorDlg(QDialog):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(CreatorDlg, self).__init__(parent)

        # host name of the configuration server
        self.components = []
        self.componentName = None
        # user interface
        self.ui = _formclass()
        self.action = ''

    # creates GUI
    # \brief It updates GUI and creates creatorion for required actions
    def createGUI(self):
        self.ui.setupUi(self)
        self.updateForm()

        self.ui.savePushButton.clicked.connect(self.savePressed)
        self.ui.storePushButton.clicked.connect(self.storePressed)
        self.ui.applyPushButton.clicked.connect(self.applyPressed)
        self.ui.cancelPushButton.clicked.connect(self.reject)

    # updates the connect dialog
    # \brief It sets initial values of the connection form
    def updateForm(self):
        self.ui.compComboBox.clear()
        if self.components:
            self.ui.compComboBox.addItems(self.components)

    def savePressed(self):
        self.componentName = unicode(self.ui.compComboBox.currentText())
        self.action = 'SAVE'
        QDialog.accept(self)

    def storePressed(self):
        self.componentName = unicode(self.ui.compComboBox.currentText())
        self.action = 'STORE'
        QDialog.accept(self)

    def applyPressed(self):
        self.componentName = unicode(self.ui.compComboBox.currentText())
        self.action = 'APPLY'
        QDialog.accept(self)


# dialog defining a component creator dialog
class StdCreatorDlg(QDialog):

    # constructor
    # \param parent patent instance
    def __init__(self, creator, parent=None):
        super(StdCreatorDlg, self).__init__(parent)

        # host name of the configuration server
        self.__parent = parent
        self.__types = []
        self.__creator = creator
        self.componentType = None
        self.componentName = None
        # user interface
        self.ui = _stdformclass()
        self.action = ''
        self.__vars = {}
        self.__pardesc = {}
        self.__oldvars = {}

    # creates GUI
    # \brief It updates GUI and creates creatorion for required actions
    def createGUI(self):
        self.ui.setupUi(self)
        self.__types = list(self.__creator.listcomponenttypes() or [])
        self.updateForm()
        self.__updateUi()

        self.ui.savePushButton.clicked.connect(
            self.savePressed)
        self.ui.linkPushButton.clicked.connect(
            self.linkPressed)
        self.ui.storePushButton.clicked.connect(
            self.storePressed)
        self.ui.applyPushButton.clicked.connect(
            self.applyPressed)
        self.ui.cancelPushButton.clicked.connect(
            self.reject)
        self.ui.varTableWidget.itemChanged.connect(
            self.__tableItemChanged)
        self.ui.cpNameLineEdit.textEdited[str].connect(
            self.__updateUi)
        self.ui.cpTypeComboBox.currentIndexChanged[str].connect(
            self.__currentIndexChanged)

    # updates the connect dialog
    # \brief It sets initial values of the connection form
    def updateForm(self):
        self.ui.cpTypeComboBox.clear()
        if self.__types:
            self.ui.cpTypeComboBox.addItems(self.__types)
        self.updateParams()

    def updateParams(self):
        self.componentType = unicode(self.ui.cpTypeComboBox.currentText())
        self.__creator.options.cptype = self.componentType or None
        if self.componentType:
            self.__pardesc = self.__creator.listcomponentvariables()
            self.__vars = {}
            for var in sorted(self.__pardesc.keys()):
                desc = self.__pardesc[var]
                if not var.startswith('__') and not var.endswith('__'):
                    if var not in self.__vars or self.__vars[var] is None:
                        if var in self.__oldvars and \
                           self.__oldvars[var] is not None:
                            self.__vars[var] = self.__oldvars[var]
                        else:
                            self.__vars[var] = desc['default']
                            self.__oldvars[var] = self.__vars[var]

        self.populateVars()

    def populateArgs(self):
        args = []
        for name, value in self.__vars.items():
            if value:
                args.extend([name, value])
        self.__creator.args = args

    def savePressed(self):
        self.componentName = unicode(self.ui.cpNameLineEdit.text())
        self.__creator.options.component = self.componentName or None
        self.populateArgs()
        self.action = 'SAVE'
        QDialog.accept(self)

    def storePressed(self):
        self.componentName = unicode(self.ui.cpNameLineEdit.text())
        self.__creator.options.component = self.componentName or None
        self.populateArgs()
        self.action = 'STORE'
        QDialog.accept(self)

    def applyPressed(self):
        self.componentName = unicode(self.ui.cpNameLineEdit.text())
        self.__creator.options.component = self.componentName or None
        self.populateArgs()
        self.action = 'APPLY'
        QDialog.accept(self)

    def linkPressed(self):
        dsname = self.__parent.currentDataSourceName()
        if not dsname:
            QMessageBox.warning(
                self, "DataSource not selected",
                "Please select the required datasource from the list")
            return

        var = self.__currentTableVar()
        if unicode(var) not in self.__vars.keys():
            QMessageBox.warning(
                self, "Variable not selected",
                "Please select the required variable from the table")
            return
            return
        self.__vars[unicode(var)] = unicode(dsname)
        self.__oldvars[unicode(var)] = self.__vars[unicode(var)]
        self.populateVars()

    # calls updateUi when the name text is changing
    # \param text the edited text
    def __currentIndexChanged(self, text):
        self.updateParams()

    # takes a name of the current variable
    # \returns name of the current variable
    def __currentTableVar(self):
        item = self.ui.varTableWidget.item(
            self.ui.varTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole)

    # changes the current value of the variable
    # \brief It changes the current value of the variable
    #        and informs the user that variable names arenot editable
    def __tableItemChanged(self, item):
        var = self.__currentTableVar()
        if unicode(var) not in self.__vars.keys():
            return
        column = self.ui.varTableWidget.currentColumn()
        if column == 1:
            self.__vars[unicode(var)] = unicode(item.text())
            self.__oldvars[unicode(var)] = self.__vars[unicode(var)]
        if column == 0:
            QMessageBox.warning(
                self, "Variable name is not editable",
                "You cannot change it")
        if column == 3:
            QMessageBox.warning(
                self, "Variable descritpion is not editable",
                "You cannot change it")
        self.populateVars()

    # fills in the variable table
    # \param selectedVariable selected variable
    def populateVars(self, selectedVar=None):
        selected = None
        self.ui.varTableWidget.clear()
        self.ui.varTableWidget.setSortingEnabled(False)
        self.ui.varTableWidget.setRowCount(len(self.__vars))
        headers = ["Name", "Value", "Info"]
        self.ui.varTableWidget.setColumnCount(len(headers))
        self.ui.varTableWidget.setHorizontalHeaderLabels(headers)
        for row, name in enumerate(sorted(self.__vars.keys())):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, (name))
            flags = item.flags()
            flags ^= Qt.ItemIsEditable
            item.setFlags(flags)
            self.ui.varTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self.__vars[name] or "")
            self.ui.varTableWidget.setItem(row, 1, item2)
            item3 = QTableWidgetItem(self.__pardesc[name]['doc'] or "")
            flags = item3.flags()
            flags &= ~Qt.ItemIsEnabled
            item3.setFlags(flags)
            self.ui.varTableWidget.setItem(row, 2, item3)
            if selectedVar is not None and selectedVar == name:
                selected = item2
        self.ui.varTableWidget.setSortingEnabled(True)
        self.ui.varTableWidget.resizeColumnsToContents()
        self.ui.varTableWidget.horizontalHeader()\
            .setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.varTableWidget.setCurrentItem(selected)

    # updates group user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        enable = bool(self.ui.cpNameLineEdit.text())
        self.ui.applyPushButton.setEnabled(enable)
        self.ui.storePushButton.setEnabled(enable)
        self.ui.savePushButton.setEnabled(enable)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # connect form
    form = CreatorDlg()
    form.createGUI()
    form.show()
    app.exec_()

    if form.result():
        if form.device:
            logger.info("Connect: %s , %s , %s" %
                        (form.device, form.host, form.port))
