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
# \file NodeDlg.py
# Abstract Node dialog class

""" abstract Node widget """

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import (QModelIndex)

from .DomTools import DomTools


# abstract node dialog
class NodeDlg(QDialog):

    # constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(NodeDlg, self).__init__(parent)

        # DOM node
        self.node = None
        # DOM root
        self.root = None
        # component tree view
        self.view = None

        # allowed subitems
        self.subItems = []

        #  user interface
        self.ui = None

        # external apply action
        self.externalApply = None

        # external apply action
        self.externalDSLink = None

        # datasource label for templated XML
        self.dsLabel = "datasources"

    # connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    # \param externalDSLink dsource link action
    def connectExternalActions(self, externalApply=None, externalSave=None,
                               externalClose=None, externalStore=None,
                               externalDSLink=None):
        if externalApply and self.externalApply is None and self.ui and \
                hasattr(self.ui, "applyPushButton") and \
                self.ui.applyPushButton:
            self.ui.applyPushButton.clicked.connect(externalApply)
            self.externalApply = externalApply
        if externalDSLink and self.externalDSLink is None and self.ui and \
                hasattr(self.ui, "linkDSPushButton") \
                and self.ui.linkDSPushButton:
            self.ui.linkDSPushButton.clicked.connect(externalDSLink)
            self.externalDSLink = externalDSLink

    # resets the dialog
    # \brief It sets forms and dialog from DOM
    def reset(self):
        if self.view and hasattr(self.view, "currentIndex"):
            index = self.view.currentIndex()
        self.setFromNode()
        self.updateForm()
        if self.view:
            if index.column() != 0:
                index = self.view.model().index(index.row(), 0, index.parent())
            self.view.model().dataChanged.emit(index, index)

    # replaces node text for the given node
    # \param index of child text node
    # \param text string with text
    def replaceText(self, index, text=None):
        if self.view is not None and self.view.model() is not None:
            return DomTools.replaceText(
                self.node, index, self.view.model(), text)

    # removes node element
    # \param element DOM node element to remove
    # \param parent parent node index
    def removeElement(self, element, parent):
        if self.view is not None and self.view.model() is not None:
            return DomTools.removeElement(
                element, parent, self.view.model())

    # replaces node element
    # \param oldElement old DOM node element
    # \param newElement new DOM node element
    # \param parent parent node index
    def replaceElement(self, oldElement, newElement, parent):
        if self.view is not None and self.view.model() is not None:
            return DomTools.replaceElement(
                oldElement, newElement, parent, self.view.model())

    # appends node element
    # \param newElement new DOM node element
    # \param parent parent node index
    def appendElement(self, newElement, parent):
        if self.view is not None and self.view.model() is not None:
            return DomTools.appendNode(
                newElement, parent, self.view.model())
        return False

    # updates the form
    # \brief abstract class
    def updateForm(self):
        pass

    # updates the node
    # \brief abstract class
    def updateNode(self, index=QModelIndex()):
        pass

    # creates GUI
    # \brief abstract class
    def createGUI(self):
        pass

    # sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        pass


if __name__ == "__main__":
    pass
