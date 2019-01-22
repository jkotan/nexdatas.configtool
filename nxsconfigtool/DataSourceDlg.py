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
# \file DataSourceDlg.py
# Data Source dialog class

""" Provides datasource widget """

from PyQt5.QtCore import QModelIndex, pyqtSlot
from PyQt5.QtWidgets import QApplication

from .NodeDlg import NodeDlg
from .DataSources import ClientSource, TangoSource, DBSource, PyEvalSource
from .DataSourceMethods import DataSourceMethods
from PyQt5 import uic

import os


# from .ui.ui_datasourcedlg import Ui_DataSourceDlg
_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "datasourcedlg.ui"))


# available datasources
dsTypes = {'CLIENT': ClientSource,
           'TANGO': TangoSource,
           'DB': DBSource,
           'PYEVAL': PyEvalSource
           }


# load user datasources
# \param dsJSON json string with user datasources
def appendUserDataSource(dsJSON):
    for dk in dsJSON.keys():
        pkl = dsJSON[dk].split(".")
        dec = __import__(".".join(pkl[:-1]),
                         globals(), locals(), pkl[-1])
        dsTypes[dk] = getattr(dec, pkl[-1])


# dialog defining commmon datasource
class CommonDataSourceDlg(NodeDlg):

    # constructor
    # \param datasource instance
    # \param parent patent instance
    def __init__(self, datasource, parent=None):
        super(CommonDataSourceDlg, self).__init__(parent)

        #  datasource instance
        self.datasource = datasource

        # allowed subitems
        self.subItems = []

        # datasource dialog impementations
        self.imp = {}

        # user interface
        self.ui = _formclass()
        # datasource widget
        self.wg = {}

        # QWidget instances
        self.qwg = {}

        for ds in dsTypes.keys():
            self.imp[ds] = dsTypes[ds](self)
            self.subItems.extend(self.imp[ds].subItems)
            self.wg[ds] = self.imp[ds].widgetClass()
            self.imp[ds].ui = self.wg[ds]

    # sets focus on save button
    # \brief It sets focus on save button
    def setSaveFocus(self):
        if self.ui:
            self.ui.savePushButton.setFocus()

    # updates group user interface
    # \brief It sets enable or disable the OK button
    def updateUi(self, text):
        enable = True
        if text in self.imp.keys():
            enable = self.imp[str(text)].isEnable()
        self.ui.applyPushButton.setEnabled(enable)
        self.ui.savePushButton.setEnabled(enable)
        self.ui.storePushButton.setEnabled(enable)
        self.setTabOrder(self.ui.typeComboBox, self.ui.nameLineEdit)
        self.imp[str(text)].setTabOrder(
            self.ui.nameLineEdit, self.ui.savePushButton)
        self.setTabOrder(self.ui.savePushButton, self.ui.storePushButton)
        self.setTabOrder(self.ui.storePushButton, self.ui.closePushButton)
        self.setTabOrder(self.ui.closePushButton, self.ui.applyPushButton)
        self.setTabOrder(self.ui.applyPushButton, self.ui.resetPushButton)
        self.setTabOrder(self.ui.resetPushButton, self.ui.docTextEdit)

    # shows and hides frames according to typeComboBox
    # \param text the edited text
    @pyqtSlot(str)
    def setFrames(self, text):
        for k in self.qwg.keys():
            if text == k:
                self.qwg[k].show()
            else:
                self.qwg[k].hide()

            if hasattr(self.imp[k], "populateParameters"):
                self.imp[k].populateParameters()

        self.updateUi(text)

    # connects the dialog actions
    def connectWidgets(self):
        try:
            self.ui.typeComboBox.currentIndexChanged[str].disconnect(
                self.setFrames)
        except Exception:
            pass
        self.ui.typeComboBox.currentIndexChanged[str].connect(self.setFrames)
        for k in self.imp.keys():
            self.imp[k].connectWidgets()

    # closes the window and cleans the dialog label
    # \param event closing event
    def closeEvent(self, event):
        if hasattr(self.datasource.dialog, "clearDialog"):
            self.datasource.dialog.clearDialog()
        self.datasource.dialog = None
        if hasattr(self.datasource, "clearDialog"):
            self.datasource.clearDialog()
        event.accept()

    # rejects datasource changes
    def reject(self):
        self.parent().close()
        super(CommonDataSourceDlg, self).reject()


# dialog defining separate datasource
class DataSourceDlg(CommonDataSourceDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DataSourceDlg, self).__init__(None, parent)

        from .DataSource import CommonDataSource

        # datasource data
        self.datasource = CommonDataSource(parent)
        # datasource methods
        self.__methods = DataSourceMethods(self, self.datasource, parent)

    # updates the form
    # \brief updates the form
    def updateForm(self):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.updateForm()

    # clears the dialog
    # \brief clears the dialog
    def clearDialog(self):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.setDialog(None)

    # updates the node
    # \brief updates the node
    def updateNode(self, index=QModelIndex()):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.updateNode(index)

    # creates GUI
    # \brief creates GUI
    def createGUI(self):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.createGUI()

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.setFromNode(node)

    # accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def apply(self):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.apply()

    # sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode
    def treeMode(self, enable=True):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.treeMode(enable)

    # connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    # \param externalDSLink dsource link action
    def connectExternalActions(self, externalApply=None, externalSave=None,
                               externalClose=None, externalStore=None,
                               externalDSLink=None):
        if hasattr(self, "_DataSourceDlg__methods") and self.__methods:
            return self.__methods.connectExternalActions(
                externalApply, externalSave,
                externalClose, externalStore)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QWidget
    # Qt application
    app = QApplication(sys.argv)

    # the second datasource form

    w = QWidget()
    w.show()
    # datasource form
    form2 = DataSourceDlg(w)
    form2.createGUI()
    form2.treeMode(True)

    form2.show()

    app.exec_()
