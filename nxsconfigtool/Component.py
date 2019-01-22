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
# \file Component.py
# component classes

""" component widget data """

import os
import sys

from PyQt5.QtCore import (QModelIndex, Qt,
                          QFileInfo, QFile, QIODevice, QTextStream)
from PyQt5.QtWidgets import (QWidget, QGridLayout, QApplication,
                             QMenu, QFileDialog, QMessageBox)
from PyQt5.QtXml import (QDomDocument)


from .FieldDlg import FieldDlg
from .GroupDlg import GroupDlg
from .LinkDlg import LinkDlg
from .RichAttributeDlg import RichAttributeDlg
from .DataSourceDlg import DataSourceDlg
from .StrategyDlg import StrategyDlg
from .DefinitionDlg import DefinitionDlg
from .Merger import Merger, MergerDlg, IncompatibleNodeError
from .ComponentModel import ComponentModel
from .DomTools import DomTools
from .ComponentDlg import ComponentDlg

import logging
# message logger
logger = logging.getLogger("nxsdesigner")

if sys.version_info > (3,):
    unicode = str


# Component data
class Component(object):

    # constructor
    # \brief Sets variables
    def __init__(self, parent=None):

        # directory from which components are loaded by default
        self.directory = ""
        # component view
        self.view = None
        # component id
        self.id = None
        # component name
        self.name = ""
        # component dialog
        self.dialog = None
        # component DOM document
        self.document = None
        # parent node
        self.parent = parent

        if os.path.exists(os.path.join(os.getcwd(), "components")):
            self._xmlPath = os.path.abspath(os.path.join(
                os.getcwd(), "components"))
        else:
            self._xmlPath = os.getcwd()

        if os.path.exists(os.path.join(os.getcwd(), "datasources")):
            self._dsPath = os.path.abspath(os.path.join(
                os.getcwd(), "datasources"))
        else:
            self._dsPath = os.getcwd()

        self._componentFile = None

#        # item frame
#        self.frame = None
        # component actions
        self._actions = None

        # save action
        self.externalSave = None
        # strore action
        self.externalStore = None
        # apply action
        self.externalApply = None
        # close action
        self.externalClose = None
        # datasource link action
        self.externalDSLink = None

        # item class shown in the frame
        self._tagClasses = {"field": FieldDlg,
                            "group": GroupDlg,
                            "definition": DefinitionDlg,
                            "attribute": RichAttributeDlg,
                            "link": LinkDlg,
                            "datasource": DataSourceDlg,
                            "strategy": StrategyDlg
                            }

        # current component tag
        self._currentTag = None
        self._frameLayout = None

        # if merging compited
        self._merged = False

        # merger dialog
        self._mergerdlg = None

        # merger
        self._merger = None

        # show all attribures or only the type attribute
        self._allAttributes = False

        # saved XML
        self.savedXML = None

        # tag counter
        self._tagCnt = 0

        # sub components
        self.components = []
        # sub datasources
        self.datasources = []

    # fetches $datasources and $components from xml
    # \brief populate components and datasources
    def fetchElements(self):
        dss = set()
        cps = set()
        if hasattr(self.document, "toString"):
            xml = unicode(self.document.toString(0))
            dss = set(DomTools.findElements(xml, "datasources"))
            cps = set(DomTools.findElements(xml, "components"))
        self.components = list(cps)
        self.datasources = list(dss)

    # provides attribute flag
    # \returns flag if all attributes have to be shown
    def getAttrFlag(self):
        return self._allAttributes

    # checks if not saved
    # \returns True if it is not saved
    def isDirty(self):
        string = self.get()
        return False if string == self.savedXML else True

    # provides the path of component tree for a given node
    # \param node DOM node
    # \returns path represented as a list with elements:
    #         (row number, node name)
    @classmethod
    def _getPathFromNode(cls, node):
        ancestors = [node]
        path = []

        while unicode(
            ancestors[0].parentNode().nodeName()).strip() != '#document' and \
                unicode(ancestors[0].parentNode().nodeName()).strip() != '':
            ancestors.insert(0, ancestors[0].parentNode())
        ancestors.insert(0, ancestors[0].parentNode())

        parent = None
        for child in ancestors:
            if parent:
                row = DomTools.getNodeRow(child, parent)

                if row is None:
                    path = []
                    break

                path.append((row, unicode(child.nodeName())))
            parent = child
        if not path:
            path = [(0, 'definition')]
        return path

    # provides the current component tree item
    # \returns DOM node instance
    def _getCurrentNode(self):
        index = QModelIndex()
        if self.view and self.dialog:
            index = self.view.currentIndex()
        if not index.isValid():
            return
        item = index.internalPointer()
        if not item:
            return
        return item.node

    # provides the current view index
    # \returns the current view index
    def currentIndex(self):
        index = QModelIndex()
        if self.view and self.dialog:
            try:
                index = self.view.currentIndex()
            except Exception:
                pass
        return index

    # provides the path of component tree for the current component tree item
    # \returns path represented as a list with elements:
    #          (row number, node name)
    def _getPath(self):
        index = self.currentIndex()
        pindex = index.parent()
        path = []
        if not index.isValid():
            return
        row = 1
        while pindex.isValid() and row is not None:
            child = index.internalPointer().node
            parent = pindex.internalPointer().node
            row = DomTools.getNodeRow(child, parent)
            path.insert(0, (row, unicode(child.nodeName())))
            index = pindex
            pindex = pindex.parent()

        child = index.internalPointer().node
        row = DomTools.getNodeRow(child, self.document)
        path.insert(0, (row, unicode(child.nodeName())))

        return path

    # selects and opens the last nodes of the given list in the component tree
    # \param nodes list of DOM nodes
    def _showNodes(self, nodes):
        for node in nodes:
            path = self._getPathFromNode(node)
            self._selectItem(path)

    # provides  index of the component item defined by the path
    # \param path path represented as a list with elements:
    #        (row number, node name)
    # \returns component item index
    def _getIndex(self, path):
        if not path or not self.view or not self.dialog:
            return QModelIndex()
        index = self.view.model().rootIndex
        self.view.expand(index)
        for step in path:
            index = self.view.model().index(step[0], 0, index)
            self.view.expand(index)
        return index

    # selectes item defined by path in component tree
    # \param path path represented as a list with elements:
    #        (row number, node name)
    def _selectItem(self, path):
        index = self._getIndex(path)

        if index and index.isValid():
            self.view.setCurrentIndex(index)
            self.tagClicked(index)
            self.view.expand(index)

    # provides the state of the component dialog
    # \returns tuple with (xml string, path)
    def getState(self):
        path = self._getPath()
        return (self.document.toString(0), path)

    # sets the state of the component dialog
    # \param state tuple with (xml string, path)
    def setState(self, state):
        (xml, path) = state
        try:
            self._loadFromString(xml)
        except (IOError, OSError, ValueError) as e:
            error = "Failed to load: %s" % e
            logger.warn(error)
        self._hideFrame()
        self._selectItem(path)

    # updates the component dialog
    # \brief It creates model and frame item
    def updateForm(self):
        self.dialog.ui.splitter.setStretchFactor(0, 1)
        self.dialog.ui.splitter.setStretchFactor(1, 1)

        model = ComponentModel(self.document, self._allAttributes, self.parent)
        self.view.setModel(model)
        self.connectView()

        self.dialog.ui.widget = QWidget(self.dialog)
        self._frameLayout = QGridLayout()
        self._frameLayout.addWidget(self.dialog.ui.widget)
        self.dialog.ui.frame.setLayout(self._frameLayout)

    # applies component item
    # \brief it checks if item widget exists and calls apply of the item widget
    def applyItem(self):
        if not self.view or not self.view.model() or not self.dialog \
                or not self.dialog.ui or not self.dialog.ui.widget:
            return
        if not hasattr(self.dialog.ui.widget, 'apply'):
            return
#        import gc
#        gc.collect()
        self.dialog.ui.widget.apply()

        self.view.resizeColumnToContents(0)
        self.view.resizeColumnToContents(1)
        self.fetchElements()
        return True

    # moving node up
    # \param node DOM node
    # \param parent parent node index
    # \returns the new row number if changed otherwise None
    def _moveNodeUp(self, node, parent):
        if self.view is not None and self.dialog is not None \
                and self.view.model() is not None:
            if not parent.isValid():
                return
            parentItem = parent.internalPointer()
            pnode = parentItem.node
            row = DomTools.getNodeRow(node, pnode)
            if row is not None and row != 0:
                self.view.model().removeItem(row, parent)
                self.view.model().insertItem(row - 1, node, parent)
                return row - 1

    # moving node down
    # \param node DOM node
    # \param parent parent node index
    # \returns the new row number if changed otherwise None
    def _moveNodeDown(self, node, parent):
        if self.view is not None and self.dialog is not None \
                and self.view.model() is not None:
            if not parent.isValid():
                return
            parentItem = parent.internalPointer()
            pnode = parentItem.node
            row = DomTools.getNodeRow(node, pnode)
            if row is not None and row < pnode.childNodes().count() - 1:
                self.view.model().removeItem(row, parent)
                if row < pnode.childNodes().count() - 1:
                    self.view.model().insertItem(row + 1, node, parent)
                else:
                    self.view.model().appendItem(node, parent)
                return row + 1

    # moves component item up
    # \returns the new row number if item move othewise None
    def moveUpItem(self):
        if not self.view or not self.dialog or not self.view.model():
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node
        parent = index.parent()
        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, parent)
        row = self._moveNodeUp(node, parent)
        if row is not None:
            index = self.view.model().index(row, 0, parent)
            self.view.setCurrentIndex(index)
            self.view.model().dataChanged.emit(index, index)
            self.view.model().dataChanged.emit(parent, parent)
            return row

    # moves component item up
    # \returns the new row number if item move othewise None
    def moveDownItem(self):
        if not self.view or not self.dialog or not self.view.model():
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node
        parent = index.parent()
        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, parent)
        row = self._moveNodeDown(node, parent)
        if row is not None:
            index = self.view.model().index(row, 0, parent)
            self.view.setCurrentIndex(index)
            self.view.model().dataChanged.emit(index, index)
            self.view.model().dataChanged.emit(parent, parent)
            return row

    # converts DOM node to XML string
    # \param component DOM node
    # \returns XML string
    @classmethod
    def _nodeToString(cls, node):
        doc = QDomDocument()
        child = doc.importNode(node, True)
        doc.appendChild(child)
        return unicode(doc.toString(0))

    # converts XML string to DOM node
    # \param xml XML string
    # \returns component DOM node
    def _stringToNode(self, xml):
        doc = QDomDocument()

        if not unicode(xml).strip():
            return
        if not doc.setContent(unicode(xml).strip()):
            raise ValueError("could not parse XML")
        if self.document and doc and doc.hasChildNodes():
            return self.document.importNode(doc.firstChild(), True)

    # pastes the component item from the clipboard into the component tree
    # \returns True on success
    def pasteItem(self):
        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget \
                or not hasattr(self.dialog.ui.widget, "subItems"):
            return

        clipboard = QApplication.clipboard()
        clipNode = self._stringToNode(clipboard.text())
        if clipNode is None:
            return

        name = unicode(clipNode.nodeName())

        if name not in self.dialog.ui.widget.subItems:
            return

        index = self.view.currentIndex()
        if not index.isValid():
            return
        sel = index.internalPointer()
        if not sel:
            return

        node = sel.node

        self.dialog.ui.widget.node = node
        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.dialog.ui.widget.appendElement(clipNode, index)

        self.view.model().dataChanged.emit(index, index)

        self.view.expand(index)
        self.fetchElements()
        return True

    # creates the component item with the given name in the component tree
    # \param name component item name
    # \returns component DOM node related to the new item
    def addItem(self, name):
        if name not in self._tagClasses.keys():
            return
        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget:
            return
        if not hasattr(self.dialog.ui.widget, 'subItems') \
                or name not in self.dialog.ui.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node
        self.dialog.ui.widget.node = node
        child = self.dialog.ui.widget.root.createElement(str(name))
        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        status = self.dialog.ui.widget.appendElement(child, index)
        self.view.model().dataChanged.emit(index, index)
        self.view.expand(index)
        self.fetchElements()
        if status:
            return child

    # removes the currenct component tree item if possible
    # \returns True on success
    def removeSelectedItem(self):

        if not self.view or not self.view.model():
            return
        dialog = True if self.dialog and self.dialog.ui \
            and self.dialog.ui.widget else False
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return

        node = sel.node

        clipboard = QApplication.clipboard()
        clipboard.setText(self._nodeToString(node))

        if hasattr(self.dialog.ui.widget, "node") and dialog:
            self.dialog.ui.widget.node = node.parentNode()

        if self.view is not None and self.view.model() is not None:
            DomTools.removeNode(node, index.parent(), self.view.model())

        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.model().dataChanged.emit(index, index)
        if index.parent().isValid():
            self.view.model().dataChanged.emit(
                index.parent(), index.parent())

            index = self.view.currentIndex()
            self.tagClicked(index)
        else:
            self.tagClicked(QModelIndex())

        self.fetchElements()
        return True

    # copies the currenct component tree item if possible
    # \returns True on success
    def copySelectedItem(self):
        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return

        node = sel.node

        clipboard = QApplication.clipboard()
        clipboard.setText(self._nodeToString(node))
        self.fetchElements()
        return True

    # creates GUI
    # It calls setupUi and creates required action connections
    def createGUI(self):
        self.dialog = ComponentDlg(self, self.parent)
        self.dialog.ui.setupUi(self.dialog)
        self.view = self.dialog.ui.view

        self.updateForm()
        self.connectView()

    # connects the view and model into resize and click command
    def connectView(self):
        try:
            self.view.selectionModel().currentChanged.disconnect(
                self.tagClicked)
        except Exception:
            pass
        self.view.selectionModel().currentChanged.connect(
            self.tagClicked)
        # self.dialog.disconnect(
        #     self.view.selectionModel(),
        #     SIGNAL("currentChanged(QModelIndex,QModelIndex)"),
        #     self.tagClicked)
        # self.parent.connect(
        #     self.view.selectionModel(),
        #     SIGNAL("currentChanged(QModelIndex,QModelIndex)"),
        #     self.tagClicked)
        try:
            self.view.expanded.disconnect(self._resizeColumns)
        except Exception:
            pass
        self.view.expanded.connect(self._resizeColumns)
        # self.dialog.disconnect(
        #     self.view, SIGNAL("expanded(QModelIndex)"),
        #     self._resizeColumns)
        # self.parent.connect(
        #     self.view, SIGNAL("expanded(QModelIndex)"),
        #     self._resizeColumns)
        try:
            self.view.collapsed.disconnect(self._resizeColumns)
        except Exception:
            pass
        self.view.collapsed.connect(self._resizeColumns)
        # self.dialog.disconnect(
        #     self.view, SIGNAL("collapsed(QModelIndex)"),
        #     self._resizeColumns)
        # self.parent.connect(
        #     self.view, SIGNAL("collapsed(QModelIndex)"),
        #     self._resizeColumns)

    # connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    # \param externalDSLink dsource link action
    def connectExternalActions(self, externalApply=None, externalSave=None,
                               externalClose=None, externalStore=None,
                               externalDSLink=None):
        if externalSave and self.externalSave is None:
            self.dialog.ui.savePushButton.clicked.connect(
                externalSave)
            # self.parent.connect(
            #     self.dialog.ui.savePushButton, SIGNAL("clicked()"),
            #     externalSave)
            self.externalSave = externalSave
        if externalStore and self.externalStore is None:
            self.dialog.ui.storePushButton.clicked.connect(
                externalStore)
            # self.parent.connect(
            #     self.dialog.ui.storePushButton, SIGNAL("clicked()"),
            #     externalStore)
            self.externalStore = externalStore
        if externalClose and self.externalClose is None:
            self.dialog.ui.closePushButton.clicked.connect(
                externalClose)
            # self.parent.connect(
            #     self.dialog.ui.closePushButton, SIGNAL("clicked()"),
            #     externalClose)
            self.externalClose = externalClose
        if externalApply and self.externalApply is None:
            self.externalApply = externalApply
        if externalDSLink and self.externalDSLink is None:
            self.externalDSLink = externalDSLink

    # reconnects save actions
    # \brief It reconnects the save action
    def reconnectSaveAction(self):
        self.connectView()
        if self.externalSave:
            try:
                self.dialog.ui.savePushButton.clicked.disconnect(
                    self.externalSave)
            except Exception:
                pass
            self.dialog.ui.savePushButton.clicked.connect(
                self.externalSave)
            # self.dialog.disconnect(
            #     self.dialog.ui.savePushButton, SIGNAL("clicked()"),
            #     self.externalSave)
            # self.parent.connect(
            #     self.dialog.ui.savePushButton, SIGNAL("clicked()"),
            #     self.externalSave)
        if self.externalStore:
            try:
                self.dialog.ui.storePushButton.clicked.disconnect(
                    self.externalStore)
            except Exception:
                pass
            self.dialog.ui.storePushButton.clicked.connect(
                self.externalStore)
            # self.dialog.disconnect(
            #     self.dialog.ui.storePushButton, SIGNAL("clicked()"),
            #     self.externalStore)
            # self.parent.connect(
            #     self.dialog.ui.storePushButton, SIGNAL("clicked()"),
            #     self.externalStore)
        if self.externalClose:
            try:
                self.dialog.ui.closePushButton.clicked.disconnect(
                    self.externalClose)
            except Exception:
                pass
            self.dialog.ui.closePushButton.clicked.connect(
                self.externalClose)
            # self.dialog.disconnect(
            #     self.dialog.ui.closePushButton, SIGNAL("clicked()"),
            #     self.externalClose)
            # self.parent.connect(
            #     self.dialog.ui.closePushButton, SIGNAL("clicked()"),
            #     self.externalClose)

    # switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status):
        if status == self._allAttributes:
            return
        self._allAttributes = status
        if hasattr(self, "view") and self.dialog:
            cNode = self._getCurrentNode()
            model = self.view.model()
            model.setAttributeView(self._allAttributes)
#             self.view.reset()
            newModel = ComponentModel(
                self.document, self._allAttributes, self.parent)
            self.view.setModel(newModel)
            self.connectView()
            self._hideFrame()
            if cNode:
                self._showNodes([cNode])

    # sets selected component item in the item frame
    # \brief It is executed  when component tree item is selected
    # \param index of component tree item
    def tagClicked(self, index):
        if not index.isValid() or not self.dialog:
            logger.warn("Not valid index")
            return
        self._currentTag = index
        item = self._currentTag.internalPointer()
        if item is None:
            logger.warn("Not valid index item")
            return

        node = item.node
        nNode = node.nodeName()

        if not self.dialog.ui:
            logger.warn("Dialog does not exist")
            return

        if self.dialog.ui.widget:
            self.dialog.ui.widget.setVisible(False)
        if unicode(nNode) in self._tagClasses.keys():
            if self.dialog.ui and self.dialog.ui.widget:
                if hasattr(self.dialog.ui.widget, "widget"):
                    self.dialog.ui.widget.widget.hide()
                else:
                    self.dialog.ui.widget.hide()

            self.dialog.ui.frame.hide()
            self._frameLayout.removeWidget(self.dialog.ui.widget)
            self.dialog.ui.widget = self._tagClasses[
                unicode(nNode)](self.dialog)
            self.dialog.ui.widget.root = self.document
            self.dialog.ui.widget.setFromNode(node)
            self.dialog.ui.widget.createGUI()
            if hasattr(self.dialog.ui.widget, "connectExternalActions"):
                self.dialog.ui.widget.connectExternalActions(
                    externalApply=self.externalApply,
                    externalDSLink=self.externalDSLink)
            if hasattr(self.dialog.ui.widget, "treeMode"):
                self.dialog.ui.widget.treeMode()
            self.dialog.ui.widget.view = self.view
            self.dialog.ui.view = self.view
            self._frameLayout.addWidget(self.dialog.ui.widget)
            self.dialog.ui.widget.show()
            self.dialog.ui.frame.show()
        else:
            if self.dialog.ui.widget:
                self.dialog.ui.widget.hide()
            self.dialog.ui.widget = None

    # opens context Menu
    # \param position in the component tree
    def _openMenu(self, position):
        if not self.dialog:
            return
        index = self.view.indexAt(position)
        if index.isValid():
            self.tagClicked(index)

        menu = QMenu()
        for action in self._actions:
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(action)
        menu.exec_(self.view.viewport().mapToGlobal(position))

    # sets up context menu
    # \param actions list of the context menu actions
    def addContextMenu(self, actions):
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._openMenu)
        self._actions = actions

    # resizes column size after tree item expansion
    # \param index index of the expanded item
    def _resizeColumns(self, index):
        for column in range(self.view.model().columnCount(index)):
            self.view.resizeColumnToContents(column)

    # sets name and directory of the current component
    # \param name component name
    # \param directory component directory
    def setName(self, name, directory=None):
        fi = None
        dr = ""
        if self._componentFile:
            fi = QFileInfo(self._componentFile)
        if directory is None and fi:
            dr = unicode(fi.dir().path())
        elif directory:
            dr = unicode(directory)
        elif self.directory:
            dr = self.directory
        else:
            dr = os.getcwd()

        self._componentFile = os.path.join(dr, name + ".xml")
        self.name = name
        self._xmlPath = self._componentFile

    # loads the component from the file
    # \param filePath xml file name with full path
    def load(self, filePath=None):

        if not filePath:
            if not self.name:
                self._componentFile = unicode(QFileDialog.getOpenFileName(
                    self.parent, "Open File", self._xmlPath,
                    "XML files (*.xml);;HTML files (*.html);;"
                    "SVG files (*.svg);;User Interface files (*.ui)")[0])
            else:
                self._componentFile = os.path.join(
                    self.directory, self.name + ".xml")
        else:
            self._componentFile = filePath
        if self._componentFile:
            try:
                fh = QFile(self._componentFile)
                if fh.open(QIODevice.ReadOnly):
                    self._loadFromString(fh)
                    self._xmlPath = self._componentFile
                    fi = QFileInfo(self._componentFile)
                    self.name = unicode(fi.fileName())

                    if self.name[-4:] == '.xml':
                        self.name = self.name[:-4]
                    self.savedXML = self.get()
                    return self._componentFile
                else:
                    QMessageBox.warning(
                        self.parent, "Cannot open the file",
                        "Cannot open the file: %s" % (self._componentFile))

            except (IOError, OSError, ValueError) as e:
                error = "Failed to load: %s" % e
                QMessageBox.warning(self.parent, "Loading problem",
                                    error)

                logger.warn(error)
            finally:
                self.fetchElements()
                if fh is not None:
                    fh.close()

    # sets component from XML string and reset component file name
    # \param xml XML string
    # \param new logical variableset to True if element is not saved
    def set(self, xml, new=False):
        self._componentFile = os.path.join(
            self.directory, self.name + ".xml")
        self._loadFromString(xml)
        self._xmlPath = self._componentFile
        self.savedXML = self.get()
        self.fetchElements()
        return self._componentFile

    # sets component from XML string
    # \param xml XML string
    def _loadFromString(self, xml):
        self.document = QDomDocument()

        if not self.document.setContent(xml):
            raise ValueError("could not parse XML")
        children = self.document.childNodes()

        j = 0
        for _ in range(children.count()):
            ch = children.item(j)
            if str(ch.nodeName()).strip() in \
                    ['xml', 'xml-stylesheet', "#comment"]:
                self.document.removeChild(ch)
            else:
                j += 1
        if self.dialog and self.dialog.ui:
            newModel = ComponentModel(
                self.document, self._allAttributes, self.parent)
            self.view.setModel(newModel)
            self.connectView()

    # loads the component item from the xml file
    # \param filePath xml file name with full path
    def loadComponentItem(self, filePath=None):

        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget \
                or not hasattr(self.dialog.ui.widget, "subItems") \
                or "component" not in self.dialog.ui.widget.subItems:
            return
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node

        if not filePath:
            itemFile = unicode(
                QFileDialog.getOpenFileName(
                    self.parent, "Open File", self._xmlPath,
                    "XML files (*.xml);;HTML files (*.html);;"
                    "SVG files (*.svg);;User Interface files (*.ui)")[0])
        else:
            itemFile = filePath

        if itemFile:
            try:
                fh = QFile(itemFile)
                if fh.open(QIODevice.ReadOnly):
                    root = QDomDocument()
                    if not root.setContent(fh):
                        raise ValueError("could not parse XML")
                    definition = root.firstChildElement(str("definition"))
                    if definition.nodeName() != "definition":
                        QMessageBox.warning(
                            self.parent, "Corrupted SubComponent",
                            "Component %s without <definition> tag" % itemFile)
                        return
                    child = definition.firstChild()
                    self.dialog.ui.widget.node = node

                    if index.column() != 0:
                        index = self.view.model().index(
                            index.row(), 0, index.parent())
                    while not child.isNull():
                        child2 = self.document.importNode(child, True)
                        self.dialog.ui.widget.appendElement(child2, index)

                        child = child.nextSibling()

                self.view.model().dataChanged.emit(
                    index, index)
                self.view.expand(index)

            except (IOError, OSError, ValueError) as e:
                error = "Failed to load: %s" % e
                QMessageBox.warning(self.parent, "Loading problem",
                                    error)
                logger.warn(error)
            finally:
                if fh is not None:
                    fh.close()

        self.fetchElements()
        return True

    # loads the datasource item from the xml file
    # \param filePath xml file name with full path
    def loadDataSourceItem(self, filePath=None):

        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget \
                or not hasattr(self.dialog.ui.widget, "subItems") \
                or "datasource" not in self.dialog.ui.widget.subItems:
            return
        child = self.dialog.ui.widget.node.firstChild()
        while not child.isNull():
            if child.nodeName() == 'datasource':
                QMessageBox.warning(
                    self.parent, "DataSource exists",
                    "To add a new datasource please remove the old one")
                return
            child = child.nextSibling()

        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel or not index.isValid():
            return
        node = sel.node

        if not filePath:
            dsFile = unicode(
                QFileDialog.getOpenFileName(
                    self.parent, "Open File", self._dsPath,
                    "XML files (*.xml);;HTML files (*.html);;"
                    "SVG files (*.svg);;User Interface files (*.ui)")[0])
        else:
            dsFile = filePath
        if dsFile:
            try:
                fh = QFile(dsFile)
                if fh.open(QIODevice.ReadOnly):
                    root = QDomDocument()
                    if not root.setContent(fh):
                        raise ValueError("could not parse XML")
                    ds = DomTools.getFirstElement(root, "datasource")

                    if ds:
                        if index.column() != 0:
                            index = self.view.model().index(
                                index.row(), 0, index.parent())
                        self.dialog.ui.widget.node = node
                        ds2 = self.document.importNode(ds, True)
                        self.dialog.ui.widget.appendElement(ds2, index)
                    else:
                        QMessageBox.warning(
                            self.parent, "Corrupted DataSource ",
                            "Missing <datasource> tag in %s" % dsFile)

                self.view.model().dataChanged.emit(
                    index, index)
                self.view.expand(index)
                self._dsPath = dsFile

            except (IOError, OSError, ValueError) as e:
                error = "Failed to load: %s" % e
                logger.warn(error)
            finally:
                if fh is not None:
                    fh.close()

        self.fetchElements()
        return True

    # add the datasource into the component tree
    # \param dsNode datasource DOM node
    def addDataSourceItem(self, dsNode):

        if dsNode.nodeName() != 'datasource':
            return

        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget \
                or not hasattr(self.dialog.ui.widget, "subItems") \
                or "datasource" not in self.dialog.ui.widget.subItems:
            return

        child = self.dialog.ui.widget.node.firstChild()
        while not child.isNull():
            if child.nodeName() == 'datasource':
                QMessageBox.warning(
                    self.parent, "DataSource exists",
                    "To add a new datasource please remove the old one")
                return
            child = child.nextSibling()

        index = self.view.currentIndex()
        if not index.isValid():
            return

        sel = index.internalPointer()
        if not sel:
            return

        node = sel.node

        self.dialog.ui.widget.node = node
        dsNode2 = self.document.importNode(dsNode, True)
        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.dialog.ui.widget.appendElement(dsNode2, index)

        self.view.model().dataChanged.emit(index, index)
        self.view.expand(index)
        self.fetchElements()
        return True

    # link the datasource into the component tree
    # \param dsName datasource name
    def linkDataSourceItem(self, dsName):

        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget \
                or not hasattr(self.dialog.ui.widget, "subItems") \
                or "datasource" not in self.dialog.ui.widget.subItems:
            return

        child = self.dialog.ui.widget.node.firstChild()
        while not child.isNull():
            if child.nodeName() == 'datasource':
                QMessageBox.warning(
                    self.parent, "DataSource exists",
                    "To link a new datasource please remove the old one")
                return
            child = child.nextSibling()

        index = self.view.currentIndex()
        if not index.isValid():
            return

        sel = index.internalPointer()
        if not sel:
            return

        if hasattr(self.dialog.ui.widget, "linkDataSource"):
            self.dialog.ui.widget.linkDataSource(dsName)

        if index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())

        self.view.model().dataChanged.emit(index, index)
        self.view.expand(index)
        self.fetchElements()
        return True

    # accepts merger dialog and interrupts merging
    # \brief It is connected to closing Merger dialog
    def _closeMergerDlg(self):
        if self._mergerdlg:
            self._mergerdlg.accept()

            self._interruptMerger()

    # interrupts merging
    # \brief It sets running flag of Merger to False
    def _interruptMerger(self):
        if self._merger:
            self._merger.running = False

    # merges the component tree
    # \returns True on success
    def merge(self, showMergerDlg=True):
        document = None
        dialog = False

        if showMergerDlg:
            self._mergerdlg = MergerDlg(self.parent)
            self._mergerdlg.createGUI()
            self._mergerdlg.finished.connect(
                self._interruptMerger)
            self._mergerdlg.interruptButton.clicked.connect(
                self._interruptMerger)
            # self.parent.connect(
            #     self._mergerdlg, SIGNAL("finished(int)"),
            #     self._interruptMerger)
            # self.parent.connect(
            #     self._mergerdlg.interruptButton, SIGNAL("clicked()"),
            #     self._interruptMerger)

        try:
            if self.view and self.dialog and self.dialog.ui \
                    and self.view.model():
                dialog = True
        except Exception:
            pass

        if not self.document:
            self._merged = False
            return
        try:
            self._merger = Merger(self.document)
            if showMergerDlg:
                self._merger.finished.connect(self._closeMergerDlg)
                # self.parent.connect(
                #     self._merger, SIGNAL("finished"), self._closeMergerDlg)

            cNode = self._getCurrentNode()
            if cNode:
                self._merger.selectedNode = cNode

            document = self.document
            self.document = QDomDocument()
            if dialog:
                newModel = ComponentModel(
                    self.document, self._allAttributes, self.parent)
                self.view.setModel(newModel)
                self.view.reset()
                self._hideFrame()
                self.connectView()

            self._merger.start()

            if showMergerDlg:
                self._mergerdlg.exec_()

            if self._merger:
                self._merger.wait()

            if showMergerDlg:
                self._closeMergerDlg()

            if self._merger and self._merger.exception is not None:
                raise self._merger.exception

            self._merged = True
            if dialog:
                newModel = ComponentModel(
                    document, self._allAttributes, self.parent)
            self.document = document
            if dialog:
                self.view.setModel(newModel)
                self._hideFrame()
                self.connectView()

                self.connectView()
                if hasattr(self._merger, "selectedNode") \
                        and self._merger.selectedNode:
                    self._showNodes([self._merger.selectedNode])

            self._merger = None

        except IncompatibleNodeError as e:
            logger.warn("Error in Merging: %s" % unicode(e.value))
            self._merger = None
            self._merged = False
            if dialog:
                newModel = ComponentModel(
                    document, self._allAttributes, self.parent)
            self.document = document
            if dialog:
                self.view.setModel(newModel)
                self._hideFrame()
                self.connectView()
                if hasattr(e, "nodes") and e.nodes:
                    self._showNodes(e.nodes)
            if dialog:
                QMessageBox.warning(
                    self.parent, "Merging problem",
                    "Error in %s Merging: %s" % (
                        unicode(self.name), unicode(e.value)))
        except Exception as e:
            logger.warn("Exception: %s" % unicode(e))
            self._merged = False
            if dialog:
                newModel = ComponentModel(
                    document, self._allAttributes, self.parent)
                self.document = document
                self.view.setModel(newModel)
                self._hideFrame()
                self.connectView()
            if dialog:
                QMessageBox.warning(self.parent, "Warning",
                                    "%s" % unicode(e))
        return self._merged

    # hides the component item frame
    # \brief It puts an empty widget into the widget frame
    def _hideFrame(self):
        if self.dialog and self.dialog.ui:
            if self.dialog.ui.widget:
                if hasattr(self.dialog.ui.widget, "widget"):
                    self.dialog.ui.widget.widget.setVisible(False)
                else:
                    self.dialog.ui.widget.setVisible(False)
            self.dialog.ui.widget = QWidget(self.dialog)
            self._frameLayout.addWidget(self.dialog.ui.widget)
            self.dialog.ui.widget.show()
            self.dialog.ui.frame.show()

    # creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        self.document = QDomDocument()
        self.document = self.document

        definition = self.document.createElement(str("definition"))
        self.document.appendChild(definition)
        if self.dialog and self.dialog.ui:
            newModel = ComponentModel(
                self.document, self._allAttributes, self.parent)
            self.view.setModel(newModel)
            self.connectView()
        self.fetchElements()
        self._hideFrame()

    # fetches tags with a given name  from the node branch
    # \param name of the
    # \returns dictionary with the required tags
    def _getTags(self, node, tagName):
        ds = {}
        if node:
            children = node.childNodes()
            for c1 in range(children.count()):
                child = children.item(c1)
                if child.nodeName() == tagName:
                    attr = child.attributes()
                    if attr.contains("name"):
                        name = unicode(attr.namedItem("name").nodeValue())
                    else:
                        self._tagCnt += 1
                        name = "__datasource__%s" % self._tagCnt
                    ds[name] = self._nodeToString(child)

            child = node.firstChild()
            if child:
                while not child.isNull():
                    childElem = child.toElement()
                    if childElem:
                        ds.update(self._getTags(childElem, tagName))
                    child = child.nextSibling()

        return ds

    # fetches the datasources from the component
    # \returns dictionary with datasources
    def getDataSources(self):
        ds = {}
        if hasattr(self.document, "toString"):
            self._tagCnt = 0
            ds.update(self._getTags(self.document, "datasource"))
        return ds

    # fetches the datasources from the component
    # \returns dictionary with datasources
    def getCurrentDataSource(self):
        ds = {}

        if not self.view or not self.dialog or not self.view.model() \
                or not self.dialog.ui or not self.dialog.ui.widget:
            return ds
        index = self.view.currentIndex()
        sel = index.internalPointer()
        if not sel:
            return ds
        if sel.node.nodeName() != "datasource":
            return ds

        node = sel.node

        attr = node.attributes()
        if attr.contains("name"):
            name = unicode(attr.namedItem("name").nodeValue())
        else:
            name = "__datasource__"
        ds[name] = self._nodeToString(node)
        return ds

    # provides the component in xml string
    # \param indent number of added spaces during pretty printing
    # \returns xml string
    def get(self, indent=0):
        if hasattr(self.document, "toString"):
            processing = self.document.createProcessingInstruction(
                "xml", "version='1.0'")
            self.document.insertBefore(processing, self.document.firstChild())
            string = unicode(self.document.toString(indent))
            self.document.removeChild(processing)
            return string

    # saves the component
    # \brief It saves the component in the xml file
    def save(self):
        if not self._merged:
            QMessageBox.warning(self.parent, "Saving problem",
                                "Document not merged")
            return
        error = None
        if self._componentFile is None:
            self.setName(self.name, self.directory)
        fpath = os.path.join(self.directory, self.name + ".xml")
        logger.info("saving %s" % fpath)
        try:
            fh = QFile(fpath)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(unicode(fh.errorString()))
            stream = QTextStream(fh)
            string = self.get(2)
            if string:
                stream << string
            else:
                raise ValueError("Empty component")

            self.savedXML = self.get()
        except (IOError, OSError, ValueError) as e:
            error = "Failed to save: %s Please try to use Save as "\
                "or change the component directory" % e
            QMessageBox.warning(self.parent, "Saving problem",
                                error)
            logger.warn(error)
        finally:
            if fh is not None:
                fh.close()
        if not error:
            return True

    # asks if component should be removed from the component list
    # \brief It is called on removing  the component from the list
    def _close(self):
        if QMessageBox.question(
                self.parent, "Close component",
                "Would you like to close the component ?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
            return
        self.dialog.reject()

    # provides the component name with its path
    # \returns component name with its path
    def getNewName(self):
        if self._componentFile is None:
            self.setName(self.name, self.directory)

        self._componentFile = unicode(
            QFileDialog.getSaveFileName(
                self.parent, "Save Component As ...", self._componentFile,
                "XML files (*.xml);;HTML files (*.html);;"
                "SVG files (*.svg);;User Interface files (*.ui)")[0])
        return self._componentFile


# test function
def test():
    import sys

    # Qt application
    app = QApplication(sys.argv)
    component = Component()
    component.createGUI()
    component.dialog.resize(680, 560)
    component.createHeader()
    component.dialog.show()
    component.dialog.setWindowTitle("%s [Component]" % component.name)

    app.exec_()


if __name__ == "__main__":
    test()
