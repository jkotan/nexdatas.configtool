#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package nxsconfigtool nexdatas
# \file ComponentItem.py
# dom item

""" DOM item for component model"""


# dialog defining a tag link
class ComponentItem(object):

    # constructor
    # \param node DOM node of item
    # \param parent patent instance
    def __init__(self, node, parent=None):
        # DOM node
        self.node = node
        # list with child items
        self.__childItems = []
        # the parent ComponentItem of the item
        self.parent = parent

    # provides indexs of given child
    # \param child
    # \returns child index
    def index(self, child):
        return self.__childItems.index(child)

    # provides a number of the current item
    # \returns a number of the current item
    def childNumber(self):
        if self.parent:
            return self.parent.index(self)
        return 0

    # provides the child item for the given list index
    # \param i child index
    # \returns requested child Item
    def child(self, i):
        size = len(self.__childItems)
        if i in range(size):
            return self.__childItems[i]
        if i >= 0 and i < self.node.childNodes().count():
            for j in range(size, i + 1):
                childNode = self.node.childNodes().item(j)
                childItem = ComponentItem(childNode, self)
                self.__childItems.append(childItem)
            return childItem

    # removes the given children from the child item list
    # \param position list index of the first child to remove
    # \param count number of children to remove
    # \returns if indices not out of range
    def removeChildren(self, position, count):
        if position < 0 or position + count > self.node.childNodes().count():
            return False

        for _ in range(count):
            if position < len(self.__childItems):
                self.__childItems.pop(position)

        return True

    # inserts the given children into the child item list
    # \param position list index of the first child to remove
    # \param count number of children to remove
    # \returns if indices not out of range
    def insertChildren(self, position, count):

        if position < 0 or position > self.node.childNodes().count():
            return False

        for i in range(position, position + count):
            if position <= len(self.__childItems):
                childNode = self.node.childNodes().item(i)
                childItem = ComponentItem(childNode, self)
                self.__childItems.insert(i, childItem)

        return True


if __name__ == "__main__":

    from PyQt5.QtXml import QDomNode

    # DOM node
    qdn = QDomNode()
    # instance of component item
    di = ComponentItem(qdn, None)
    di.child(0)
