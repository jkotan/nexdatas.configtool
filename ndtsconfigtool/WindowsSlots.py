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
## \file WindowsSlots.py
# user pool commands of GUI application

""" Windows slots """

from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import (QSignalMapper, Qt, SIGNAL, SLOT)

from .DataSourceDlg import CommonDataSourceDlg
from .ComponentDlg import ComponentDlg


## stack with the application commands
class WindowsSlots(object):

    ## constructor
    # \param length maximal length of the stack
    def __init__(self, main):
        self.main = main
        self.undoStack = main.undoStack

        ## dictionary with window actions
        self.windows = {}

        self.actions = {
            "actionNextWindows":[
                "&Next", "activateNextSubWindow", 
                QKeySequence.NextChild, "", "Go to the next window"],
            "actionPreviousWindows":[
                "&Previous", "activatePreviousSubWindow",
                QKeySequence.PreviousChild, "" ,"Go to the previous window"],
            "actionCascadeWindows":[
                "Casca&de", "cascadeSubWindows" , "", "",
                "Cascade the windows"],
            "actionTileWindows":[
                "&Tile", "tileSubWindows", "", "",  
                "Tile the windows"],
            "actionRestoreAllWindows":[
                "&Restore All", "windowRestoreAll", "", "",
                "Restore the windows"],
            "actionCloseAllWindows":[
                "&Close All", "closeAllSubWindows", "", "", 
                "Close the windows"],
            "actionIconizeAllWindows":[
                "&Iconize All", "windowMinimizeAll", "", "",
                "Minimize the windows"],
            "actionCloseWindows":[
                "&Close", "closeActiveSubWindow", "",
                QKeySequence(Qt.Key_Escape),
                "Close the window" ],
            "actionComponentListWindows":[
                "&Component List", "gotoComponentList", "Ctrl+<", "",
                "Go to the component list" ],
            "actionDataSourceListWindows":[
                "&DataSource List", "gotoDataSourceList", "Ctrl+>", "",
                "Go to the component list" ]
            }

        
        for ac in self.actions.keys():
            self.windows[ac] = getattr(self.main.ui, ac)

        self.windows["Mapper"] = QSignalMapper(self.main)
        self.main.connect(self.windows["Mapper"], SIGNAL("mapped(QWidget*)"),
                     self.main.ui.mdi, SLOT("setActiveWindow(QMdiSubWindow*)"))

        self.windows["Menu"] = self.main.ui.menuWindow
        self.main.connect(self.windows["Menu"], SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)


        # signals

        self.main.connect(
            self.main.ui.mdi, SIGNAL("subWindowActivated(QMdiSubWindow*)"), 
            self.mdiWindowActivated)






    ## activated window action, i.e. it changes the current position 
    #  of the component and datasource lists 
    # \param subwindow selected subwindow
    def mdiWindowActivated(self, subwindow):
        widget = subwindow.widget() if hasattr(subwindow, "widget") else None
        if isinstance(widget, CommonDataSourceDlg):
            if widget.datasource.id is not None:
                if hasattr(self.main.sourceList.currentListElement(),"id"):
                    if self.main.sourceList.currentListElement().id \
                            != widget.datasource.id: 
                        self.main.sourceList.populateElements(
                            widget.datasource.id)
        elif isinstance(widget, ComponentDlg):
            if widget.component.id is not None:
                if hasattr(self.main.componentList.currentListElement(),"id"):
                    if self.main.componentList.currentListElement().id \
                            != widget.component.id:
                        self.main.componentList.populateElements(
                            widget.component.id)


    ## restores all windows
    # \brief It restores all windows in MDI
    def windowRestoreAll(self):
        for dialog in self.main.ui.mdi.subWindowList():
            dialog.showNormal()


    ## minimizes all windows
    # \brief It minimizes all windows in MDI
    def windowMinimizeAll(self):
        for dialog in self.main.ui.mdi.subWindowList():
            dialog.showMinimized()


    ## restores all windows
    # \brief It restores all windows in MDI
    def gotoComponentList(self):
        self.main.componentList.ui.elementListWidget.setFocus()

  
  ## restores all windows
    # \brief It restores all windows in MDI
    def gotoDataSourceList(self):
        self.main.sourceList.ui.elementListWidget.setFocus()

    def activateNextSubWindow(self):
        self.main.ui.mdi.activateNextSubWindow()

    def activatePreviousSubWindow(self):
        self.main.ui.mdi.activatePreviousSubWindow()

    def cascadeSubWindows(self):
        self.main.ui.mdi.cascadeSubWindows()

    def tileSubWindows(self):
        self.main.ui.mdi.tileSubWindows()
 
    def closeAllSubWindows(self):
        self.main.ui.mdi.closeAllSubWindows()

    def closeActiveSubWindow(self):
        self.main.ui.mdi.closeActiveSubWindow()


        

    ## updates the window menu
    # \brief It updates the window menu with the open windows
    def updateWindowMenu(self):
        self.windows["Menu"].clear()
        self._addActions(self.windows["Menu"], 
                         (self.windows["actionNextWindows"],
                          self.windows["actionPreviousWindows"], 
                          self.windows["actionCascadeWindows"],
                          self.windows["actionTileWindows"], 
                          self.windows["actionRestoreAllWindows"],
                          self.windows["actionIconizeAllWindows"],
                          None,
                          self.windows["actionCloseWindows"],
                          self.windows["actionCloseAllWindows"],
                          None,
                          self.windows["actionComponentListWindows"], 
                          self.windows["actionDataSourceListWindows"]
                          ))
        dialogs = self.main.ui.mdi.subWindowList()
        if not dialogs:
            return
        self.windows["Menu"].addSeparator()
        i = 1
        menu = self.windows["Menu"]
        for dialog in dialogs:
            title = dialog.windowTitle()
            if i == 10:
                self.windows["Menu"].addSeparator()
                menu = menu.addMenu("&More")
            accel = ""
            if i < 10:
                accel = "&%s " % unicode(i)
            elif i < 36:
                accel = "&%s " % unicode(chr(i + ord("@") - 9))
            action = menu.addAction("%s%s" % (accel, title))
            self.main.connect(action, SIGNAL("triggered()"),
                         self.windows["Mapper"], SLOT("map()"))
            self.windows["Mapper"].setMapping(action, dialog)
            i += 1


    ## adds actions to target
    # \param target action target
    # \param actions actions to be added   
    @classmethod    
    def _addActions(cls, target, actions):
        if not  hasattr(actions, '__iter__'):
            target.addAction(actions)
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)



if __name__ == "__main__":   
    pass
