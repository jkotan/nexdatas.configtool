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
# \file LinkDlg.py
# Link dialog class

""" link widget """

import os
import sys

from PyQt5.QtCore import (QModelIndex)
from PyQt5.QtWidgets import (QMessageBox)
from PyQt5 import uic

from .NodeDlg import NodeDlg
from .Errors import CharacterError
from .DomTools import DomTools

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "linkdlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a tag link
class LinkDlg(NodeDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(LinkDlg, self).__init__(parent)

        # link name
        self.name = u''
        # link target
        self.target = u''
        # field doc
        self.doc = u''

        # allowed subitems
        self.subItems = ["doc", "datasource", "strategy"]

        # user interface
        self.ui = _formclass()

    # updates the link dialog
    # \brief It sets the form local variables
    def updateForm(self):
        if self.name is not None:
            self.ui.nameLineEdit.setText(self.name)
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)

        if self.target is not None:
            self.ui.targetLineEdit.setText(self.target)

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):

        self.ui.setupUi(self)

        self.updateForm()

        self._updateUi()

        self.ui.resetPushButton.clicked.connect(self.reset)
        self.ui.nameLineEdit.textEdited[str].connect(
            self._updateUi)

    # provides the state of the link dialog
    # \returns state of the group in tuple
    def getState(self):

        state = (self.name,
                 self.target,
                 self.doc
                 )
        return state

    # sets the state of the link dialog
    # \param state link state written in tuple
    def setState(self, state):

        (self.name,
         self.target,
         self.doc
         ) = state

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            # defined in NodeDlg
            self.node = node
        if not self.node:
            return
        attributeMap = self.node.attributes()

        self.name = unicode(
            attributeMap.namedItem("name").nodeValue()
            if attributeMap.contains("name") else "")
        self.target = unicode(
            attributeMap.namedItem("target").nodeValue()
            if attributeMap.contains("target") else "")

        text = unicode(DomTools.getText(self.node)).strip()
        if text and text.startswith("$datasources."):
            self.target = text

        doc = self.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.doc = unicode(text).strip() if text else ""

    # updates link user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        enable = bool(self.ui.nameLineEdit.text())
        self.ui.applyPushButton.setEnabled(enable)

    # accepts input text strings
    # \brief It copies the link name and target from lineEdit widgets
    #        and accept the dialog
    def apply(self):
        name = unicode(self.ui.nameLineEdit.text())

        try:
            if 1 in [c in name for c in '!"#$%&\'()*+,/;<=>?@[\\]^`{|}~']:
                raise CharacterError(
                    "Name contains one of forbidden characters")
            if name[0] == '-':
                raise CharacterError(
                    "The first character of Name is '-'")

        except CharacterError as e:
            QMessageBox.warning(self, "Character Error", unicode(e))
            return
        self.name = name
        self.target = unicode(self.ui.targetLineEdit.text())

        self.doc = unicode(self.ui.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(
            index.row(), 2, index.parent().internalPointer())
        self.view.expand(index)

        if self.node and self.root and self.node.isElement():
            self.updateNode(index)

        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.model().dataChanged.emit(index, finalIndex)
        self.view.expand(index)

    # updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self, index=QModelIndex()):
        elem = self.node.toElement()
        mindex = self.view.currentIndex() if not index.isValid() else index

        attributeMap = self.node.attributes()
        for _ in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(0).nodeName())
        if self.name:
            elem.setAttribute(str("name"), str(self.name))
        self.replaceText(mindex)
        if self.target:
            if self.target.startswith("$datasources."):
                self.replaceText(mindex, unicode(self.target))
            else:
                elem.setAttribute(str("target"), str(self.target))

        doc = self.node.firstChildElement(str("doc"))
        if not self.doc and doc and doc.nodeName() == "doc":
            self.removeElement(doc, mindex)
        elif self.doc:
            newDoc = self.root.createElement(str("doc"))
            newText = self.root.createTextNode(str(self.doc))
            newDoc.appendChild(newText)
            if doc and doc.nodeName() == "doc":
                self.replaceElement(doc, newDoc, mindex)
            else:
                self.appendElement(newDoc, mindex)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # link form
    form = LinkDlg()
    form.name = 'data'
    form.target = '/NXentry/NXinstrument/NXdetector/data'
    form.createGUI()
    form.show()
    app.exec_()

    if form.name:
        logger.info("Link: %s = \'%s\'" % (form.name, form.target))
