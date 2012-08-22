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
## \file ComponentItem.py
# dom item

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *


## dialog defining a tag link 
class ComponentItem(object):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, node, row, parent = None):
        
        
        self.node = node
        self.childItems = {}
        self.parent = parent
        self.row = row
        
    def child(self, i):
        if i in self.childItems.keys():
            return self.childItems[i]
        if i >=0 and i < self.node.childNodes().count():
            childNode = self.node.childNodes().item(i)
            childItem = ComponentItem(childNode, i, self)
            self.childItems[i] = childItem
            return childItem

if __name__ == "__main__":
    import sys

    qdn = QDomNode()
    di = ComponentItem(qdn, 1,None)
    di.child(0)
