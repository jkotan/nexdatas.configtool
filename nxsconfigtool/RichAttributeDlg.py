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
# \file RichAttributeDlg.py
# Rich Attribute dialog class

""" attribute widget """

import copy
import os

from PyQt5.QtCore import (QModelIndex)
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import uic

from .NodeDlg import NodeDlg
from .DimensionsDlg import DimensionsDlg
from .Errors import CharacterError
from .DomTools import DomTools

import logging
import sys
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "richattributedlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining an attribute
class RichAttributeDlg(NodeDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(RichAttributeDlg, self).__init__(parent)

        # attribute name
        self.name = u''
        # attribute value
        self.value = u''
        # attribute type
        self.nexusType = u''
        # attribute doc
        self.doc = u''

        # rank
        self.rank = 0
        # dimensions
        self.dimensions = []
        self._dimensions = []

        # allowed subitems
        self.subItems = ["enumeration", "doc", "datasource",
                         "strategy", "dimensions"]

        # user interface
        self.ui = _formclass()

    # provides the state of the richattribute dialog
    # \returns state of the richattribute in tuple
    def getState(self):
        dimensions = copy.copy(self.dimensions)

        state = (self.name,
                 self.value,
                 self.nexusType,
                 self.doc,
                 self.rank,
                 dimensions
                 )
        return state

    # sets the state of the richattribute dialog
    # \param state richattribute state written in tuple
    def setState(self, state):

        (self.name,
         self.value,
         self.nexusType,
         self.doc,
         self.rank,
         dimensions
         ) = state
        self.dimensions = copy.copy(dimensions)

    # links dataSource
    # \param dsName datasource name
    def linkDataSource(self, dsName):
        self.value = "$%s.%s" % (self.dsLabel, dsName)
        self.updateForm()

    # updates the richattribute dialog
    # \brief It sets the form local variables
    def updateForm(self):
        if self.name is not None:
            self.ui.nameLineEdit.setText(self.name)
        if self.nexusType is not None:
            index = self.ui.typeComboBox.findText(unicode(self.nexusType))
            if index > -1:
                self.ui.typeComboBox.setCurrentIndex(index)
                self.ui.otherFrame.hide()
            else:
                index2 = self.ui.typeComboBox.findText('other ...')
                self.ui.typeComboBox.setCurrentIndex(index2)
                self.ui.typeLineEdit.setText(self.nexusType)
                self.ui.otherFrame.show()
        else:
            index = self.ui.typeComboBox.findText(unicode("None"))
            self.ui.typeComboBox.setCurrentIndex(index)
            self.ui.otherFrame.hide()

        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)
        if self.value is not None:
            self.ui.valueLineEdit.setText(self.value)

        if self.rank < len(self.dimensions):
            self.rank = len(self.dimensions)

        if self.dimensions:
            label = self.dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))
        elif self.rank > 0:
            label = ([None] * self.rank).__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))
        else:
            self.ui.dimLabel.setText("[]")

        self._dimensions = []
        for dm in self.dimensions:
            self._dimensions.append(dm)

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        self.ui.setupUi(self)

        self.updateForm()

        self._updateUi()

        self.ui.resetPushButton.clicked.connect(self.reset)

        self.ui.nameLineEdit.textEdited[str].connect(self._updateUi)
        self.ui.typeComboBox.currentIndexChanged[str].connect(
            self._currentIndexChanged)
        self.ui.dimPushButton.clicked.connect(self._changeDimensions)

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            # defined in NodeDlg
            self.node = node
        if not self.node:
            return
        attributeMap = self.node.attributes()

        self.name = unicode(attributeMap.namedItem("name").nodeValue()
                            if attributeMap.contains("name") else "")
        self.nexusType = unicode(attributeMap.namedItem("type").nodeValue()
                                 if attributeMap.contains("type") else "")

        text = DomTools.getText(self.node)
        self.value = unicode(text).strip() if text else ""

        dimens = self.node.firstChildElement(str("dimensions"))
        attributeMap = dimens.attributes()

        self.dimensions = []
        self._dimensions = []
        if attributeMap.contains("rank"):
            try:
                self.rank = int(attributeMap.namedItem("rank").nodeValue())
                if self.rank < 0:
                    self.rank = 0
            except Exception:
                self.rank = 0
        else:
            self.rank = 0
        if self.rank > 0:
            child = dimens.firstChild()
            while not child.isNull():
                if child.isElement() and child.nodeName() == "dim":
                    attributeMap = child.attributes()
                    index = None
                    value = None
                    try:
                        if attributeMap.contains("index"):
                            index = int(attributeMap.namedItem(
                                "index").nodeValue())
                        if attributeMap.contains("value"):
                            value = str(attributeMap.namedItem(
                                "value").nodeValue())
                    except Exception:
                        pass
                    text = DomTools.getText(child)
                    if text and "$datasources." in text:
                        value = str(text).strip()
                    if index < 1:
                        index = None
                    if index is not None:
                        while len(self.dimensions) < index:
                            self.dimensions.append(None)
                            self._dimensions.append(None)
                        self._dimensions[index - 1] = value
                        self.dimensions[index - 1] = value

                child = child.nextSibling()

        if self.rank < len(self.dimensions):
            self.rank = len(self.dimensions)
            self.rank = len(self._dimensions)
        elif self.rank > len(self.dimensions):
            self.dimensions.extend(
                [None] * (self.rank - len(self.dimensions)))
            self._dimensions.extend(
                [None] * (self.rank - len(self._dimensions)))

        doc = self.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.doc = unicode(text).strip() if text else ""

    # changing dimensions of the field
    #  \brief It runs the Dimensions Dialog and fetches rank
    #         and dimensions from it
    def _changeDimensions(self):
        dform = DimensionsDlg(self)
        dform.rank = self.rank
        dform.lengths = [ln for ln in self._dimensions]
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            if self.rank:
                self._dimensions = [ln for ln in dform.lengths]
            else:
                self._dimensions = []
            label = self._dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))

    # calls updateUi when the name text is changing
    # \param text the edited text
    def _currentIndexChanged(self, text):
        if text == 'other ...':
            self.ui.otherFrame.show()
            self.ui.typeLineEdit.setFocus()
        else:
            self.ui.otherFrame.hide()

    # updates attribute user interface
    # \brief It sets enable or disable the OK button
    def _updateUi(self):
        enable = bool(self.ui.nameLineEdit.text())
        self.ui.applyPushButton.setEnabled(enable)

    # accepts input text strings
    # \brief It copies the attribute name and value from lineEdit widgets
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
        self.value = unicode(self.ui.valueLineEdit.text())

        self.nexusType = unicode(self.ui.typeComboBox.currentText())
        if self.nexusType == 'other ...':
            self.nexusType = unicode(self.ui.typeLineEdit.text())
        elif self.nexusType == 'None':
            self.nexusType = u''

        self.doc = unicode(self.ui.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(
            index.row(), 2, index.parent().internalPointer())
        self.view.expand(index)

        self.dimensions = []
        for dm in self._dimensions:
            self.dimensions.append(dm)

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
        for i in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(0).nodeName())
        elem.setAttribute(str("name"), str(self.name))
        if self.nexusType:
            elem.setAttribute(str("type"), str(self.nexusType))

        self.replaceText(mindex, unicode(self.value))

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

        dimens = self.node.firstChildElement(str("dimensions"))
        if not self.dimensions and dimens \
                and dimens.nodeName() == "dimensions":
            self.removeElement(dimens, mindex)
        elif self.dimensions:
            newDimens = self.root.createElement(str("dimensions"))
            newDimens.setAttribute(str("rank"),
                                   str(unicode(self.rank)))
            dimDefined = True
            for i in range(min(self.rank, len(self.dimensions))):
                if self.dimensions[i] is None:
                    dimDefined = False
            if dimDefined:
                for i in range(min(self.rank, len(self.dimensions))):
                    dim = self.root.createElement(str("dim"))
                    dim.setAttribute(str("index"), str(unicode(i + 1)))
                    if "$datasources." not in unicode(self.dimensions[i]):

                        dim.setAttribute(str("value"),
                                         str(unicode(self.dimensions[i])))
                    else:
                        dsText = self.root.createTextNode(
                            str(unicode(self.dimensions[i])))
                        dstrategy = self.root.createElement(
                            str("strategy"))
                        dstrategy.setAttribute(str("mode"),
                                               str(unicode("CONFIG")))
                        dim.appendChild(dsText)
                        dim.appendChild(dstrategy)
                    newDimens.appendChild(dim)

            if dimens and dimens.nodeName() == "dimensions":
                self.replaceElement(dimens, newDimens, mindex)
            else:
                self.appendElement(newDimens, mindex)

    # appends newElement
    # \param newElement DOM node to append
    # \param parent parent DOM node
    def appendElement(self, newElement, parent):
        singles = {"datasource": "DataSource", "strategy": "Strategy"}
        if unicode(newElement.nodeName()) in singles:
            if not self.node:
                return
            child = self.node.firstChild()
            while not child.isNull():
                if child.nodeName() == unicode(newElement.nodeName()):
                    QMessageBox.warning(
                        self, "%s exists" % singles[
                            str(newElement.nodeName())],
                        "To add a new %s please remove the old one"
                        % newElement.nodeName())
                    return False
                child = child.nextSibling()

        return NodeDlg.appendElement(self, newElement, parent)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # attribute form
    form = RichAttributeDlg()
    form.name = "pre_sample_flightpath"
    form.nexusType = 'NX_FLOAT'
    form.doc = "This is the flightpath before the sample position."
    form.value = "1.2"
    form.createGUI()
    form.show()
    app.exec_()

    if form.name:
        logger.info("Attribute: %s = \'%s\'" % (form.name, form.value))
    if form.nexusType:
        logger.info("Type: %s" % form.nexusType)
    if form.doc:
        logger.info("Doc: \n%s" % form.doc)
