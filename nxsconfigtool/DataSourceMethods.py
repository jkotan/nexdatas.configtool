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
# \file DataSourceMethods.py
# Data Source method class

""" Provides datasource widget methods """

import sys

from PyQt5.QtCore import (QModelIndex)
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QVBoxLayout)
from PyQt5.QtXml import (QDomDocument)

from .DomTools import DomTools
from .Errors import ParameterError


import logging
# message logger
logger = logging.getLogger("nxsdesigner")

if sys.version_info > (3,):
    unicode = str


# dialog defining datasource
class DataSourceMethods(object):

    # constructor
    # \param dialog datasource dialog
    # \param datasource data
    # \param parent qt parent
    def __init__(self, dialog, datasource, parent=None):

        # datasource dialog
        self.__dialog = dialog

        # datasource data
        self.__datasource = datasource

        # qt parent
        self.__parent = parent

    # clears the dialog
    # \brief It sets dialog to None
    def setDialog(self, dialog=None):
        self.__dialog = dialog

    # creates a new dialog
    def createDialog(self):
        if self.__datasource.dialog:
            self.__dialog = self.__datasource.dialog
        else:
            self.__datasource.createDialog()

    # rejects the changes
    # \brief It asks for the cancellation  and reject the changes
    def close(self):
        if QMessageBox.question(self.__parent, "Close datasource",
                                "Would you like to close the datasource?",
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes) == QMessageBox.No:
            return
        self.updateForm()
        if not self.__dialog:
            self.createDialog()
        self.__dialog.reject()

    #  resets the form
    # \brief It reverts form variables to the last accepted ones
    def reset(self):
        self.updateForm()

    # updates the datasource self.__dialog
    # \brief It sets the form local variables
    def updateForm(self):
        if not self.__dialog or not self.__datasource:
            raise ParameterError("updateForm parameters not defined")

        if self.__datasource.doc is not None:
            self.__dialog.ui.docTextEdit.setText(self.__datasource.doc)
        if self.__datasource.dataSourceType is not None:
            index = self.__dialog.ui.typeComboBox.findText(
                unicode(self.__datasource.dataSourceType))
            if index > -1:
                self.__dialog.ui.typeComboBox.setCurrentIndex(index)
            else:
                self.__datasource.dataSourceType = 'CLIENT'
        if self.__datasource.dataSourceName is not None:
            self.__dialog.ui.nameLineEdit.setText(
                self.__datasource.dataSourceName)

        for k in self.__dialog.imp.keys():
            self.__dialog.imp[k].updateForm(self.__datasource)

        self.__dialog.setFrames(self.__datasource.dataSourceType)

    # sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode
    def treeMode(self, enable=True):
        if enable:
            self.__dialog.ui.closeSaveFrame.hide()
            self.__datasource.tree = True
        else:
            self.__datasource.tree = False
            self.__dialog.ui.closeSaveFrame.show()

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        if not self.__dialog:
            self.createDialog()
        if self.__dialog and self.__dialog.ui \
                and not hasattr(self.__dialog.ui, "resetPushButton"):
            self.__dialog.ui.setupUi(self.__dialog)
            layout = QVBoxLayout()
            for ds in self.__dialog.wg.keys():
                self.__dialog.qwg[ds] = QWidget(self.__dialog)
                self.__dialog.wg[ds].setupUi(self.__dialog.qwg[ds])
                layout.addWidget(self.__dialog.qwg[ds])

            self.__dialog.ui.dsFrame.setLayout(layout)

        self.updateForm()
        self.__dialog.resize(460, 550)

        if not self.__datasource.tree:

            try:
                self.__dialog.ui.resetPushButton.clicked.disconnect(self.reset)
            except Exception:
                pass
            self.__dialog.ui.resetPushButton.clicked.connect(self.reset)
        else:
            try:
                self.__dialog.ui.resetPushButton.clicked.disconnect(
                    self.__dialog.reset)
            except Exception:
                pass
            self.__dialog.ui.resetPushButton.clicked.connect(
                self.__dialog.reset)
        self.__dialog.connectWidgets()
        self.__dialog.setFrames(self.__datasource.dataSourceType)

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if not self.__dialog:
            self.createDialog()
        if node:
            # defined in NodeDlg class
            self.__dialog.node = node
            if self.__dialog:
                self.__dialog.node = node
        if not self.__dialog.node \
                or not hasattr(self.__dialog.node, "attributes"):
            return
        attributeMap = self.__dialog.node.attributes()

        value = attributeMap.namedItem("type").nodeValue() \
            if attributeMap.contains("type") else ""
        self.__datasource.dataSourceType = unicode(value)

        if attributeMap.contains("name"):
            self.__datasource.dataSourceName = \
                attributeMap.namedItem("name").nodeValue()

        if value in self.__dialog.imp.keys():
            self.__dialog.imp[str(value)].setFromNode(self.__datasource)

        doc = self.__dialog.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.__datasource.doc = unicode(text).strip() if text else ""

    # accepts input text strings
    # \brief It copies the parameters and accept the self.__dialog
    def apply(self):
        if not self.__dialog:
            self.createDialog()

        self.__datasource.applied = False
        sourceType = unicode(self.__dialog.ui.typeComboBox.currentText())
        self.__datasource.dataSourceName = unicode(
            self.__dialog.ui.nameLineEdit.text())

        if sourceType in self.__dialog.imp.keys():
            self.__dialog.imp[sourceType].fromForm(self.__datasource)

        self.__datasource.dataSourceType = sourceType
        self.__datasource.doc = unicode(
            self.__dialog.ui.docTextEdit.toPlainText()).strip()

        index = QModelIndex()
        if hasattr(self.__dialog, "view") and self.__dialog.view \
                and self.__dialog.view.model():
            if hasattr(self.__dialog.view, "currentIndex"):
                index = self.__dialog.view.currentIndex()
                finalIndex = self.__dialog.view.model().createIndex(
                    index.row(), 2, index.parent().internalPointer())
                self.__dialog.view.expand(index)

        row = index.row()
        column = index.column()
        parent = index.parent()

        if self.__dialog.root:
            self.updateNode(index)

            if index.isValid():
                index = self.__dialog.view.model().index(row, column, parent)
                self.__dialog.view.setCurrentIndex(index)
                self.__dialog.view.expand(index)

            if hasattr(self.__dialog, "view") and self.__dialog.view \
                    and self.__dialog.view.model():
                self.__dialog.view.model().dataChanged.emit(
                    index.parent(), index.parent())
                if index.column() != 0:
                    index = self.__dialog.view.model().index(index.row(), 0,
                                                             index.parent())
                self.__dialog.view.model().dataChanged.emit(
                    index, finalIndex)
                self.__dialog.view.expand(index)

        if not self.__datasource.tree:
            self.createNodes()

        self.__datasource.applied = True

        return True

    def __createDOMNodes(self, root):
        newDs = root.createElement(str("datasource"))
        elem = newDs.toElement()
#        attributeMap = self.__datasource.newDs.attributes()
        elem.setAttribute(str("type"),
                          str(self.__datasource.dataSourceType))
        if self.__datasource.dataSourceName:
            elem.setAttribute(str("name"),
                              str(self.__datasource.dataSourceName))
        else:
            logger.info("name not defined")

        if self.__datasource.dataSourceType in self.__dialog.imp.keys():
            self.__dialog.imp[str(self.__datasource.dataSourceType)
                              ].createNodes(self.__datasource, root, elem)

        if(self.__datasource.doc):
            newDoc = root.createElement(str("doc"))
            newText = root.createTextNode(str(self.__datasource.doc))
            newDoc.appendChild(newText)
            elem.appendChild(newDoc)
        return elem

    # creates datasource node
    # \param external True if it should be create on a local DOM root,
    #        i.e. in component tree
    # \returns created DOM node
    def createNodes(self, external=False):
        if not self.__dialog:
            self.createDialog()
        if external:
            root = QDomDocument()
        else:
            if not self.__dialog.root or not self.__dialog.node:
                self.createHeader()
            root = self.__dialog.root

        elem = self.__createDOMNodes(root)

        if external and hasattr(self.__dialog.root, "importNode"):
            rootDs = self.__dialog.root.importNode(elem, True)
        else:
            rootDs = elem
        return rootDs

    # updates the Node
    # \brief It sets node from the self.__dialog variables
    def updateNode(self, index=QModelIndex()):
        if not self.__dialog:
            self.createDialog()

        newDs = self.createNodes(self.__datasource.tree)
        oldDs = self.__dialog.node

        if hasattr(index, "parent"):
            parent = index.parent()
        else:
            parent = QModelIndex()

        self.__dialog.node = self.__dialog.node.parentNode()
        if self.__datasource.tree:
            if self.__dialog.view is not None \
                    and self.__dialog.view.model() is not None:
                DomTools.replaceNode(oldDs, newDs, parent,
                                     self.__dialog.view.model())
        else:
            self.__dialog.node.replaceChild(newDs, oldDs)
        self.__dialog.node = newDs

    # reconnects save actions
    # \brief It reconnects the save action
    def reconnectSaveAction(self):
        if not self.__dialog:
            self.createDialog()
        if self.__datasource.externalSave:
            try:
                self.__dialog.ui.savePushButton.clicked.disconnect(
                    self.__datasource.externalSave)
            except Exception:
                pass
            self.__dialog.ui.savePushButton.clicked.connect(
                self.__datasource.externalSave)
            # self.__parent.disconnect(self.__dialog.ui.savePushButton,
            #                       SIGNAL("clicked()"),
            #                       self.__datasource.externalSave)
            # self.__parent.connect(self.__dialog.ui.savePushButton,
            #                       SIGNAL("clicked()"),
            #                       self.__datasource.externalSave)
        if self.__datasource.externalStore:
            try:
                self.__dialog.ui.storePushButton.clicked.disconnect(
                    self.__datasource.externalStore)
            except Exception:
                pass
            self.__dialog.ui.storePushButton.clicked.connect(
                self.__datasource.externalStore)
            # self.__parent.disconnect(self.__dialog.ui.storePushButton,
            #                          SIGNAL("clicked()"),
            #                          self.__datasource.externalStore)
            # self.__parent.connect(self.__dialog.ui.storePushButton,
            #                       SIGNAL("clicked()"),
            #                       self.__datasource.externalStore)
        if self.__datasource.externalClose:
            try:
                self.__dialog.ui.closePushButton.clicked.disconnect(
                    self.__datasource.externalClose)
            except Exception:
                pass
            self.__dialog.ui.closePushButton.clicked.connect(
                                     self.__datasource.externalClose)
            # self.__parent.disconnect(self.__dialog.ui.closePushButton,
            #                          SIGNAL("clicked()"),
            #                          self.__datasource.externalClose)
            # self.__parent.connect(self.__dialog.ui.closePushButton,
            #                       SIGNAL("clicked()"),
            #                       self.__datasource.externalClose)
        if self.__datasource.externalApply:
            try:
                self.__dialog.ui.applyPushButton.clicked.disconnect(
                    self.__datasource.externalApply)
            except Exception:
                pass
            self.__dialog.ui.applyPushButton.clicked.connect(
                self.__datasource.externalApply)
            # self.__parent.disconnect(self.__dialog.ui.applyPushButton,
            #                          SIGNAL("clicked()"),
            #                          self.__datasource.externalApply)
            # self.__parent.connect(self.__dialog.ui.applyPushButton,
            #                       SIGNAL("clicked()"),
            #                       self.__datasource.externalApply)

    # connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    def connectExternalActions(self, externalApply=None, externalSave=None,
                               externalClose=None, externalStore=None):
        if not self.__dialog:
            self.createDialog()
        if externalSave and self.__datasource.externalSave is None:
            try:
                self.__dialog.ui.savePushButton.clicked.disconnect(
                    externalSave)
            except Exception:
                pass
            self.__dialog.ui.savePushButton.clicked.connect(
                externalSave)
            # self.__parent.disconnect(self.__dialog.ui.savePushButton,
            #                          SIGNAL("clicked()"),
            #                          externalSave)
            # self.__parent.connect(self.__dialog.ui.savePushButton,
            #                       SIGNAL("clicked()"),
            #                       externalSave)
            self.__datasource.externalSave = externalSave
        if externalStore and self.__datasource.externalStore is None:
            try:
                self.__dialog.ui.storePushButton.clicked.disconnect(
                    externalStore)
            except Exception:
                pass
            self.__dialog.ui.storePushButton.clicked.connect(
                externalStore)
            # self.__parent.disconnect(self.__dialog.ui.storePushButton,
            #                          SIGNAL("clicked()"),
            #                          externalStore)
            # self.__parent.connect(self.__dialog.ui.storePushButton,
            #                       SIGNAL("clicked()"),
            #                       externalStore)
            self.__datasource.externalStore = externalStore
        if externalClose and self.__datasource.externalClose is None:
            try:
                self.__dialog.ui.closePushButton.clicked.disconnect(
                    externalClose)
            except Exception:
                pass
            self.__dialog.ui.closePushButton.clicked.connect(
                externalClose)
            # self.__parent.disconnect(self.__dialog.ui.closePushButton,
            #                          SIGNAL("clicked()"),
            #                          externalClose)
            # self.__parent.connect(self.__dialog.ui.closePushButton,
            #                       SIGNAL("clicked()"),
            #                       externalClose)
            self.__datasource.externalClose = externalClose
        if externalApply and self.__datasource.externalApply is None:
            try:
                self.__dialog.ui.applyPushButton.clicked.disconnect(
                    externalApply)
            except Exception:
                pass
            self.__dialog.ui.applyPushButton.clicked.connect(
                externalApply)
            # self.__parent.disconnect(self.__dialog.ui.applyPushButton,
            #                          SIGNAL("clicked()"),
            #                          externalApply)
            # self.__parent.connect(self.__dialog.ui.applyPushButton,
            #                       SIGNAL("clicked()"),
            #                       externalApply)
            self.__datasource.externalApply = externalApply

    # creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        if not self.__dialog:
            self.createDialog()
        if hasattr(self.__dialog, "view") and self.__dialog.view:
            self.__dialog.view.setModel(None)
        self.__datasource.document = QDomDocument()
        # defined in NodeDlg class
        self.__dialog.root = self.__datasource.document
        processing = self.__dialog.root.createProcessingInstruction(
            "xml", "version='1.0'")
        self.__dialog.root.appendChild(processing)

        definition = self.__dialog.root.createElement(str("definition"))
        self.__dialog.root.appendChild(definition)
        self.__dialog.node = self.__dialog.root.createElement(
            str("datasource"))
        definition.appendChild(self.__dialog.node)
        return self.__dialog.node

    # copies the datasource to the clipboard
    # \brief It copies the current datasource to the clipboard
    def copyToClipboard(self):
        dsNode = self.createNodes(True)
        doc = QDomDocument()
        child = doc.importNode(dsNode, True)
        doc.appendChild(child)
        text = unicode(doc.toString(0))
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    # copies the datasource from the clipboard to the current datasource
    #       dialog
    # \return status True on success
    def copyFromClipboard(self):
        if not self.__dialog:
            self.createDialog()
        clipboard = QApplication.clipboard()
        text = unicode(clipboard.text())
        self.__datasource.document = QDomDocument()
        self.__dialog.root = self.__datasource.document
        if not self.__datasource.document.setContent(
                self.__datasource.repair(text)):
            raise ValueError("could not parse XML")
        else:
            if self.__dialog and hasattr(self.__dialog, "root"):
                self.__dialog.root = self.__datasource.document
                self.__dialog.node = DomTools.getFirstElement(
                    self.__datasource.document, "datasource")
        if not self.__dialog.node:
            return
        self.setFromNode(self.__dialog.node)

        return True


if __name__ == "__main__":
    pass
