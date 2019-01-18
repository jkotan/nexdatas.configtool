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
# \file StrategyDlg.py
# Strategy dialog class

""" strategy widget """

import os
import sys

from PyQt5.QtCore import (QModelIndex)
from PyQt5 import uic

# from .ui.ui_strategydlg import Ui_StrategyDlg
from .NodeDlg import NodeDlg
from .DomTools import DomTools

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "strategydlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining an attribute
class StrategyDlg(NodeDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(StrategyDlg, self).__init__(parent)

        # strategy mode
        self.mode = u''
        # trigger label
        self.trigger = u''
        # growing dimension
        self.grows = u''
        # postrun  label
        self.postrun = u''
        # attribute doc
        self.doc = u''
        # compression flag
        self.compression = False
        # compression rate
        self.rate = 5
        # compression shuffle
        self.shuffle = True

        # allowed subitems
        self.subItems = ["doc"]

        # writing can fail
        self.canfail = False

        # user interface
        self.ui = _formclass()

    # updates the field strategy
    # \brief It sets the form local variables
    def updateForm(self):
        index = -1
        if self.mode is not None:
            index = self.ui.modeComboBox.findText(unicode(self.mode))
            if index > -1:
                self.ui.modeComboBox.setCurrentIndex(index)
                self.setFrames(self.mode)
        if index < 0 or index is None:
            index2 = self.ui.modeComboBox.findText(unicode("STEP"))
            self.mode = 'STEP'
            self.ui.modeComboBox.setCurrentIndex(index2)
            self.setFrames(self.mode)

        if self.trigger is not None:
            self.ui.triggerLineEdit.setText(self.trigger)

        self.ui.compressionCheckBox.setChecked(self.compression)
        self.ui.canFailCheckBox.setChecked(self.canfail)
        self.ui.shuffleCheckBox.setChecked(self.shuffle)
        self.ui.rateSpinBox.setValue(self.rate)

        if self.grows is not None:
            try:
                grows = int(self.grows)
                if grows < 0:
                    grows = 0
            except Exception:
                grows = 0
            self.ui.growsSpinBox.setValue(grows)
        if self.postrun is not None:
            self.ui.postLineEdit.setText(self.postrun)
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        self.ui.setupUi(self)

        self.updateForm()

        self.ui.resetPushButton.clicked.connect(self.reset)
        self.ui.modeComboBox.currentIndexChanged[str].connect(self.setFrames)
        self.ui.compressionCheckBox.stateChanged[int].connect(
            self.setCompression)

        self.setCompression(self.ui.compressionCheckBox.isChecked())

    # provides the state of the strategy dialog
    # \returns state of the strategy in tuple
    def getState(self):
        state = (self.mode,
                 self.trigger,
                 self.grows,
                 self.postrun,
                 self.compression,
                 self.rate,
                 self.shuffle,
                 self.canfail,
                 self.doc
                 )
        return state

    # sets the state of the strategy dialog
    # \param state strategy state written in tuple
    def setState(self, state):

        (self.mode,
         self.trigger,
         self.grows,
         self.postrun,
         self.compression,
         self.rate,
         self.shuffle,
         self.canfail,
         self.doc
         ) = state

    # shows and hides frames according to modeComboBox
    # \param text the edited text
    def setFrames(self, text):
        if text == 'STEP':
            self.ui.triggerFrame.show()
            self.ui.postFrame.hide()
            self.ui.triggerLineEdit.setFocus()
        elif text == 'POSTRUN':
            self.ui.postFrame.show()
            self.ui.triggerFrame.hide()
            self.ui.postLineEdit.setFocus()
        else:
            self.ui.postFrame.hide()
            self.ui.triggerFrame.hide()

    # shows and hides compression widgets according to compressionCheckBox
    # \param state value from compressionCheckBox
    def setCompression(self, state):
        enable = bool(state)
        self.ui.rateLabel.setEnabled(enable)
        self.ui.rateSpinBox.setEnabled(enable)
        self.ui.shuffleCheckBox.setEnabled(enable)

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            # defined in NodeDlg class
            self.node = node
        if not self.node:
            return
        attributeMap = self.node.attributes()

        self.trigger = attributeMap.namedItem("trigger").nodeValue() \
            if attributeMap.contains("trigger") else ""
        self.grows = attributeMap.namedItem("grows").nodeValue() \
            if attributeMap.contains("grows") else ""
        self.mode = attributeMap.namedItem("mode").nodeValue() \
            if attributeMap.contains("mode") else ""

        if attributeMap.contains("canfail"):
            self.canfail = \
                False if str(attributeMap.namedItem("canfail").nodeValue()
                             ).upper() == "FALSE" else True

        if attributeMap.contains("compression"):
            self.compression = \
                False if str(attributeMap.namedItem("compression").nodeValue()
                             ).upper() == "FALSE" else True

            if attributeMap.contains("shuffle"):
                self.shuffle = \
                    False if str(attributeMap.namedItem("shuffle").nodeValue()
                                 ).upper() == "FALSE" else True

            if attributeMap.contains("rate"):
                rate = int(attributeMap.namedItem("rate").nodeValue())
                if rate < 0:
                    rate = 0
                elif rate > 9:
                    rate = 9
                self.rate = rate

        text = DomTools.getText(self.node)
        self.postrun = unicode(text).strip() if text else ""

        doc = self.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.doc = unicode(text).strip() if text else ""

    # accepts input text strings
    # \brief It copies the attribute name and value from
    #        lineEdit widgets and accept the dialog
    def apply(self):

        self.trigger = ''
        self.grows = ''
        self.postrun = ''

        self.mode = unicode(self.ui.modeComboBox.currentText())
        if self.mode == 'STEP':
            self.trigger = unicode(self.ui.triggerLineEdit.text())
            grows = int(self.ui.growsSpinBox.value())
            if grows > 0:
                self.grows = str(grows)
        if self.mode == 'POSTRUN':
            self.postrun = unicode(self.ui.postLineEdit.text())

        self.canfail = self.ui.canFailCheckBox.isChecked()
        self.compression = self.ui.compressionCheckBox.isChecked()
        self.shuffle = self.ui.shuffleCheckBox.isChecked()
        self.rate = self.ui.rateSpinBox.value()

        self.doc = unicode(self.ui.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(
            index.row(), 2, index.parent().internalPointer())

        self.view.expand(index)
        if self.node and self.root and self.node.isElement():
            self.updateNode(index)
        if index.column() != 0:
            index = self.view.model().index(
                index.row(), 0, index.parent())
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
        elem.setAttribute(str("mode"), str(self.mode))

        if self.mode == 'STEP':
            if self.trigger:
                elem.setAttribute(str("trigger"), str(self.trigger))
            if self.grows:
                elem.setAttribute(str("grows"), str(str(self.grows)))
        if self.canfail:
            elem.setAttribute(str("canfail"), str("true"))
        if self.compression:
            elem.setAttribute(str("compression"), str("true"))
            elem.setAttribute(str("shuffle"), str("true")
                              if self.shuffle else "false")
            elem.setAttribute(str("rate"), str(str(self.rate)))

        self.replaceText(mindex, unicode(self.postrun))

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
    # attribute form
    form = StrategyDlg()

    form.mode = "pre_sample_flightpath"
    form.trigger = "trigger1"
    form.postrun = 'http://haso.desy.de:/data/power.dat'
    form.doc = "This is the flightpath before the sample position."
    form.createGUI()
    form.show()
    app.exec_()

    if form.mode:
        logger.info("Mode: %s " % form.mode)
    if form.mode == "STEP":
        if form.trigger:
            logger.info("Trigger: %s" % form.trigger)
    if form.mode == "POSTRUN":
        if form.postrun:
            logger.info("Postrun label: %s" % form.postrun)
