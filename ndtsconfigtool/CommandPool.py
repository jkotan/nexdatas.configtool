#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \file CommandPool.py
# user pool commands of GUI application

from PyQt4.QtGui import  (QAction, QIcon) 
from PyQt4.QtCore import (QString, SIGNAL)


## stack with the application commands
class CommandStack(object):

    ## constructor
    # \param length maximal length of the stack
    def __init__(self, length):
        ## maximal length of the stack        
        self._maxlen = length if length > 1 else 2
        self._stack = []
        self._current = 0


    ## appends command to stack
    # \param command appended command    
    def append(self, command):
        while self._current < len(self._stack):
            self._stack.pop()
        self._stack.append(command)    
        if self._maxlen >= self._current:
            self._current += 1
        else:
            self._stack.pop(0)
        print "append",  self._current , len(self._stack) 


    ## provides the previously performed command    
    # \returns the previously performed command    
    def undo(self):
        if self._stack and self._current > 0 :
            self._current -= 1
            print "undo",  self._current , len(self._stack) 
            return self._stack[self._current]

    ## provides the previously unexecuted command    
    # \returns the previously unexecuted command    
    def redo(self):
#        print  "st", self._current - 1, self._current , len(self._stack) 
        if self._stack and self._current < len(self._stack) :
            self._current += 1
            print "redo",  self._current , len(self._stack) 
            return self._stack[ self._current - 1 ]

    ## provides name of  of previously performed command    
    # \returns slot name of previously performed command    
    def getUndoName(self) :
        if self._current > 0 :
            return self._stack[self._current-1].slot

    ## provides name of  of previously unexecuted command    
    # \returns slot name of previously unexecuted command    
    def getRedoName(self) :
        if self._current <  len(self._stack):
            return self._stack[self._current].slot
    
        
    ## checks if stack is empty
    # \returns True if it is not possible to perform the undo operation    
    def isEmpty(self):
        return self._current == 0
       
    ## checks if stack is full
    # \returns True if it is not possible to perform the redo operation    
    def isFinal(self):
        return self._current == len(self._stack)

    ## clears the stack
    # \brief It sets current command counter to 0 and clear the stack list
    def clear(self):
        self._stack = []
        self._current = 0
        


    
## pool with the application commands
class CommandPool(object):
    ## constructor
    # \param origin instance for which the command is called
    def __init__(self, origin):
        self._pool = {}
        self._actions = {}
        if hasattr(origin, 'connect'):
            self._origin = origin
        else:
            raise ValueError, "Origin without 'connect' attribute"


    ## creates the required command instance
    # \param text string shown in menu
    # \param name name of the action member function, i.e. command label
    # \param args parameters of the command constructor
    # \param command name of the command class
    # \param shortcut key short-cut
    # \param icon qrc_resource icon name
    # \param tip text for status bar and text hint
    # \param checkable if command/action checkable
    # \param signal action signal   
    # \returns the action instance
    def createCommand(self, text, name, args, command=None,  shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self._origin)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % str(icon).strip()))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if name not in  self._pool.keys():
            largs = args
            largs["slot"] = name 
            self._pool[name] = command(**largs)        
            slot = self._pool[name].connectSlot()
        if slot is not None:
            self._origin.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        self._actions[name] = action
           
        return action



    ## creates the required task
    # \param name name of the action member function, i.e. command label
    # \param args parameters of the command constructor
    # \param command name of the command class
    # \param instance of the slot
    # \param signal action signal   
    def createTask(self, name, args, command,  instance, signal):
        if name not in  self._pool.keys():
            largs = args
            largs["slot"] = name 
            self._pool[name] = command(**largs)        
            slot = self._pool[name].connectSlot()
        if slot is not None:
            self._origin.connect(instance, SIGNAL(signal), slot)
        self._actions[name] = None




    ## sets command as disable/enable
    # \param name name of the action member function, i.e. command label
    # \param flag True for disable False for enable
    # \param status status to be shown in status bar 
    # \param toShow additional text to show if the action does not have toolTip
    def setDisabled(self, name, flag, status = None, toShow = None):
        if name in self._actions.keys():
            self._actions[name].setDisabled(flag)
            if status is not None:
                if toShow is not None and toShow in self._actions.keys():
                    if hasattr(self._actions[toShow],"toolTip"):
                        tip = QString(status) + self._actions[toShow].toolTip()
                    else:
                        tip = QString(status) + toShow
                else:
                    tip = QString(status)
                self._actions[name].setToolTip(tip)
                self._actions[name].setStatusTip(tip)



    ## provides the required command
    # \param name name of the action member function, i.e. command label
    # \returns clone of the command instance from the pool
    def getCommand(self, name):
        if name not in self._pool.keys():
            return
        return self._pool[name].clone()
        
    ## removes the given command from the ppol
    # \param name name of the action member function, i.e. command label
    def removeCommand(self, name):
        if name in self._pool.keys():
            self._pool.pop(name)
        if name in self._actions.keys():
            self._actions.pop(name)
        

if __name__ == "__main__":   

    import sys
