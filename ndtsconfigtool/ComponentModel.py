#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \package ndtsconfigtool nexdatas
## \file ComponentModel.py
# component classes 

from PyQt4.QtCore import (QAbstractItemModel, QVariant, Qt, QModelIndex, QStringList, QString)
#from PyQt4.QtGui import 
from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
                         QXmlInputSource, QXmlSimpleReader)

import os
from ComponentItem import ComponentItem

## model for component tree
class ComponentModel(QAbstractItemModel):
    ## constuctor
    # \param document DOM document
    # \param parent widget
    # \param allAttributes True if show all attributes in the tree
    def __init__(self, document, allAttributes, parent=None):
        super(ComponentModel, self).__init__(parent)
        
        ## DOM document
        self._domDocument = document

        ## show all attribures or only the type attribute
        self._allAttributes = allAttributes
        
        ## root item of the tree
        self.rootItem = ComponentItem(self._domDocument
#                                      , 0 
                                      )

    # switches between all attributes in the try or only type attribute
    # \param allAttributes all attributes are shown if True
    def setAttributeView(self, allAttributes):
        self._allAttributes = allAttributes
        

    ## provides read access to the model data
    # \param index of the model item         
    # \param role access type of the data
    # \returns data defined for the given index and formated according to the role    
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid() :
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        
        item  = index.internalPointer()
        node = item.node

        attributeMap = node.attributes()
#        if node.nodeName() == 'xml':
#            return 

        if index.column() == 0:      
            name = None
            if attributeMap.contains("name"):
                name = attributeMap.namedItem("name").nodeValue()

            if name is not None:    
                return node.nodeName() +": "+ name
            else:
                return node.nodeName() 
        elif index.column() == 1:
            if self._allAttributes:
                attributes = QStringList()
                for i in range(attributeMap.count()):
                    attribute = attributeMap.item(i)
                    attributes.append(attribute.nodeName() + "=\"" +attribute.nodeValue() + "\"")
                return attributes.join(" ")   
            else:
                return attributeMap.namedItem("type").nodeValue() \
                    if attributeMap.contains("type") else QString("")
                 
        elif index.column() == 2:
            return node.nodeValue().split("\n").join(" ")
        else:
            return QVariant()
        
        
    ## provides flag of the model item    
    # \param index of the model item         
    # \returns flag defined for the given index and formated according to the role    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractItemModel.flags(self,index) |
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable )
        

    
    ## provides access to the header data
    # \param section integer index of the table column 
    # \param orientation orientation of the header
    # \param role access type of the header data
    # \returns header data defined for the given index and formated according to the role    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole :
            if section == 0 :
                return QVariant("Name")
            elif section == 1:
                if self._allAttributes:
                    return QVariant("Attribute")
                else:
                    return QVariant("Type")
            elif section == 2:
                return QVariant("Value")
            else:
                return QVariant()
        
    

    ## provides access to the item index
    # \param row integer index counting DOM child item
    # \param column integer index counting table column
    # \param parent index of the parent item       
    # \returns index for the required model item 
    def index(self, row, column, parent = QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
        


    ## provides access to the parent index
    # \param child  child index
    # \returns parent index for the given child
    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()

        ## TODO when it is performed
        if not hasattr(childItem,"parent"):
            return QModelIndex()            
        
        parentItem = childItem.parent

        if parentItem is None or parentItem == self.rootItem:
            return QModelIndex()
            
        return self.createIndex(parentItem.childNumber(), 0, parentItem)

        

    ## provides number of the model rows
    # \param parent parent index
    # \returns number of the children for the given parent
    def rowCount(self, parent = QModelIndex()):
        if parent.column() > 0 :
            return 0
        
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            

        return parentItem.node.childNodes().count()


    ## provides number of the model columns
    # \param parent parent index
    # \returns 3 which corresponds to component tag tree, tag attributes, tag values
    def columnCount(self, parent = QModelIndex()):
        return 3
    
    ## inserts the given rows into the model
    # \param position row integer index where rows should be inserted
    # \param rows numbers of rows to be inserted
    # \param parent index of the parent item       
    # \returns True if parent exists
    def insertRows(self, position, rows = 1, parent = QModelIndex()):
        item = parent.internalPointer()
        if not item:
            return False
        self.beginInsertRows(parent, position, position+rows-1)
        status = item.insertChildren(position, rows)
        self.endInsertRows()
        return status


    ## removes the given rows from the model
    # \param position row integer index of the first removed row
    # \param rows numbers of rows to be removed
    # \param parent index of the parent item       
    # \returns True if parent exists
    def removeRows(self, position, rows = 1, parent = QModelIndex()):
        item = parent.internalPointer()
        if not item:
            return False
        self.beginRemoveRows(parent, position, position+rows-1)
        status = item.removeChildren(position, rows)
        self.endRemoveRows()
        return status



if __name__ == "__main__":
    import sys

    
    

#  LocalWords:  os
