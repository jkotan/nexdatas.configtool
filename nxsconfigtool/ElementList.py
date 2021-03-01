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
# \file ElementList.py
# Data source list class

""" datasource list widget """
import os
import sys

from PyQt5.QtCore import (Qt, )
from PyQt5.QtWidgets import (QWidget, QMenu, QMessageBox, QListWidgetItem,
                             QProgressDialog)
from PyQt5 import uic

# from .ui.ui_elementlist import Ui_ElementList
from .LabeledObject import LabeledObject


import logging
# message logger
logger = logging.getLogger("nxsdesigner")

_formclass, _baseclass = uic.loadUiType(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "ui", "elementlist.ui"))

if sys.version_info > (3,):
    unicode = str


# dialog defining a group tag
class ElementList(QWidget):

    # constructor
    # \param directory datasource directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ElementList, self).__init__(parent)
        # directory from which components are loaded by default
        self.directory = directory

        # group elements
        self.elements = {}

        # actions
        self._actions = []

        # user interface
        self.ui = _formclass()

        # widget title
        self.title = "Elements"
        # singular name
        self.clName = "Element"
        # class name
        self.name = "elements"
        # extention
        self.extention = ".xml"
        # excluded extention
        self.disextention = None

    #  creates GUI
    # \brief It calls setupUi and  connects signals and slots
    def createGUI(self):

        self.ui.setupUi(self)
        self.ui.elementTabWidget.setTabText(0, self.title)
        self.ui.elementListWidget.setEditTriggers(
            self.ui.elementListWidget.SelectedClicked)

        self.populateElements()

    # opens context Menu
    # \param position in the element list
    def _openMenu(self, position):
        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            elif isinstance(action, dict):
                for k in action:
                    submenu = menu.addMenu(k)
                    for saction in action[k]:
                        if saction is None:
                            submenu.addSeparator()
                        else:
                            submenu.addAction(saction)
            else:
                menu.addAction(action)
        menu.exec_(self.ui.elementListWidget.viewport().mapToGlobal(position))

    # sets context menu actions for the element list
    # \param actions tuple with actions
    def setActions(self, actions):
        self.ui.elementListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.elementListWidget.customContextMenuRequested.connect(
            self._openMenu)
        self._actions = actions

    # adds an element
    #  \brief It runs the Element Dialog and fetches element
    #         name and value
    def addElement(self, obj, flag=True):
        self.elements[obj.id] = obj
        self.populateElements(obj.id, flag)

    # takes a name of the current element
    # \returns name of the current element
    def currentListElement(self):
        item = self.ui.elementListWidget.currentItem()
        if item is not None \
           and item.data(Qt.UserRole) \
           in self.elements.keys():
            return self.elements[item.data(Qt.UserRole)]
        else:
            return None

    # sets focus into element list
    def setItemFocus(self):
        self.ui.elementListWidget.setFocus()

    # removes the current element
    #  \brief It removes the current element asking before about it
    def removeElement(self, obj=None, question=True):

        if obj is not None:
            oid = obj.id
        else:
            cds = self.currentListElement()
            if cds is None:
                return
            oid = cds.id
        if oid is None:
            return
        if oid in self.elements.keys():
            if question:
                if QMessageBox.question(
                    self, "%s - Close" % self.clName,
                    "Close %s: %s ".encode()
                    % (self.clName, self.elements[oid].name),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes) == QMessageBox.No:
                    return

            self.elements.pop(oid)
            self.populateElements()

    # changes the current value of the element
    # \brief It changes the current value of the element and informs
    #        the user that element names arenot editable
    def listItemChanged(self, item, name=None):
        cle = self.currentListElement()
        if cle:
            ide = cle.id
            if ide in self.elements.keys():
                old = self.elements[ide]
                oname = self.elements[ide].name
                if name is None:
                    self.elements[ide].name = unicode(item.text())
                else:
                    self.elements[ide].name = name
                self.populateElements()
                return old, oname
        return None, None

    # fills in the element list
    # \param selectedElement selected element
    # \param edit flag if edit the selected item
    def populateElements(self, selectedElement=None, edit=False):
        selected = None
        self.ui.elementListWidget.clear()

        slist = [(self.elements[key].name, key)
                 for key in self.elements.keys()]
        slist.sort()

        for name, el in slist:
            item = QListWidgetItem(str("%s" % name))
            item.setData(Qt.UserRole, (self.elements[el].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            dirty = False
            if hasattr(self.elements[el], "isDirty") \
                    and self.elements[el].isDirty():
                dirty = True
            if self.elements[el].instance is not None:
                if hasattr(self.elements[el].instance, "isDirty") \
                        and self.elements[el].instance.isDirty():
                    dirty = True
            if dirty:
                item.setForeground(Qt.red)
            else:
                item.setForeground(Qt.black)

            self.ui.elementListWidget.addItem(item)
            if selectedElement is not None \
                    and selectedElement == self.elements[el].id:
                selected = item

            if self.elements[el].instance is not None \
                    and self.elements[el].instance.dialog is not None:
                try:
                    if dirty:
                        self.elements[el].instance.dialog.\
                            setWindowTitle("%s [%s]*" % (name, self.clName))
                    else:
                        self.elements[el].instance.dialog.\
                            setWindowTitle("%s [%s]" % (name, self.clName))
                except Exception:
                    self.elements[el].instance.dialog = None

        if selected is not None:
            selected.setSelected(True)
            self.ui.elementListWidget.setCurrentItem(selected)
            if edit:
                self.ui.elementListWidget.editItem(selected)

    # sets the elements
    # \param elements dictionary with the elements, i.e. name:xml
    # \param externalActions dictionary with external actions
    # \param itemActions actions of the context menu
    # \param new logical variableset to True if element is not saved
    def setList(self, elements, externalActions=None,
                itemActions=None, new=False):
        if not os.path.isdir(self.directory):
            try:
                if os.path.exists(os.path.join(os.getcwd(), self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(), self.name))
                else:
                    self.directory = os.getcwd()
            except Exception:
                return

        ide = None
        keys = list(elements.keys())
        progress = QProgressDialog(
            "Setting %s elements" % self.clName,
            "", 0, len(keys), self)
        progress.setWindowTitle("Set Elements")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        for i in range(len(keys)):
            elname = keys[i]
            name = self.dashName(elname)
            dlg = self.createElement(name)
            try:
                if str(elements[elname]).strip():
                    dlg.set(elements[elname], new)
                else:
                    if hasattr(dlg, "createHeader"):
                        dlg.createHeader()
                    QMessageBox.warning(
                        self, "%s cannot be loaded" % self.clName,
                        "%s %s without content" % (self.clName, elname))
            except Exception:
                QMessageBox.warning(
                    self, "%s cannot be loaded" % self.clName,
                    "%s %s cannot be loaded" % (self.clName, elname))

            if hasattr(dlg, "dataSourceName"):
                dlg.dataSourceName = elname

            if hasattr(dlg, "addContextMenu"):
                dlg.addContextMenu(itemActions)

            if hasattr(dlg, "connectExternalActions"):
                actions = externalActions if externalActions else {}
                dlg.connectExternalActions(**actions)

            el = LabeledObject(name, dlg)
            if new:
                el.savedName = ""

            ide = id(el)
            self.elements[ide] = el
            if el.instance is not None:
                el.instance.id = el.id
                if new and hasattr(el.instance, "applied"):
                    el.instance.applied = True
            logger.info("setting %s" % name)
            progress.setValue(i)
        progress.setValue(len(keys))
        progress.close()
        return ide

    # replaces name special characters by underscore
    # \param name give name
    # \returns replaced element
    @classmethod
    def dashName(cls, name):
        return name

    # loads the element list from the given dictionary
    # \param externalActions dictionary with external actions
    # \param itemActions actions of the context menu
    def loadList(self, externalActions=None, itemActions=None):
        try:
            dirList = [
                el for el in os.listdir(self.directory)
                if (el.endswith(self.extention)
                    and (not self.disextention
                         or not el.endswith(self.disextention)))
            ]
        except Exception:
            try:
                if os.path.exists(os.path.join(os.getcwd(), self.name)):
                    self.directory = os.path.abspath(
                        os.path.join(os.getcwd(), self.name))
                else:
                    self.directory = os.getcwd()

                dirList = [
                    el for el in os.listdir(self.directory)
                    if (el.endswith(self.extention)
                        and (not self.disextention
                             or not el.endswith(self.disextention)))
                ]
            except Exception:
                return

        progress = QProgressDialog(
            "Loading %s elements" % self.clName,
            "", 0, len(dirList), self)
        progress.setWindowTitle("Load Elements")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.forceShow()
        for i in range(len(dirList)):
            fname = dirList[i]
            name = self.nameFromFile(fname)
            dlg = self.createElement(name)
            dlg.load()
            if hasattr(dlg, "addContextMenu"):
                dlg.addContextMenu(itemActions)

            actions = externalActions if externalActions else {}
            if hasattr(dlg, "connectExternalActions"):
                dlg.connectExternalActions(**actions)

            el = LabeledObject(name, dlg)
            self.elements[id(el)] = el
            if el.instance is not None:
                el.instance.id = el.id
            logger.info("loading %s" % name)
            progress.setValue(i)
        progress.setValue(len(dirList))
        progress.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # group form
    form = ElementList("../datasources")
#    form.elements={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()

    if form.elements:
        logger.info("Other datasources:")
        for kk in form.elements.keys():
            logger.info("%s = '%s' " % (kk, form.elements[kk]))
