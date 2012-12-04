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
from PyQt4.QtCore import (QString, SIGNAL, QModelIndex)

## abstract node dialog 
class NodeDlg(QDialog):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(NodeDlg, self).__init__(parent)

#        print "parent :", parent
        ## DOM node    
        self.node = None
        ## DOM root
        self.root = None
        ## component tree view
        self.view = None 

        ## allowed subitems
        self.subItems = []

        ## widget with apply button
        self.applyPushButton = None

        ## external apply action
        self._externalApply = None


    ## connects the given apply action
    # \param externalApply apply action   
    def connectExternalActions(self,  externalApply=None):
        if externalApply and self._externalApply is None and self.applyPushButton:
            self.connect(self.applyPushButton, SIGNAL("clicked()"), 
                         externalApply)
            self._externalApply = externalApply
        
    ## resets the dialog
    # \brief It sets forms and dialog from DOM    
    def reset(self):
        index = self.view.currentIndex()
        self.setFromNode()
        self.updateForm()
        if  index.column() != 0:
            index = self.view.model().index(index.row(), 0, index.parent())
        self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)


    ## provides the first element in the tree with the given name
    # \param node DOM node
    # \param name child name
    # \returns DOM child node
    def _getFirstElement(self, node, name):
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
                    elem = self._getFirstElement(child, name)
                    if elem:
                        return elem
                    child = child.nextSibling()
                
                

    ## provides row number of the given element
    # \param element DOM element
    # \returns row number
    def _getElementRow(self, element):
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

    ## provides row number of the given node
    # \param child child item
    # \param node parent node        
    # \returns row number
    def getNodeRow(self, child, node = None):
        row = 0
        lnode =  node if node is not None else self.node
        if lnode:
            children = lnode.childNodes()
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
    def _getText(self, node):
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
    def _replaceText(self, node, index, text = None):
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    self.removeNode(child, index)
                child = child.nextSibling()
            if text:
                textNode = self.root.createTextNode(QString(text))
                self.appendNode(textNode,index)
    

    ## removes node
    # \param node DOM node to remove
    # \param parent parent node index        
    def removeNode(self, node, parent):
        if self.view is not None and self.view.model() is not None: 
            row = self.getNodeRow(node)
            if row is not None:
                self.view.model().removeItem(row, node, parent)


    ## replaces node
    # \param oldNode old DOM node 
    # \param newNode new DOM node 
    # \param parent parent node index
    def _replaceNode(self, oldNode, newNode, parent):
        if self.view is not None and self.view.model() is not None: 
            row = self.getNodeRow(oldNode)
        if self.view is not None and self.view.model() is not None: 
            if row is not None:
                self.view.model().removeItem(row, oldNode, parent)
                if row  < self.node.childNodes().count():
                    self.view.model().insertItem(row, newNode, parent)
                else:
                    self.view.model().appendItem(newNode, parent)

    ## appends node
    # \param node DOM node to remove
    # \param parent parent node index
    def appendNode(self, node, parent):
        if self.view is not None and self.view.model() is not None: 
            if self.view.model().appendItem(node, parent):
                return True
        return False     
   

    ## removes node element
    # \param element DOM node element to remove
    # \param parent parent node index      
    def _removeElement(self, element, parent):
        if self.view is not None and self.view.model() is not None: 
            row = self._getElementRow(element)
            if row is not None:
                self.view.model().removeItem(row, element, parent)


    ## replaces node element
    # \param oldElement old DOM node element 
    # \param newElement new DOM node element 
    # \param parent parent node index
    def _replaceElement(self, oldElement, newElement, parent):
        if self.view is not None and self.view.model() is not None: 
            row = self._getElementRow(oldElement)
        if self.view is not None and self.view.model() is not None: 
            if row is not None:
                self.view.model().removeItem(row, oldElement, parent)
                if row  < self.node.childNodes().count():
                    self.view.model().insertItem(row, newElement, parent)
                else:
                    self.view.model().appendItem(newElement, parent)


    ## appends node element
    # \param newElement new DOM node element 
    # \param parent parent node index      
    def _appendElement(self, newElement, parent):
        if self.view is not None and self.view.model() is not None: 
            self.view.model().appendItem(newElement, parent)

            
    ## updates the form
    # \brief abstract class
    def updateForm(self):
        pass


    ## updates the node
    # \brief abstract class
    def updateNode(self, index=QModelIndex()):
        pass
        

    ## creates GUI
    # \brief abstract class
    def createGUI(self):
        pass

        
    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        pass



if __name__ == "__main__":
    import sys
    
