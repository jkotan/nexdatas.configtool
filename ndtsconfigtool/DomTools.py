#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file DOMTools.py
# Abstract Node dialog class

from PyQt4.QtGui import QDialog
from PyQt4.QtXml import QDomNode
from PyQt4.QtCore import (QString, SIGNAL, QModelIndex)

## abstract node dialog 
class DomTools(object):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        pass

    ## provides the first element in the tree with the given name
    # \param node DOM node
    # \param name child name
    # \returns DOM child node
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
                
                

    ## provides row number of the given element
    # \param element DOM element
    # \param node DOM node
    # \returns row number
    def __getElementRow(self, element, node):
        row = 0
        if node:
            children = node.childNodes()
            for i in range(children.count()):
                ch = children.item(i)
                if ch.isElement() and  element == ch.toElement():
                    break
                row += 1
            if row < children.count():
                return row


    ## provides row number of the given node
    # \param child child item
    # \param node parent node        
    # \returns row number
    def getNodeRow(self, child, node):
        row = 0
        if node:
            children = node.childNodes()
            for i in range(children.count()):
                ch = children.item(i)
                if child == ch:
                    break
                row += 1
            if row < children.count():
                return row


    ## provides node text for the given node
    # \param node DOM node        
    # \returns string with node texts
    def getText(self, node):
        text = QString()
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
        return text    



    ## replaces node text for the given node
    # \param node parent DOM node        
    # \param index of child text node
    # \param text string with text
    def replaceText(self, node, index, model, text = None):
        if node:
            root = model.rootIndex.internalPointer().node
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    self.removeNode(child, index, model)
                child = child.nextSibling()
            if text:
                textNode = root.createTextNode(QString(text))
                self.appendNode(textNode,index, model)
    

    ## removes node
    # \param node DOM node to remove
    # \param parent parent node index  
    # \param model Component model            
    def removeNode(self, node, parent, model):
        row = self.getNodeRow(node, parent.internalPointer().node)
        if row is not None:
            model.removeItem(row, parent)

                
    ## replaces node
    # \param oldNode old DOM node 
    # \param newNode new DOM node 
    # \param parent parent node index
    # \param model Component model            
    def replaceNode(self, oldNode, newNode, parent, model):
        node = parent.internalPointer().node
        row = self.getNodeRow(oldNode, node)
        if row is not None:
            model.removeItem(row, parent)
            if row  < node.childNodes().count():
                model.insertItem(row, newNode, parent)
            else:
                model.appendItem(newNode, parent)

    ## appends node
    # \param node DOM node to append
    # \param parent parent node index
    # \param model Component model            
    def appendNode(self, node, parent, model):
        if model.appendItem(node, parent):
            return True
   

    ## removes node element
    # \param element DOM node element to remove
    # \param parent parent node index      
    # \param model Component model            
    def removeElement(self, element, parent, model):
        row = self.__getElementRow(element, parent.internalPointer().node)
        if row is not None:
            model.removeItem(row, parent)


    ## replaces node element
    # \param oldElement old DOM node element 
    # \param newElement new DOM node element 
    # \param parent parent node index
    # \param model Component model            
    def replaceElement(self, oldElement, newElement, parent, model):
        row = self.__getElementRow(oldElement, parent.internalPointer().node)
        if row is not None:
            model.removeItem(row, parent)
            if row  < self.node.childNodes().count():
                model.insertItem(row, newElement, parent)
            else:
                model.appendItem(newElement, parent)



if __name__ == "__main__":
    import sys
    
