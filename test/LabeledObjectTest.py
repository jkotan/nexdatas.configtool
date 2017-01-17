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
## \file LabeledObjectTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import binascii
import time


from nxsconfigtool.LabeledObject import LabeledObject


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class LabeledObjectTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        ## MessageBox text
        self.text = None
        ## MessageBox title
        self.title = None
        ## action status
        self.performed = False


        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 


        self.__rnd = random.Random(self.__seed)


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        
        print "SEED =", self.__seed 
        


    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."



    def test_isdirty(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)  

        name = "name1"
        newname = "name2"
        instance = "my instance"
        lo = LabeledObject(name,instance)
        self.assertEqual(lo.name, name)
        self.assertEqual(lo.instance, instance)
        self.assertEqual(lo.savedName, name)
        self.assertTrue(not lo.isDirty())

        lo.savedName = newname
        lo.name = name
        self.assertTrue(lo.isDirty())


        lo.savedName = name
        lo.name = newname
        self.assertTrue(lo.isDirty())

        lo.savedName = newname
        lo.name = newname
        self.assertTrue(not lo.isDirty())





if __name__ == '__main__':
    unittest.main()
