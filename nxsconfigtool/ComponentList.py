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
# \file ComponentList.py
# Data component list class


""" component list widget """


from .Component import Component
from .ElementList import ElementList

import logging
# message logger
logger = logging.getLogger("nxsdesigner")


# dialog defining a group tag
class ComponentList(ElementList):

    # constructor
    # \param directory element directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ComponentList, self).__init__(directory, parent)

        # show all attribures or only the type attribute
        self._allAttributes = False

        # widget title
        self.title = "Components"
        # element name
        self.name = "components"
        # class name
        self.clName = "Component"
        # extention
        self.extention = ".xml"
        # excluded extention
        self.disextention = "ds.xml"

    # switches between all attributes in the try or only type attribute
    # \param status all attributes are shown if True
    def viewAttributes(self, status=None):
        if status is None:
            return self._allAttributes
        self._allAttributes = True if status else False
        for k in self.elements.keys():
            if hasattr(self.elements[k], "instance") \
                    and self.elements[k].instance:
                self.elements[k].instance.viewAttributes(
                    self._allAttributes)

    # retrives element name from file name
    # \param fname filename
    # \returns element name
    @classmethod
    def nameFromFile(cls, fname):
        if fname[-4:] == '.xml':
            name = fname[:-4]
        else:
            name = fname
        return name

    # creates Element
    # \param name element name
    # \returns element instance
    def createElement(self, name):
        dlg = Component(self)
        dlg.directory = self.directory
        dlg.name = name
        dlg.createGUI()
        return dlg

    def dataSourceComponents(self, datasource):
        comps = set()
        for cp in self.elements.values():
            if cp and cp.name and cp.instance:
                if hasattr(cp.instance, "datasources"):
                    if datasource in cp.instance.datasources:
                        comps.add(cp.name)
        return list(comps)


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # group form
    form = ComponentList("../components")
    form.createGUI()
    form.show()
    app.exec_()

    if form.elements:
        logger.info("Other components:")
        for mk in form.elements.keys():
            logger.info(" %s = '%s' " % (mk, form.elements[mk]))
