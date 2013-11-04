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
## \file ComponentList.py
# Data component list class


""" component list widget """


from PyQt4.QtGui import QMessageBox

from .Component import Component
from .ElementList import ElementList

## dialog defining a group tag
class ComponentList(ElementList):
    
    ## constructor
    # \param directory element directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ComponentList, self).__init__(directory, parent)

        ## show all attribures or only the type attribute
        self._allAttributes = False

        ## widget title
        self.title = "Components"
        ## element name
        self.name = "components"
        ## class name
        self.clName = "Component"
        ## extention
        self.extention = ".xml"


    ## switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status = None):
        if status is None:
            return self._allAttributes
        self._allAttributes = True if status else False
        for k in self.elements.keys():
            if hasattr(self.elements[k], "instance") \
                    and self.elements[k].instance:
                self.elements[k].instance.viewAttributes(
                    self._allAttributes)
            

    ## removes the current element    
    #  \brief It removes the current element asking before about it
    def removeElement(self, obj = None, question = True):
        super(ComponentList, self).removeElement(obj, question)

        attr = self.currentListElement()
        if attr is None:
            return
        if QMessageBox.question(
            self, "%s - Remove" % self.clName,
            "Remove %s: %s = \'%s\'".encode() \
                %  (self.clName, attr, self.elements[unicode(attr)]),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return
        if unicode(attr) in self.elements.keys():
            self.elements.pop(unicode(attr))
            self.populateElements()


    ## retrives element name from file name
    # \param fname filename
    # \returns element name        
    @classmethod
    def nameFromFile(cls, fname):
        if fname[-4:] == '.xml':
            name = fname[:-4]
        else:
            name = fname
        return name        

    ## creates Element 
    # \param element name
    # \returns element instance
    def createElement(self, name):
        dlg = Component()
        dlg.directory = self.directory
        dlg.name = name
        dlg.createGUI()
        return dlg

            





if __name__ == "__main__":
    import sys
    from PyQt4.QtGui import QApplication

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = ComponentList("../components")
    form.createGUI()
    form.show()
    app.exec_()


    if form.elements:
        print "Other components:"
        for mk in form.elements.keys():
            print  " %s = '%s' " % (mk, form.elements[mk])
    
