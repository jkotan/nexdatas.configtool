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


    def areMergeable(self,node1, node2):
        if node1.nodeName() != node2.nodeName():
            return 0
        return 1

    def mergeNodes(self,node1, node2):
        print "merging nodes:" ,node1.nodeName(), node2.nodeName()


    def mergeChildren(self, node):
        if node:
            print "merging the children of: ", node.nodeName()

            child1 = node.firstChild()
            child2 = child1.nextSibling()
            if child1 and child2:
                while not child1.isNull():
                    while not child2.isNull():
                        if child1 != child2:
                            status = self.areMergeable(child1,child2)
                            if status == 1:
                                self.mergeNodes(child1, child2)
                            if status == -1:
                                raise IncompatibleNodeError,"Please change the node %s and %s" % (child1.nodeName(),child2.nodeName())

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

