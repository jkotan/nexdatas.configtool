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
## \package test nexdatas
## \file runtest.py
# the unittest runner
#

import os
import sys
import unittest


from PyQt4.QtGui import QApplication


import AttributeDlgTest
import ConnectDlgTest
import DimensionsDlgTest
import DefinitionDlgTest
import GroupDlgTest
import FieldDlgTest
import NodeDlgTest
import ComponentItemTest
import ComponentModelTest
import DomToolsTest
import RichAttributeDlgTest
import LinkDlgTest
import StrategyDlgTest
import LabeledObjectTest
import CommonDataSourceDlgTest
import DataSourceDlgTest
import CommonDataSourceTest
import DataSourceTest
import DataSourceMethodsTest



try:
    import PyTango
    ## if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print "PyTango is not available: %s" % e
    
## list of available databases
DB_AVAILABLE = []
    

    
## main function
def main():


    ## test server    
    ts = None    
    
    ## test suit
    suite = unittest.TestSuite()


    app = QApplication([])
    NodeDlgTest.app = app
    DefinitionDlgTest.app = app
    AttributeDlgTest.app = app
    ConnectDlgTest.app = app
    DimensionsDlgTest.app = app
    GroupDlgTest.app = app
    ComponentItemTest.app = app
    DomToolsTest.app = app
    RichAttributeDlgTest.app = app
    LinkDlgTest.app = app
    StrategyDlgTest.app = app
    LabeledObjectTest.app = app
    CommonDataSourceDlgTest.app = app
    DataSourceDlgTest.app = app
    CommonDataSourceTest.app = app
    DataSourceTest.app = app
    DataSourceMethodsTest.app = app



    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(AttributeDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(LinkDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(StrategyDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ConnectDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DimensionsDlgTest) )


    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DefinitionDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(GroupDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FieldDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(RichAttributeDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(NodeDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ComponentItemTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ComponentModelTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DomToolsTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(LabeledObjectTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(CommonDataSourceDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(CommonDataSourceTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceMethodsTest) )



    ## test runner
    runner = unittest.TextTestRunner()
    ## test result
    result = runner.run(suite).wasSuccessful()
    sys.exit(not result)

 #   if ts:
 #       ts.tearDown()

if __name__ == "__main__":
    main()
