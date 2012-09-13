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

from Command import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class CommandStack(object):
    def __init__(self):
        self._stack = []
        self._current = 0

    def append(self, command):
        while self._current < len(self._stack):
            self._stack.pop()
        self._stack.append(command)    
        self._current += 1
        print "append",  self._current , len(self._stack) 

    
    def undo(self):
        if self._stack and self._current > 0 :
            self._current -= 1
            print "undo",  self._current , len(self._stack) 
            return self._stack[self._current]

    def redo(self):
#        print  "st", self._current - 1, self._current , len(self._stack) 
        if self._stack and self._current < len(self._stack) :
            self._current += 1
            print "redo",  self._current , len(self._stack) 
            return self._stack[ self._current - 1 ]

    def isEmpty(self):
        return self._current == 0
       
    def isFinal(self):
        return self._current == len(self._stack)

    def clear(self):
        self._stack = []
        self._current = 0
        


    
class CommandPool(object):
    def __init__(self,origin):
        self._pool = {}
        self._actions = {}
        if hasattr(origin, 'connect'):
            self.origin = origin
        else:
            raise ValueError, "Origin without 'connect' attribute"

    def createCommand(self, text, name, args, command=None,  shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self.origin)
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
            self.origin.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        self._actions[name] = action
           
        return action



    def createTask(self, name, args, command,  instance, signal):
        if name not in  self._pool.keys():
            largs = args
            largs["slot"] = name 
            self._pool[name] = command(**largs)        
            slot = self._pool[name].connectSlot()
        if slot is not None:
            self.origin.connect(instance, SIGNAL(signal), slot)
        self._actions[name] = None




    def setDisabled(self, name, flag):
        if name in self._actions.keys():
            self._actions[name].setDisabled(flag)


    def getCommand(self, name):
        if name not in self._pool.keys():
            return
        return self._pool[name].clone()
        
    def removeCommand(self, name):
        if name in self._pool.keys():
            self._pool.pop(name)
        if name in self._actions.keys():
            self._actions.pop(name)
        
class TestMainWindow(QMainWindow):
    pass

if __name__ == "__main__":   

    import sys
    app=QApplication(sys.argv)
    win=TestMainWindow()
    win.show()

    

#    actionObj2 = ActionClass()
#    actionObj = ActionMemClass()

#    args = { 'receiver':actionObj, 'action':'myAction',  } 
    pool = CommandPool(app)
    pool.createAction("&New", "fileNew",  app, ComponentNew,
                      QKeySequence.New, "filenew", "Create a text file")
                       
#    pool.getCommand("com1",args)
    
    app.exec_()
