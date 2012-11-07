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
import gc
        
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
        print "CM"
#        gc.collect()
        
        ## DOM document
        self._domDocument = document

        ## show all attribures or only the type attribute
        self._allAttributes = allAttributes
        
        ## root item of the tree
        self.rootItem = ComponentItem(self._domDocument)
        ## index of the root item
        self.rootIndex = self.createIndex(0, 0, self.rootItem)

    ## switches between all attributes in the try or only type attribute
    # \param allAttributes all attributes are shown if True
    def setAttributeView(self, allAttributes):
        print "SA"
        gc.collect()
        self._allAttributes = allAttributes
        

    ## provides read access to the model data
    # \param index of the model item         
    # \param role access type of the data
    # \returns data defined for the given index and formated according to the role    
    def data(self, index, role = Qt.DisplayRole):
        print "DA"
#        gc.collect()
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
                return attributes.join(" ") + "  "    
            else:
                return (attributeMap.namedItem("type").nodeValue() + "  ") \
                    if attributeMap.contains("type") else QString("  ")
                 
        elif index.column() == 2:
            return node.nodeValue().split("\n").join(" ")
        else:
            return QVariant()
        
        


    ## provides flag of the model item    
    # \param index of the model item         
    # \returns flag defined for the given index and formated according to the role    
    def flags(self, index):
        print "FL"
        gc.collect()
        if not index.isValid():
            print "FL2I"
            return Qt.ItemIsEnabled
#        return Qt.ItemFlags(QAbstractItemModel.flags(self,index) |
#                            Qt.ItemIsEnabled | Qt.ItemIsSelectable )
#        gc.collect()
        print "FL1"
        
#        fl1 = Qt.ItemFlags()
#        print "FL1a"
#        fl = Qt.ItemIsUserCheckable
#        print "FL1a2", int(fl)
#        fl1 |= 33
#        print "FL1b"
#        fl1 |= Qt.ItemIsEnabled
#        print "FL1c"
#        fl1 |= Qt.ItemIsSelectable
#        print "FL1d"
        
#        fl1 =  QAbstractItemModel.flags(self,index) | Qt.ItemIsEnabled | Qt.ItemIsSelectable 
#        print "FL1b",fl1.__str__()
        
#        f = Qt.ItemFlags(fl1)
        f = Qt.ItemFlags(33)
        print "FL2"
        return f

    
    ## provides access to the header data
    # \param section integer index of the table column 
    # \param orientation orientation of the header
    # \param role access type of the header data
    # \returns header data defined for the given index and formated according to the role    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        print "HD"
#        gc.collect()
        if orientation == Qt.Horizontal and role == Qt.DisplayRole :
            if section == 0 :
                return QVariant("Name")
            elif section == 1:
                if self._allAttributes:
                    return QVariant("Attributes")
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
        print "ID"
#        gc.collect()
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
        print "PA"
 #       gc.collect()
        print "PA1"
        if not child.isValid():
            return QModelIndex()

        print "PA2"
        childItem = child.internalPointer()

        print "PA3"
        ## TODO when it is performed
        if not hasattr(childItem, "parent"):
            return QModelIndex()            
        
        print "PA4"
        parentItem = childItem.parent

        print "PA5"
        if parentItem is None or parentItem == self.rootItem:
            print "PA6a"
            return QModelIndex()

#        if parentItem is None:
#            return QModelIndex()

#        if parentItem == self.rootItem:
#            self.rootIndex

        print "PA6b"

        
#        return self.createIndex(parentItem.childNumber(), 0, parentItem)
        res= self.createIndex(parentItem.childNumber(), 0, parentItem)
        print "PA7"
        return res

    ## provides number of the model rows
    # \param parent parent index
    # \returns number of the children for the given parent
    def rowCount(self, parent = QModelIndex()):
        print "RC"
#        gc.collect()
        if parent.column() > 0 :
            return 0
        
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
 
#        gc.collect()
            
        return parentItem.node.childNodes().count()


    ## provides number of the model columns
    # \param parent parent index
    # \returns 3 which corresponds to component tag tree, tag attributes, tag values
    def columnCount(self, parent = QModelIndex()):
        print "CC"
 #       gc.collect()
        return 3
    

    ## inserts the given rows into the model
    # \param position row integer index where rows should be inserted
    # \param rows numbers of rows to be inserted
    # \param parent index of the parent item       
    # \returns True if parent exists
    def insertRows(self, position, rows = 1, parent = QModelIndex()):
        print "IR"
 #       gc.collect()
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
        print "RR"
 #       gc.collect()
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
