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
## \package nxsconfigtool nexdatas
## \file CreatorDlg.py
# Component Creator dialog class

""" server creator widget """

from PyQt4.QtCore import SIGNAL, Qt, QVariant
from PyQt4.QtGui import QDialog, QTableWidgetItem, QMessageBox

from .ui.ui_creatordlg import Ui_CreatorDlg
from .ui.ui_stdcreatordlg import Ui_StdCreatorDlg

import logging
## message logger
logger = logging.getLogger("nxsdesigner")


## dialog defining a component creator dialog
class CreatorDlg(QDialog):

    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(CreatorDlg, self).__init__(parent)

        ## host name of the configuration server
        self.components = []
        self.componentName = None
        ## user interface
        self.ui = Ui_CreatorDlg()
        self.action = ''

    ## creates GUI
    # \brief It updates GUI and creates creatorion for required actions
    def createGUI(self):
        self.ui.setupUi(self)
        self.updateForm()

        self.connect(self.ui.savePushButton, SIGNAL("clicked()"),
                     self.savePressed)
        self.connect(self.ui.storePushButton, SIGNAL("clicked()"),
                     self.storePressed)
        self.connect(self.ui.applyPushButton, SIGNAL("clicked()"),
                     self.applyPressed)
        self.connect(self.ui.cancelPushButton, SIGNAL("clicked()"),
                     self.reject)

    ## updates the connect dialog
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


## dialog defining a component creator dialog
class StdCreatorDlg(QDialog):

    ## constructor
    # \param parent patent instance
    def __init__(self, creator, parent=None):
        super(StdCreatorDlg, self).__init__(parent)

        ## host name of the configuration server
        self.__parent = parent
        self.__types = []
        self.__creator = creator
        self.componentType = None
        self.componentName = None
        ## user interface
        self.ui = Ui_StdCreatorDlg()
        self.action = ''
        self.__vars = {}
        self.__pardesc = {}
        self.__oldvars = {}

    ## creates GUI
    # \brief It updates GUI and creates creatorion for required actions
    def createGUI(self):
        self.ui.setupUi(self)
        self.__types = list(self.__creator.listcomponenttypes() or [])
        self.updateForm()
        self.__updateUi()

        self.connect(self.ui.savePushButton, SIGNAL("clicked()"),
                     self.savePressed)
        self.connect(self.ui.linkPushButton, SIGNAL("clicked()"),
                     self.linkPressed)
        self.connect(self.ui.storePushButton, SIGNAL("clicked()"),
                     self.storePressed)
        self.connect(self.ui.applyPushButton, SIGNAL("clicked()"),
                     self.applyPressed)
        self.connect(self.ui.cancelPushButton, SIGNAL("clicked()"),
                     self.reject)
        self.connect(
            self.ui.varTableWidget,
            SIGNAL("itemChanged(QTableWidgetItem*)"),
            self.__tableItemChanged)
        self.connect(
            self.ui.cpNameLineEdit, SIGNAL("textEdited(QString)"),
            self.__updateUi)
        self.connect(self.ui.cpTypeComboBox,
                     SIGNAL("currentIndexChanged(QString)"),
                     self.__currentIndexChanged)

    ## updates the connect dialog
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

    ## calls updateUi when the name text is changing
    # \param text the edited text
    def __currentIndexChanged(self, text):
        self.updateParams()

    ## takes a name of the current variable
    # \returns name of the current variable
    def __currentTableVar(self):
        item = self.ui.varTableWidget.item(
            self.ui.varTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole).toString()

    ## changes the current value of the variable
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

    ## fills in the variable table
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
            item.setData(Qt.UserRole, QVariant(name))
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

    ## updates group user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        enable = not self.ui.cpNameLineEdit.text().isEmpty()
        self.ui.applyPushButton.setEnabled(enable)
        self.ui.storePushButton.setEnabled(enable)
        self.ui.savePushButton.setEnabled(enable)


if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    ## Qt application
    app = QApplication(sys.argv)
    ## connect form
    form = CreatorDlg()
    form.createGUI()
    form.show()
    app.exec_()

    if form.result():
        if form.device:
            logger.info("Connect: %s , %s , %s" %
                        (form.device, form.host, form.port))
