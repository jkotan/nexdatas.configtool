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
# \file FieldDlg.py
# Field dialog class

""" field widget """

import copy

from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem)
from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5 import uic

import os
import sys

from .AttributeDlg import AttributeDlg
from .DimensionsDlg import DimensionsDlg
from .NodeDlg import NodeDlg
from .DomTools import DomTools

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "fielddlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a field tag
class FieldDlg(NodeDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(FieldDlg, self).__init__(parent)

        # field name
        self.name = u''
        # field type
        self.nexusType = u''
        # field units
        self.units = u''
        # field value
        self.value = u''
        # field doc
        self.doc = u''
        # field attributes
        self.attributes = {}
        self.__attributes = {}

        # rank
        self.rank = 0
        # dimensions
        self.dimensions = []
        self.__dimensions = []

        # allowed subitems
        self.subItems = ["attribute", "datasource", "doc", "dimensions",
                         "enumeration", "strategy"]

        # user interface
        self.ui = _formclass()

    # provides the state of the field dialog
    # \returns state of the field in tuple
    def getState(self):
        attributes = copy.copy(self.attributes)
        dimensions = copy.copy(self.dimensions)

        state = (self.name,
                 self.nexusType,
                 self.units,
                 self.value,
                 self.doc,
                 self.rank,
                 attributes,
                 dimensions
                 )
        return state

    # sets the state of the field dialog
    # \param state field state written in tuple
    def setState(self, state):

        (self.name,
         self.nexusType,
         self.units,
         self.value,
         self.doc,
         self.rank,
         attributes,
         dimensions
         ) = state
        self.attributes = copy.copy(attributes)
        self.dimensions = copy.copy(dimensions)

    # links dataSource
    # \param dsName datasource name
    def linkDataSource(self, dsName):
        self.value = "$%s.%s" % (self.dsLabel, dsName)
        self.updateForm()

    # updates the field dialog
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
        if self.units is not None:
            self.ui.unitsLineEdit.setText(self.units)
        if self.value is not None:
            self.ui.valueLineEdit.setText(self.value)

        if self.rank < len(self.dimensions):
            self.rank = len(self.dimensions)

        if self.dimensions:
            label = self.dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))
        elif self.rank > 0:
            label = ([None] * (self.rank)).__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))
        else:
            self.ui.dimLabel.setText("[]")

        self.__dimensions = []
        for dm in self.dimensions:
            self.__dimensions.append(dm)

        self.__attributes.clear()
        for at in self.attributes.keys():
            self.__attributes[unicode(at)] = self.attributes[(unicode(at))]

        self.populateAttributes()

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        self.ui.setupUi(self)

        self.updateForm()

        self.__updateUi()

        self.ui.resetPushButton.clicked.connect(self.reset)
        self.ui.attributeTableWidget.itemChanged.connect(
            self.__tableItemChanged)
        self.ui.addPushButton.clicked.connect(
            self.__addAttribute)
        self.ui.removePushButton.clicked.connect(
            self.__removeAttribute)
        self.ui.dimPushButton.clicked.connect(
            self.__changeDimensions)

        self.ui.nameLineEdit.textEdited[str].connect(
            self.__updateUi)
        self.ui.typeComboBox.currentIndexChanged[str].connect(
            self.__currentIndexChanged)

        self.populateAttributes()

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
        self.units = unicode(attributeMap.namedItem("units").nodeValue()
                             if attributeMap.contains("units") else "")

        text = DomTools.getText(self.node)
        self.value = unicode(text).strip() if text else ""

        self.attributes.clear()
        self.__attributes.clear()
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = unicode(attribute.nodeName())
            if attrName != "name" and attrName != "type" \
                    and attrName != "units":
                self.attributes[attrName] = unicode(attribute.nodeValue())
                self.__attributes[attrName] = unicode(attribute.nodeValue())

        dimens = self.node.firstChildElement(str("dimensions"))
        attributeMap = dimens.attributes()

        self.dimensions = []
        self.__dimensions = []
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
                            index = int(
                                attributeMap.namedItem("index").nodeValue())
                        if attributeMap.contains("value"):
                            value = str(
                                attributeMap.namedItem("value").nodeValue())
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
                            self.__dimensions.append(None)
                        self.__dimensions[index - 1] = value
                        self.dimensions[index - 1] = value

                child = child.nextSibling()

        if self.rank < len(self.dimensions):
            self.rank = len(self.dimensions)
            self.rank = len(self.__dimensions)
        elif self.rank > len(self.dimensions):
            self.dimensions.extend(
                [None] * (self.rank - len(self.dimensions)))
            self.__dimensions.extend(
                [None] * (self.rank - len(self.__dimensions)))

        doc = self.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.doc = unicode(text).strip() if text else ""

    # adds an attribute
    #  \brief It runs the Field Dialog and fetches attribute name and value
    def __addAttribute(self):
        aform = AttributeDlg()
        if aform.exec_():

            if aform.name not in self.__attributes.keys():
                self.__attributes[aform.name] = aform.value
                self.populateAttributes(aform.name)
            else:
                QMessageBox.warning(
                    self, "Attribute name exists",
                    "To change the attribute value, "
                    "please edit the value in the attribute table")

    # changing dimensions of the field
    #  \brief It runs the Dimensions Dialog and fetches rank
    #         and dimensions from it
    def __changeDimensions(self):
        dform = DimensionsDlg(self)
        dform.rank = self.rank
        dform.lengths = [ln for ln in self.__dimensions]
        dform.createGUI()
        if dform.exec_():
            self.rank = dform.rank
            if self.rank:
                self.__dimensions = [dm for dm in dform.lengths]
            else:
                self.__dimensions = []
            label = self.__dimensions.__str__()
            self.ui.dimLabel.setText("%s" % label.replace('None', '*'))

    # takes a name of the current attribute
    # \returns name of the current attribute
    def __currentTableAttribute(self):
        item = self.ui.attributeTableWidget.item(
            self.ui.attributeTableWidget.currentRow(), 0)
        if item is None:
            return None
        return item.data(Qt.UserRole)

    # removes an attribute
    #  \brief It removes the current attribute asking before about it
    def __removeAttribute(self):
        attr = self.__currentTableAttribute()
        if attr is None:
            return
        if unicode(attr) in self.__attributes.keys():
            self.__attributes.pop(unicode(attr))
            self.populateAttributes()

    # changes the current value of the attribute
    # \brief It changes the current value of the attribute and informs
    #        the user that attribute names arenot editable
    def __tableItemChanged(self, item):
        attr = self.__currentTableAttribute()
        if unicode(attr) not in self.__attributes.keys():
            return
        column = self.ui.attributeTableWidget.currentColumn()
        if column == 1:
            self.__attributes[unicode(attr)] = unicode(item.text())
        if column == 0:
            QMessageBox.warning(
                self, "Attribute name is not editable",
                "To change the attribute name, "
                "please remove the attribute and add the new one")
        self.populateAttributes()

    # fills in the attribute table
    # \param selectedAttribute selected attribute
    def populateAttributes(self, selectedAttribute=None):
        selected = None
        self.ui.attributeTableWidget.clear()
        self.ui.attributeTableWidget.setSortingEnabled(False)
        self.ui.attributeTableWidget.setRowCount(len(self.__attributes))
        headers = ["Name", "Value"]
        self.ui.attributeTableWidget.setColumnCount(len(headers))
        self.ui.attributeTableWidget.setHorizontalHeaderLabels(headers)
        for row, name in enumerate(self.__attributes):
            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, (name))
            self.ui.attributeTableWidget.setItem(row, 0, item)
            item2 = QTableWidgetItem(self.__attributes[name])
            self.ui.attributeTableWidget.setItem(row, 1, item2)
            if selectedAttribute is not None and selectedAttribute == name:
                selected = item2
        self.ui.attributeTableWidget.setSortingEnabled(True)
        self.ui.attributeTableWidget.resizeColumnsToContents()
        self.ui.attributeTableWidget.horizontalHeader().\
            setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.attributeTableWidget.setCurrentItem(selected)

    # calls updateUi when the name text is changing
    # \param text the edited text
    def __currentIndexChanged(self, text):
        if text == 'other ...':
            self.ui.otherFrame.show()
            self.ui.typeLineEdit.setFocus()
        else:
            self.ui.otherFrame.hide()

    # updates field user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        enable = bool(self.ui.nameLineEdit.text())
        self.ui.applyPushButton.setEnabled(enable)

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
                        self,
                        "%s exists" % singles[str(newElement.nodeName())],
                        "To add a new %s please remove the old one"
                        % newElement.nodeName())
                    return False
                child = child.nextSibling()

        return NodeDlg.appendElement(self, newElement, parent)

    # applys input text strings
    # \brief It copies the field name and type from lineEdit widgets
    #        and apply the dialog
    def apply(self):
        self.name = unicode(self.ui.nameLineEdit.text())
        self.units = unicode(self.ui.unitsLineEdit.text())
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

        self.attributes.clear()
        for at in self.__attributes.keys():
            self.attributes[at] = self.__attributes[at]

        self.dimensions = []
        for dm in self.__dimensions:
            self.dimensions.append(dm)

        if self.node and self.root and self.node.isElement():
            self.updateNode(index)

        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.expand(index)
        self.view.model().dataChanged.emit(index, finalIndex)
        self.view.model().dataChanged.emit(index, index)

    # updates the Node
    # \brief It sets node from the dialog variables
    def updateNode(self, index=QModelIndex()):
        elem = self.node.toElement()

        mindex = self.view.currentIndex() if not index.isValid() else index

        attributeMap = self.node.attributes()
        for i in range(attributeMap.count()):
            attributeMap.removeNamedItem(attributeMap.item(0).nodeName())
        if self.name:
            elem.setAttribute(str("name"), str(self.name))
        if self.nexusType:
            elem.setAttribute(str("type"), str(self.nexusType))
        if self.units:
            elem.setAttribute(str("units"), str(self.units))

        self.replaceText(mindex, unicode(self.value))

        for attr in self.attributes.keys():
            elem.setAttribute(str(attr), str(self.attributes[attr]))

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
                        dstrategy.setAttribute(
                            str("mode"),
                            str(unicode("CONFIG")))
                        dim.appendChild(dsText)
                        dim.appendChild(dstrategy)

                    newDimens.appendChild(dim)

            if dimens and dimens.nodeName() == "dimensions":
                self.replaceElement(dimens, newDimens, mindex)
            else:
                self.appendElement(newDimens, mindex)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # field form
    form = FieldDlg()
    form.name = 'distance'
    form.nexusType = 'NX_FLOAT'
    form.units = 'cm'
    form.attributes = {"signal": "1",
                       "long_name": "source detector distance",
                       "interpretation": "spectrum"}
    form.doc = """Distance between the source and the mca detector.
It should be defined by client."""
    form.dimensions = [3]
    form.value = "1.23,3.43,4.23"
    form.createGUI()
    form.show()
    app.exec_()
    if form.name:
        logger.info("Field: name = \'%s\'" % (form.name))
    if form.nexusType:
        logger.info("       type = \'%s\'" % (form.nexusType))
    if form.units:
        logger.info("       units = \'%s\'" % (form.units))
    if form.attributes:
        logger.info("Other attributes:")
        for k in form.attributes.keys():
            logger.info(" %s = '%s' " % (k, form.attributes[k]))
    if form.value:
        logger.info("Value:\n \'%s\'" % (form.value))
    if form.rank:
        logger.info(" rank = %s" % (form.rank))
    if form.dimensions:
        logger.info("Dimensions:")
        for mrow, mln in enumerate(form.dimensions):
            logger.info(" %s: %s " % (mrow + 1, mln))

    if form.doc:
        logger.info("Doc: \n%s" % form.doc)
