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
# \package test nexdatas
# \file runtest.py
# the unittest runner
#

import sys
import unittest


from PyQt5.QtWidgets import QApplication


import AttributeDlg_test
import ConnectDlg_test
import DimensionsDlg_test
import DefinitionDlg_test
import GroupDlg_test
import FieldDlg_test
import NodeDlg_test
import ComponentItem_test
import ComponentModel_test
import DomTools_test
import RichAttributeDlg_test
import LinkDlg_test
import StrategyDlg_test
import LabeledObject_test
import CommonDataSourceDlg_test
import DataSourceDlg_test
import CommonDataSource_test
import DataSource_test
import DataSourceMethods_test


try:
    __import__("PyTango")
    # if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError as e:
    PYTANGO_AVAILABLE = False
    print("PyTango is not available: %s" % e)

# list of available databases
DB_AVAILABLE = []


# main function
def main():

    # test server
    # ts = None

    # test suit
    suite = unittest.TestSuite()

    app = QApplication([])
    NodeDlg_test.app = app
    DefinitionDlg_test.app = app
    AttributeDlg_test.app = app
    ConnectDlg_test.app = app
    DimensionsDlg_test.app = app
    GroupDlg_test.app = app
    ComponentItem_test.app = app
    DomTools_test.app = app
    RichAttributeDlg_test.app = app
    LinkDlg_test.app = app
    StrategyDlg_test.app = app
    LabeledObject_test.app = app
    CommonDataSourceDlg_test.app = app
    DataSourceDlg_test.app = app
    CommonDataSource_test.app = app
    DataSource_test.app = app
    DataSourceMethods_test.app = app

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(AttributeDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(LinkDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(StrategyDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ConnectDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DimensionsDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DefinitionDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(GroupDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FieldDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(RichAttributeDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(NodeDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ComponentItem_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ComponentModel_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DomTools_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(LabeledObject_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(
            CommonDataSourceDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceDlg_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(CommonDataSource_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSource_test))

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceMethods_test))

    # test runner
    runner = unittest.TextTestRunner()
    # test result
    result = runner.run(suite).wasSuccessful()
    sys.exit(not result)

    #   if ts:
    #       ts.tearDown()


if __name__ == "__main__":
    main()
