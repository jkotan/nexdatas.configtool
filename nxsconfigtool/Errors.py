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
# \file Errors.py
# Error classes

""" "Component Desigener Errors  """


# charater error
class CharacterError(Exception):
    pass


# error of passed parameter
class ParameterError(Exception):
    pass


# merging error for wrong node structure
class IncompatibleNodeError(Exception):
    # constructor
    # \param value text of the error
    # \param nodes list of error related nodes
    def __init__(self, value, nodes=None):
        Exception.__init__(self, value)
        # text of the error
        self.value = value
        # list of error related nodes
        self.nodes = nodes if nodes else []
