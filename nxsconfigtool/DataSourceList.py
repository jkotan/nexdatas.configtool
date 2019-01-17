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
# \file DataSourceList.py
# Data source list class

""" datasource list widget """


from .DataSource import DataSource
from .ElementList import ElementList

import logging
# message logger
logger = logging.getLogger("nxsdesigner")


# dialog defining a group tag
class DataSourceList(ElementList):

    # constructor
    # \param directory element directory
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(DataSourceList, self).__init__(directory, parent)

        # widget title
        self.title = "DataSources"
        # element name
        self.name = "datasources"
        # class name
        self.clName = "DataSource"
        # extention
        self.extention = ".ds.xml"

    # retrives element name from file name
    # \param fname filename
    # \returns element name
    @classmethod
    def nameFromFile(cls, fname):
        if fname[-4:] == '.xml':
            name = fname[:-4]
            if name[-3:] == '.ds':
                name = name[:-3]
        else:
            name = fname
        return name

    # creates Element
    # \param name element name
    # \returns element instance
    def createElement(self, name):
        dlg = DataSource(self)
        dlg.directory = self.directory
        dlg.name = name
        dlg.createGUI()
        return dlg

    # replaces name special characters by underscore
    # \param name give name
    # \returns replaced element
    @classmethod
    def dashName(cls, name):
        res = "".join(
            x.replace('/', '_').replace('\\', '_').replace(':', '_')
            for x in name if (x.isalnum() or x in ["/", "\\", ":", "_"]))
        return res


if __name__ == "__main__":
    import sys
    from PyQt5.QtGui import QApplication

    logging.basicConfig(level=logging.DEBUG)

    # Qt application
    app = QApplication(sys.argv)
    # group form
    form = DataSourceList("../datasources")
#    form.elements={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()

    if form.elements:
        logger.info("Other datasources:")
        for k in form.elements.keys():
            logger.info(" %s = '%s' " % (k, form.elements[k]))
