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
## \file NodeDlg.py
# Abstract Node dialog class

from PyQt4.QtGui import QDialog
from PyQt4.QtXml import QDomNode
from PyQt4.QtCore import (QString,SIGNAL)

## dialog defining a field tag
class NodeDlg(QDialog):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(NodeDlg, self).__init__(parent)

        ## DOM node    
        self.node = None
        ## DOM root
        self.root = None
        ## component tree view
        self.view = None 
        ## component tree model
        self.model = None 

        self.subItems = []

    def reset(self):
        index = self.view.currentIndex()
        self.setFromNode()
        self.updateForm()
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)


    def getFirstElement(self, node, name):
        if node:

            child = node.firstChild()
            if child:
                while not child.isNull():
                    if child and  child.nodeName() == name:
                        return child
                    child = child.nextSibling()
            
            child = node.firstChild()
            if child:
                while not child.isNull():
                    elem = self.getFirstElement(child, name)
                    if elem:
                        return elem
                    child = child.nextSibling()
                
                

    def getElementRow(self, element):
        row = 0
        if self.node:
            children = self.node.childNodes()
            for i in range(children.count()):
                ch = children.item(i)
                if ch.isElement() and  element == ch.toElement():
                    break
                row += 1
            if row < children.count():
                return row

    def getNodeRow(self, child):
        row = 0
        if self.node:
            children = self.node.childNodes()
            for i in range(children.count()):
                ch = children.item(i)
                if child == ch:
                    break
                row += 1
            if row < children.count():
                return row


    def getText(self, node):
        text = QString()
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
        return text    

    def replaceText(self, node, index, text = None):
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    self.removeNode(child, index)
                child = child.nextSibling()
            if text:
                textNode = self.root.createTextNode(QString(text))
                self.appendNode(textNode,index)
    

    def removeNode(self, node, parent):
        if self.model is not None: 
            row = self.getNodeRow(node)
            if row is not None:
                self.model.removeRows(row, 1, parent)
        self.node.removeChild(node)


    def replaceNode(self, oldNode, newNode, parent):
        if self.model is not None: 
            row = self.getNodeRow(oldNode)
        self.node.replaceChild(newNode, oldNode)
        if self.model is not None: 
            if row is not None:
                self.model.removeRows(row, 1, parent)
                self.model.insertRows(row, 1, parent)


    def appendNode(self, node, parent):
        self.node.appendChild(node)
        if self.model is not None: 
            row = self.node.childNodes().count()-1
            if row is not None:
                self.model.insertRows(row, 1, parent)


    def removeElement(self, element, parent):
        if self.model is not None: 
            row = self.getElementRow(element)
            if row is not None:
                self.model.removeRows(row, 1, parent)
        self.node.removeChild(element)

    def replaceElement(self, oldElement, newElement, parent):
        if self.model is not None: 
            row = self.getElementRow(oldElement)
        self.node.replaceChild(newElement, oldElement)
        if self.model is not None: 
            if row is not None:
                self.model.removeRows(row, 1, parent)
                self.model.insertRows(row, 1, parent)

    def appendElement(self, newElement, parent):
        self.node.appendChild(newElement)
        if self.model is not None: 
            row = self.node.childNodes().count()-1
            if row is not None:
                self.model.insertRows(row, 1, parent)

            



    ## updates the form
    # \brief abstract class
    def updateForm(self):
        pass
        

    ## creates GUI
    # \brief abstract class
    def createGUI(self):
        pass

        
    ## sets the form from the DOM node
    # \param node Dom node
    def setFromNode(self, node=None):
        pass



if __name__ == "__main__":
    import sys
    
