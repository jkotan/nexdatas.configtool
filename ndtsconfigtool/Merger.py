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
## \file Merger.py
# Class for merging DOM component trees

from PyQt4.QtXml import QDomNode
#from PyQt4.QtXml import (QDomDocument, QDomNode, QXmlDefaultHandler,
#                         QXmlInputSource, QXmlSimpleReader)

from PyQt4.QtCore import QString

class IncompatibleNodeError(Exception): pass




## merges the components
class Merger(object):
    
    ## constructor
    # \param root  DOM root node
    def __init__(self, root):
        
        ## DOM root node
        self.root = root
        ## tags which cannot have the same siblings
        self.singles =['datasource', 'strategy', 'dimensions', 'definition',
                       'record', 'device', 'query', 'database', 'door']

        self.children ={
            "datasource":("record", "doc", "device", "database", "query", "door"),
            "attribute":("enumeration", "doc"),
            "definition":("group", "field", "attribute", "link", "component", "doc", "symbols"),
            "dimensions":("dim", "doc"),
            "field":("attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"),
            "group":("group", "field", "attribute", "link", "component", "doc"),
            "link":("doc")
            }

    def getText(self, node):
        text = QString()
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
        return text    

    def getAncestors(self, node):
        res = "" 
        attr = node.attributes()

        name = attr.namedItem("name").nodeValue() \
            if attr.contains("name") else ""

        if node.parentNode().nodeName() != '#document':
            print node.nodeName()
            res =  self.getAncestors(node.parentNode()) 
        res += "/" + unicode(node.nodeName()) 
        if name:
            res += ":" + name
        return res 


    def areMergeable(self,elem1, elem2):
#        print "checking:" ,elem1.nodeName(), elem2.nodeName()
        if elem1.nodeName() != elem2.nodeName():
            return False
        tagName = unicode(elem1.nodeName())
        attr1 = elem1.attributes()
        attr2 = elem2.attributes()
        status = True
        tags =[]

        name1 = attr1.namedItem("name").nodeValue() \
            if attr1.contains("name") else ""
        name2 = attr2.namedItem("name").nodeValue() \
            if attr1.contains("name") else ""
#        print "with names" ,name1,name2        

        if name1 != name2 :
            return False

        for i1 in range(attr1.count()):
            for i2 in range(attr2.count()):
                at1 = attr1.item(i1)
                at2 = attr2.item(i2)
                if at1.nodeName() == at2.nodeName() and at1.nodeValue() != at2.nodeValue():
                    status = False
                    tags.append((str(self.getAncestors(at1)),
                                 str(at1.nodeValue()) , str(at2.nodeValue())))

        if not status  and tagName in self.singles: 
            raise IncompatibleNodeError,\
                "Incompatible element attributes  %s: " % str(tags)


        if tagName == 'field':
            text1=unicode(self.getText(elem1)).strip()
            text2=unicode(self.getText(elem2)).strip()         
            ## TODO white spaces?
            if text1 != text2:
                raise IncompatibleNodeError,\
                    "Incompatible \n%s element value\n%s \n%s "  \
                    % (str(self.getAncestors(elem1)), text1, text2)
            
        return status

    def mergeNodes(self,elem1, elem2):
        tagName = elem1.nodeName()
        attr1 = elem1.attributes()
        attr2 = elem2.attributes()
        texts = []

        for i2 in range(attr2.count()):
            at2 = attr2.item(i2)
            elem1.setAttribute(at2.nodeName(),at2.nodeValue())
        
            
        child1 = elem1.firstChild()
        while not child1.isNull(): 
            if child1.nodeType() == QDomNode.TextNode:
                texts.append(unicode(child1.toText().data()).strip())
            child1 = child1.nextSibling()    

        toMove = []    

        child2 = elem2.firstChild()
        while not child2.isNull(): 
            if child2.nodeType() == QDomNode.TextNode:
                if unicode(child2.toText().data()).strip() not in texts:
                    toMove.append(child2)
            else:    
                toMove.append(child2)
            child2 = child2.nextSibling()    

        for child in toMove:
            elem1.appendChild(child)
        toMove = []    


        parent = elem2.parentNode()    
        parent.removeChild(elem2)


    def mergeChildren(self, node):
        status = False
        if node:
#            print "merging the children of: ", node.nodeName()
            changes = True
            
            children = node.childNodes()
            while changes:
                
                changes = False
                for c1 in range(children.count()):
                    child1 = children.item(c1)
                    elem1 = child1.toElement()
                    for c2 in range(children.count()):
                        child2 = children.item(c2)
                        if child1 != child2:
                            elem2 = child2.toElement()
                            if elem1 is not None and elem2 is not None:
                                if self.areMergeable(elem1,elem2):
                                    self.mergeNodes(elem1, elem2)
                                    changes = True
                                    status = True
                        if changes:
                            break
                    if changes:
                        break
                        
            child = node.firstChild()
            elem = node.toElement()
            nName = unicode(elem.nodeName()) if elem  else ""
            
            if child:
                while not child.isNull():
                    if nName and nName in self.children.keys():
                        childElem = child.toElement()
                        cName = unicode(childElem.nodeName()) if childElem  else ""
                        if cName and cName not in self.children[nName]:
                            raise IncompatibleNodeError,\
                                "Not allowed <%s> child of \n < %s > \n  parent"  \
                                % (cName, self.getAncestors(elem))
                            
                    self.mergeChildren(child)
                    child = child.nextSibling()


    def merge(self):
            self.mergeChildren(self.root)

if __name__ == "__main__":
    import sys

