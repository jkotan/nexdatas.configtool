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
## \package test nexdatas
## \file runtest.py
# the unittest runner
#

import os 
import unittest

import AttributeDlgTest
import ConnectDlgTest

try:
    import PyTango
    ## if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print "PyTango is not available: %s" % e
    
## list of available databases
DB_AVAILABLE = []
    
try:
    import MySQLdb    
    ## connection arguments to MYSQL DB
    args = {}
    args["db"] = 'tango'
    args["host"] = 'localhost'
    args["read_default_file"] = '/etc/my.cnf'
    ## inscance of MySQLdb
    mydb = MySQLdb.connect(**args)
    mydb.close()
    DB_AVAILABLE.append("MYSQL")
except ImportError, e:
    print "MYSQL not available: %s" % e
except Exception, e:
    print "MYSQL not available: %s" % e
except:
    print "MYSQL not available"



if "MYSQL" in DB_AVAILABLE:
    pass


if PYTANGO_AVAILABLE:
    if "MYSQL" in DB_AVAILABLE:
        pass

## main function
def main():




    ## test server    
    ts = None    
    
    ## test suit
    suite = unittest.TestSuite()

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(AttributeDlgTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ConnectDlgTest) )


    if "MYSQL" in DB_AVAILABLE:
        pass



    if PYTANGO_AVAILABLE:
        if "MYSQL" in DB_AVAILABLE:
            pass


    
    ## test runner
    runner = unittest.TextTestRunner()
    ## test result
    result = runner.run(suite)

 #   if ts:
 #       ts.tearDown()

if __name__ == "__main__":
    main()
