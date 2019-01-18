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
# \file DomTools.py
# Abstract Node dialog class

"""  DOM parser and tree view tools"""

from PyQt5.QtXml import QDomNode
import re


# abstract node dialog
class DomTools(object):

    # provides a list of elements from the given text
    # \param text give text
    # \param label element label
    # \returns list of element names from the given text
    @classmethod
    def findElements(self, text, label):
        variables = []
        index = text.find("$%s." % label)
        while index != -1:
            try:
                subc = re.finditer(
                    r"[\w]+",
                    text[(index + len(label) + 2):]
                ).next().group(0)
            except Exception:
                subc = ""
            name = subc.strip() if subc else ""
            if name:
                variables.append(name)
            index = text.find("$%s." % label, index + 1)
        return variables

    # provides row number of the given node
    # \param child child item
    # \param node parent node
    # \returns row number
    @classmethod
    def getNodeRow(cls, child, node):
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

    # provides node text for the given node
    # \param node DOM node
    # \returns string with node texts
    @classmethod
    def getText(cls, node):
        text = ""
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
        return text

    # provides row number of the given element
    # \param element DOM element
    # \param node DOM node
    # \returns row number
    @classmethod
    def __getElementRow(cls, element, node):
        row = 0
        if node:
            children = node.childNodes()
            for i in range(children.count()):
                ch = children.item(i)
                if ch.isElement() and element == ch.toElement():
                    break
                row += 1
            if row < children.count():
                return row

    # replaces node text for the given node
    # \param node parent DOM node
    # \param index of child text node
    # \param model Component model
    # \param text string with text
    @classmethod
    def replaceText(cls, node, index, model, text=None):
        if node:
            root = model.rootIndex.internalPointer().node
            children = node.childNodes()
            i = 0
            j = 0
            while i < children.count():
                child = children.item(i)
                if child.nodeType() == QDomNode.TextNode:
                    if j == 0 and text:
                        child.toText().setData(str(text))
                    else:
                        child.toText().setData(str(""))
                    j += 1
                i += 1

            if j == 0 and text:
                textNode = root.createTextNode(str(text))
                cls.appendNode(textNode, index, model)

    # removes node
    # \param node DOM node to remove
    # \param parent parent node index
    # \param model Component model
    @classmethod
    def removeNode(cls, node, parent, model):
        if not parent or not hasattr(parent, "internalPointer") \
                or not hasattr(parent.internalPointer(), "node"):
            return
        row = cls.getNodeRow(node, parent.internalPointer().node)
        if row is not None:
            model.removeItem(row, parent)

    # replaces node
    # \param oldNode old DOM node
    # \param newNode new DOM node
    # \param parent parent node index
    # \param model Component model
    @classmethod
    def replaceNode(cls, oldNode, newNode, parent, model):
        if not parent or not hasattr(parent, "internalPointer") \
                or not hasattr(parent.internalPointer(), "node"):
            return
        node = parent.internalPointer().node
        row = cls.getNodeRow(oldNode, node)
        if row is not None:
            model.removeItem(row, parent)
            if row < node.childNodes().count():
                model.insertItem(row, newNode, parent)
            else:
                model.appendItem(newNode, parent)

    # appends node
    # \param node DOM node to append
    # \param parent parent node index
    # \param model Component model
    @classmethod
    def appendNode(cls, node, parent, model):
        if model.appendItem(node, parent):
            return True

    # removes node element
    # \param element DOM node element to remove
    # \param parent parent node index
    # \param model Component model
    @classmethod
    def removeElement(cls, element, parent, model):
        if not parent or not hasattr(parent, "internalPointer") \
                or not hasattr(parent.internalPointer(), "node"):
            return
        row = cls.__getElementRow(element, parent.internalPointer().node)
        if row is not None:
            model.removeItem(row, parent)

    # replaces node element
    # \param oldElement old DOM node element
    # \param newElement new DOM node element
    # \param parent parent node index
    # \param model Component model
    @classmethod
    def replaceElement(cls, oldElement, newElement, parent, model):
        if not parent or not hasattr(parent, "internalPointer") \
                or not hasattr(parent.internalPointer(), "node"):
            return
        node = parent.internalPointer().node
        row = cls.__getElementRow(oldElement, node)
        if row is not None:
            model.removeItem(row, parent)
            if row < node.childNodes().count():
                model.insertItem(row, newElement, parent)
            else:
                model.appendItem(newElement, parent)

    # provides the first element in the tree with the given name
    # \param node DOM node
    # \param name child name
    # \returns DOM child node
    @classmethod
    def getFirstElement(cls, node, name):
        if node:
            child = node.firstChild()
            if child:
                while not child.isNull():
                    if child and child.nodeName() == name:
                        return child
                    child = child.nextSibling()

            child = node.firstChild()
            if child:
                while not child.isNull():
                    elem = cls.getFirstElement(child, name)
                    if elem:
                        return elem
                    child = child.nextSibling()


if __name__ == "__main__":
    pass
