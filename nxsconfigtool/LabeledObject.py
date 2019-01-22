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
# \file LabeledObject.py
# object with label and ID

""" labeled object for component and datasource lists"""


# item of the component or datasource list
class LabeledObject(object):
    # constructor
    # \param name item name
    # \param instance instance related to the item
    def __init__(self, name, instance):
        # item name
        self.name = name
        # saved item name
        self.savedName = name
        # item instance
        self.instance = instance
        # item id
        self.id = id(self)

    # checks if the name is not saved
    # returns False if the name is not saved
    def isDirty(self):
        return False if self.name == self.savedName else True
