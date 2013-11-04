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
## \file Command.py
# user commands of GUI application

""" Component Designer commands """

from PyQt4.QtGui import (QUndoCommand)

## abstract command 
class Command(object):
    
    ## constructor
    # \param receiver command receiver
    # \param slot slot name of the receiver related to the command
    def __init__(self, receiver, slot=None):
        ## command receiver
        self.receiver = receiver
        ## command slot name 
        self.slot = slot

    ## connects the slot name to receiver
    # returns callable slot     
    def connectSlot(self):
        if hasattr(self.receiver, self.slot):
            return  getattr(self.receiver, self.slot)
        
    ## executes the command
    # \brief It is an abstract member function to reimplement execution 
    #        of the derived command
    def redo(self):
        pass

    ## unexecutes the command
    # \brief It is an abstract member function to reimplement un-do execution 
    #        of the derived command
    def undo(self):
        pass


    ## clones the command
    # \brief It is an abstract member function to reimplement cloning 
    #        of the derived command
    def clone(self): 
        pass







        

if __name__ == "__main__":
    pass

