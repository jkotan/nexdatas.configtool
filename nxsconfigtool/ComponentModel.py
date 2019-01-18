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
# \file ComponentModel.py
# component classes

""" component model for tree view """

from PyQt5.QtCore import (QAbstractItemModel, Qt, QModelIndex)
from PyQt5.QtXml import QDomNode

from . ComponentItem import ComponentItem


# model for component tree
class ComponentModel(QAbstractItemModel):
    # constuctor
    # \param document DOM document
    # \param parent widget
    # \param allAttributes True if show all attributes in the tree
    def __init__(self, document, allAttributes, parent=None):
        super(ComponentModel, self).__init__(parent)

        # show all attribures or only the type attribute
        self.__allAttributes = allAttributes

        # root item of the tree
        self.__rootItem = ComponentItem(document)
        # index of the root item
        self.rootIndex = self.createIndex(0, 0, self.__rootItem)

    # provides access to the header data
    # \param section integer index of the table column
    # \param orientation orientation of the header
    # \param role access type of the header data
    # \returns header data defined for the given index and formated according
    #          to the role
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                if self.__allAttributes:
                    return "Attributes"
                else:
                    return "Type"
            elif section == 2:
                return "Value"
            else:
                return None

    # switches between all attributes in the try or only type attribute
    # \param allAttributes all attributes are shown if True
    def setAttributeView(self, allAttributes):
        self.__allAttributes = allAttributes

    # provides read access to the model data
    # \param index of the model item
    # \param role access type of the data
    # \returns data defined for the given index and formated according
    #          to the role
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        node = item.node

        attributeMap = node.attributes()
#        if node.nodeName() == 'xml':
#            return

        if index.column() == 0:
            name = None
            if attributeMap.contains("name"):
                name = attributeMap.namedItem("name").nodeValue()

            if name is not None:
                return str(node.nodeName() + ": " + name)
            else:
                return str(node.nodeName())
        elif index.column() == 1:
            if self.__allAttributes:
                attributes = []
                for i in range(attributeMap.count()):
                    attribute = attributeMap.item(i)
                    attributes.append(attribute.nodeName() + "=\""
                                      + attribute.nodeValue() + "\"")
                return str(" ".join(attributes) + "  ")
            else:
                return str(
                    (attributeMap.namedItem("type").nodeValue() + "  ")
                    if attributeMap.contains("type") else str("  "))

        elif index.column() == 2:
            return str(" ".join(node.nodeValue().split("\n")))
        else:
            return ""

    # provides flag of the model item
    # \param index of the model item
    # \returns flag defined for the given index and formated according
    #          to the role
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractItemModel.flags(self, index) |
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    # provides access to the item index
    # \param row integer index counting DOM child item
    # \param column integer index counting table column
    # \param parent index of the parent item
    # \returns index for the required model item
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.__rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    # provides access to the parent index
    # \param child  child index
    # \returns parent index for the given child
    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()

        if not hasattr(childItem, "parent"):
            return QModelIndex()

        parentItem = childItem.parent

        if parentItem is None or parentItem == self.__rootItem:
            return QModelIndex()

        if parentItem is None:
            return QModelIndex()

#        if parentItem == self.__rootItem:
#            self.rootIndex

        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    # provides number of the model rows
    # \param parent parent index
    # \returns number of the children for the given parent
    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.__rootItem
        else:
            parentItem = parent.internalPointer()

        if not hasattr(parentItem, "node") or parentItem.node is None:
            return 0
        return parentItem.node.childNodes().count()

    # provides number of the model columns
    # \param parent parent index
    # \returns 3 which corresponds to component tag tree, tag attributes,
    #          tag values
    def columnCount(self, parent=QModelIndex()):
        return 3

    # inserts the given rows into the model
    # \param position row integer index where rows should be inserted
    # \param node DOM node to append
    # \param parent index of the parent item
    # \returns True if parent exists
    def insertItem(self, position, node, parent=QModelIndex()):
        item = parent.internalPointer()
        if not item:
            return False

        self.beginInsertRows(parent, position, position)

        pIndex = self.index(position, 0, parent)
        previous = pIndex.internalPointer().node if pIndex.isValid() \
            else QDomNode()
        item.node.insertBefore(node, previous)
#
        status = item.insertChildren(position, 1)

        self.endInsertRows()

        return status

    # append the given DOM node into parent item
    # \param node DOM node to append
    # \param parent index of the parent item
    # \returns True if parent exists
    def appendItem(self, node, parent=QModelIndex()):
        item = parent.internalPointer()
        if not item:
            return False
        position = item.node.childNodes().count()
        self.beginInsertRows(parent, position, position)

        pIndex = self.index(position, 0, parent)
        previous = pIndex.internalPointer().node \
            if pIndex.isValid() else QDomNode()
        item.node.insertAfter(node, previous)
#
        status = item.insertChildren(position, 1)

        self.endInsertRows()

        return status

    # removes the given rows from the model
    # \param position row integer index of the first removed row
    # \param parent index of the parent item
    # \returns True if parent exists
    def removeItem(self, position, parent=QModelIndex()):
        item = parent.internalPointer()
        if not item:
            return False
        self.beginRemoveRows(parent, position, position)
        node = item.child(position).node

        status = item.removeChildren(position, 1)
        item.node.removeChild(node)
        self.endRemoveRows()
        return status


if __name__ == "__main__":
    pass
