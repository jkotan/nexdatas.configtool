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

class IncompatibleNodeError(Exception): pass


## merges the components
class Merger(object):
    
    ## constructor
    # \param root  DOM root node
    def __init__(self, root):
        
        ## DOM root node
        self.root = root

    def getText(self, node):
        text = QString()
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
        return text    


    def areMergeable(self,elem1, elem2):
        if elem1.nodeName() != elem2.nodeName():
            return False
        tagName = elem1.nodeName()
        attr1 = elem1.attributes()
        attr2 = elem2.attributes()
        
        name1 = attr1.namedItem("name").nodeValue() \
            if attr1.contains("name") else ""
        name2 = attr2.namedItem("name").nodeValue() \
            if attr1.contains("name") else ""
        
        if name1 != name2 or not name1:
            if tagName != 'datasource':
                return False
            else:
                raise IncompatibleNodeError,\
                    "Two datasource for one field %s %s" % (name1, name2)

        ## TODO   correct dim?
        for i1 in range(attr1.count()):
            for i2 in range(attr2.count()):
                at1 = attr1.item(i1)
                at2 = attr2.item(i2)
                if at1.nodeName() == at2.nodeName() and at1.nodeValue() != at2.nodeValue():
                    raise IncompatibleNodeError,\
                        "Incompatible element attributes  %s: %s = %s / %s " \
                        % (tagName, at1.nodeName(), at1.nodeValue() , at2.nodeValue())

        if tagName == 'field':
            text1=self.getText(elem1).strip()
            text2=self.getText(elem2).strip()         
            ## TODO white spaces?
            if text1 != text2:
                raise IncompatibleNodeError,\
                    "Incompatible %s element value   %s \n  %s "  \
                    % (tagName,text1, text2)
            
                      
                      
#if check tag value are not compatible 
#        (text additable? :not for fields)

        return True

    def mergeNodes(self,node1, node2):
        print "merging nodes:" ,node1.nodeName(), node2.nodeName()


#        if node1.nodeType() == QDomNode.TextNode and node2.nodeType() == QDomNode.TextNode:
# if texnode and value is different

    def mergeChildren(self, node):
        if node:
            print "merging the children of: ", node.nodeName()

            child1 = node.firstChild()
            child2 = child1.nextSibling()
            if child1 and child2:
                while not child1.isNull():
                    while not child2.isNull():
                        if child1 != child2:
                            elem1 = child1.toElement()
                            elem2 = child2.toElement()
                            if elem1 is not None and elem2 is not None:
                                if self.areMergeable(child1,child2):
                                    self.mergeNodes(child1, child2)

                                print "compering:" ,child1.nodeName(),child2.nodeName()
                        child2 = child2.nextSibling()
                    child1 = child1.nextSibling()



            child = node.firstChild()
            if child:
                while not child.isNull():
                    self.mergeChildren(child)
                    child = child.nextSibling()


    def merge(self):
        try:
            self.mergeChildren(self.root)
        except IncompatibleNodeError, e: 
            print "Error in Merging: %s" % unicode(e)

if __name__ == "__main__":
    import sys

