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
# \file GroupDlg.py
# Group dialog class

""" group widget """

import copy
import os
import sys

from PyQt5.QtCore import (Qt, QModelIndex)
from PyQt5.QtWidgets import (QMessageBox, QTableWidgetItem, QCompleter)
from PyQt5 import uic

# from .ui.ui_groupdlg import Ui_GroupDlg
from .AttributeDlg import AttributeDlg
from .NodeDlg import NodeDlg
from .DomTools import DomTools

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "groupdlg.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a group tag
class GroupDlg(NodeDlg):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(GroupDlg, self).__init__(parent)

        # group name
        self.name = u''
        # group type
        self.nexusType = u''
        # group doc
        self.doc = u''
        # group attributes
        self.attributes = {}
        # group attributes
        self.__attributes = {}

        # allowed subitems
        self.subItems = ["group", "field", "attribute", "link",
                         "component", "doc"]

        # list of NeXus types
        self.typehelper = [
            'NXaperture',
            'NXattenuator',
            'NXbeam',
            'NXbeam_stop',
            'NXbending_magnet',
            'NXcapillary',
            'NXcharacterization',
            'NXcite',
            'NXcollection',
            'NXcollimator',
            'NXcrystal',
            'NXdata',
            'NXdetector_group',
            'NXdetector_module',
            'NXdetector',
            'NXdisk_chopper',
            'NXentry',
            'NXenvironment',
            'NXevent_data',
            'NXfermi_chopper',
            'NXfilter',
            'NXflipper',
            'NXfresnel_zone_plate',
            'NXgeometry',
            'NXgrating',
            'NXguide',
            'NXinsertion_device',
            'NXinstrument',
            'NXlog',
            'NXmirror',
            'NXmoderator',
            'NXmonitor',
            'NXmonochromator',
            'NXnote',
            'NXobject',
            'NXorientation',
            'NXparameters',
            'NXpinhole',
            'NXpolarizer',
            'NXpositioner',
            'NXprocess',
            'NXroot',
            'NXsample',
            'NXsensor',
            'NXshape',
            'NXslit',
            'NXsource',
            'NXsubentry',
            'NXtransformations',
            'NXtranslation',
            'NXuser',
            'NXvelocity_selector',
            'NXxraylens'
        ]

        # user interface
        self.ui = _formclass()

    # updates the group dialog
    # \brief It sets the form local variables
    def updateForm(self):

        if self.name is not None:
            self.ui.nameLineEdit.setText(self.name)
        if self.nexusType is not None:
            self.ui.typeLineEdit.setText(self.nexusType)
        if self.doc is not None:
            self.ui.docTextEdit.setText(self.doc)

        self.__attributes.clear()
        for at in self.attributes.keys():
            self.__attributes[unicode(at)] = self.attributes[(unicode(at))]

        self.populateAttributes()

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):
        self.ui.setupUi(self)
        completer = QCompleter(
            [str(tp) for tp in self.typehelper],
            self)
        self.ui.typeLineEdit.setCompleter(completer)
        self.updateForm()

        self.__updateUi()

        self.ui.resetPushButton.clicked.connect(self.reset)
        self.ui.attributeTableWidget.itemChanged.connect(
            self.__tableItemChanged)
        self.ui.addPushButton.clicked.connect(self.__addAttribute)
        self.ui.removePushButton.clicked.connect(self.__removeAttribute)

        self.ui.typeLineEdit.textEdited[str].connect(self.__updateUi)

    # provides the state of the group dialog
    # \returns state of the group in tuple
    def getState(self):
        attributes = copy.copy(self.attributes)

        state = (self.name,
                 self.nexusType,
                 self.doc,
                 attributes
                 )
        return state

    # sets the state of the group dialog
    # \param state group state written in tuple
    def setState(self, state):

        (self.name,
         self.nexusType,
         self.doc,
         attributes
         ) = state
        self.attributes = copy.copy(attributes)

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if node:
            # defined in NodeDlg class
            self.node = node
        if not self.node:
            # exception?
            return
        attributeMap = self.node.attributes()

        self.name = unicode(
            attributeMap.namedItem("name").nodeValue()
            if attributeMap.contains("name") else "")
        self.nexusType = unicode(
            attributeMap.namedItem("type").nodeValue()
            if attributeMap.contains("type") else "")

        self.attributes.clear()
        self.__attributes.clear()
        for i in range(attributeMap.count()):
            attribute = attributeMap.item(i)
            attrName = unicode(attribute.nodeName())
            if attrName != "name" and attrName != "type":
                self.attributes[attrName] = unicode(attribute.nodeValue())
                self.__attributes[attrName] = unicode(attribute.nodeValue())

        doc = self.node.firstChildElement(str("doc"))
        text = DomTools.getText(doc)
        self.doc = unicode(text).strip() if text else ""

    # adds an attribute
    #  \brief It runs the Group Dialog and fetches attribute name and value
    def __addAttribute(self):
        aform = AttributeDlg()
        if aform.exec_():
            if aform.name not in self.__attributes.keys():
                self.__attributes[aform.name] = aform.value
                self.populateAttributes(aform.name)
            else:
                QMessageBox.warning(
                    self, "Attribute name exists",
                    "To change the attribute value, please edit the value "
                    "in the attribute table")

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
    # \brief It changes the current value of the attribute
    #        and informs the user that attribute names arenot editable
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
        self.ui.attributeTableWidget.horizontalHeader()\
            .setStretchLastSection(True)
        if selected is not None:
            selected.setSelected(True)
            self.ui.attributeTableWidget.setCurrentItem(selected)

    # updates group user interface
    # \brief It sets enable or disable the OK button
    def __updateUi(self):
        enable = bool(self.ui.typeLineEdit.text())
        self.ui.applyPushButton.setEnabled(enable)

    # applys input text strings
    # \brief It copies the group name and type from lineEdit widgets
    #        and apply the dialog
    def apply(self):
        self.name = unicode(self.ui.nameLineEdit.text())
        self.nexusType = unicode(self.ui.typeLineEdit.text())

        self.doc = unicode(self.ui.docTextEdit.toPlainText())

        index = self.view.currentIndex()
        finalIndex = self.view.model().createIndex(
            index.row(), 2, index.parent().internalPointer())

        self.attributes.clear()
        for at in self.__attributes.keys():
            self.attributes[at] = self.__attributes[at]

        self.view.expand(index)

        if self.node and self.root and self.node.isElement():
            self.updateNode(index)
        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.expand(index)
        self.view.model().dataChanged.emit(index, finalIndex)

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
        if self.nexusType:
            elem.setAttribute(str("type"), str(self.nexusType))

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


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # group form
    form = GroupDlg()
    form.name = 'entry'
    form.nexusType = 'NXentry'
    form.doc = 'The main entry'
    form.attributes = {"title": "Test run 1", "run_cycle": "2012-1"}
    form.createGUI()
    form.show()
    app.exec_()

    if form.nexusType:
        logger.info("Group: name = \'%s\' type = \'%s\'" % (
            form.name, form.nexusType))
    if form.attributes:
        logger.info("Other attributes:")
        for k in form.attributes.keys():
            logger.info(" %s = '%s' " % (k, form.attributes[k]))
    if form.doc:
        logger.info("Doc: \n%s" % form.doc)
