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
## \file ComponentDesigner.pyw
# GUI to create the XML components 

""" Component Designer - configuration tool for Nexus Data Writer """

import logging
import sys
from optparse import OptionParser

from PyQt4.QtGui import (QApplication, QIcon)


from ndtsconfigtool.MainWindow import MainWindow
from ndtsconfigtool.qrc import qrc_resources


## the main function
def main():
    levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    usage = "usage: ComponentDesigner.pyw [-l logging level] "\
        "[-c components] [-d datasources] [-s server]"

    parser = OptionParser(usage=usage)

    parser.add_option(
        "-l","--log", dest="log", 
        help="logging level, i.e. debug, info, warning, error, critical")
    parser.add_option(
        "-c","--components", dest="components", 
        help="directory with components")
    parser.add_option(
        "-d","--datasources", dest="datasources", 
        help="directory with datasources")
    parser.add_option(
        "-s","--server", dest="server", 
        help="configuration server")

    (options, args) = parser.parse_args()


    if options.log:
        level_name = options.log
        level = levels.get(level_name, logging.NOTSET)
        logging.basicConfig(level=level)     

#    import gc
#    gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)
#    gc.set_debug(gc.DEBUG_LEAK )
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icon.png"))
    app.setOrganizationName("DESY")
    app.setOrganizationDomain("desy.de")
    app.setApplicationName("NDTS Component Designer")
    form = MainWindow(options.components, options.datasources, options.server)
    form.show()

    sys.exit(app.exec_())



if __name__ == "__main__":
    main()


