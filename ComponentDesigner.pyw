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

import sys

from PyQt4.QtGui import (QApplication, QIcon)


import ndtsconfigtool     
from ndtsconfigtool.MainWindow import MainWindow
from ndtsconfigtool.qrc import qrc_resources


if __name__ == "__main__":
    import gc
#    gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)
#    gc.set_debug(gc.DEBUG_LEAK )
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icon.png"))
    app.setOrganizationName("DESY")
    app.setOrganizationDomain("desy.de")
    app.setApplicationName("NDTS Component Designer")
    form = MainWindow()
    form.show()
    app.exec_()
    


