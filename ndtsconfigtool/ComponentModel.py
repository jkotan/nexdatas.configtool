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
## \file ComponentDlg.py
# component classes 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
                         QXmlInputSource, QXmlSimpleReader)

import os
from ComponentItem import *

class ComponentModel(QAbstractItemModel):
    def __init__(self, document, parent=None):
        super(ComponentModel, self).__init__(parent)
        
        self.domDocument = document
        self.rootItem = ComponentItem(self.domDocument, 0)

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid() :
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        
        item  = index.internalPointer()
        node = item.node

        if index.column() == 0:
            return node.nodeName()
        elif index.column() == 1:
            attributeMap = node.attributes()
            attributes = QStringList()
            for i in range(attributeMap.count()):
                attribute = attributeMap.item(i)
                attributes.append(attribute.nodeName() + "=\"" +attribute.nodeValue() + "\"")
            return attributes.join(" ")   
        elif index.column() == 2:
            return node.nodeValue().split("\n").join(" ")
        else:
            return QVariant()
        
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractItemModel.flags(self,index) |
                            Qt.ItemIsEnabled | Qt.ItemIsSelectable )
        
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole :
            if section == 0 :
                return QVariant("Name")
            elif section == 1:
                return QVariant("Attribute")
            elif section == 2:
                return QVariant("Value")
            else:
                return QVariant()
        
    
    def index(self, row, column, parent = QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row,column, childItem)
        else:
            return QModelIndex()
        


    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.parent

        if parentItem is None or parentItem == self.rootItem:
            return QModelIndex()
            
        return self.createIndex(parentItem.row,0, parentItem)

        

    def rowCount(self, parent = QModelIndex()):
        if parent.column() > 0 :
            return 0
        
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            

        return parentItem.node.childNodes().count()


    def columnCount(self, parent = QModelIndex()):
        return 3
    


if __name__ == "__main__":
    import sys

    
    

#  LocalWords:  os
