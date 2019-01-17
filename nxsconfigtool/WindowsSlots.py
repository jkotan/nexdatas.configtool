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
# \file WindowsSlots.py
# user pool commands of GUI application

""" Windows slots """
import sys

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import (QSignalMapper, Qt)

from .DataSourceDlg import CommonDataSourceDlg
from .ComponentDlg import ComponentDlg


if sys.version_info > (3,):
    unicode = str


# stack with the application commands
class WindowsSlots(object):

    # constructor
    # \param main the main window dialog
    def __init__(self, main):
        # main window
        self.main = main
        # command stack
        self.undoStack = main.undoStack

        # dictionary with window actions
        self.windows = {}

        # action data
        self.actions = {
            "actionNextWindows": [
                "&Next", "activateNextSubWindow",
                QKeySequence.NextChild, "", "Go to the next window"],
            "actionPreviousWindows": [
                "&Previous", "activatePreviousSubWindow",
                QKeySequence.PreviousChild, "", "Go to the previous window"],
            "actionCascadeWindows": [
                "Casca&de", "cascadeSubWindows", "", "",
                "Cascade the windows"],
            "actionTileWindows": [
                "&Tile", "tileSubWindows", "", "",
                "Tile the windows"],
            "actionRestoreAllWindows": [
                "&Restore All", "windowRestoreAll", "", "",
                "Restore the windows"],
            "actionCloseAllWindows": [
                "&Close All", "closeAllSubWindows", "", "",
                "Close the windows"],
            "actionIconizeAllWindows": [
                "&Iconize All", "windowMinimizeAll", "", "",
                "Minimize the windows"],
            "actionCloseWindows": [
                "&Close", "closeActiveSubWindow", "",
                QKeySequence(Qt.Key_Escape),
                "Close the window"],
            "actionComponentListWindows": [
                "&Component List", "gotoComponentList", "Ctrl+<", "",
                "Go to the component list"],
            "actionDataSourceListWindows": [
                "&DataSource List", "gotoDataSourceList", "Ctrl+>", "",
                "Go to the component list"]
        }

        for ac in self.actions.keys():
            self.windows[ac] = getattr(self.main.ui, ac)

        self.windows["Mapper"] = QSignalMapper(self.main)
        self.windows["Menu"] = self.main.ui.menuWindow

        # self.main.connect(self.windows["Mapper"], SIGNAL("mapped(QWidget*)"),
        #                   self.main.setActiveSubWindow)
        self.windows["Mapper"].mapped.connect(self.main.setActiveSubWindow)

        # self.main.connect(self.windows["Menu"], SIGNAL("aboutToShow()"),
        #                   self.updateWindowMenu)
        self.windows["Menu"].aboutToShow.connect(self.updateWindowMenu)
        # self.main.connect(
        #     self.main.ui.mdi, SIGNAL("subWindowActivated(QMdiSubWindow*)"),
        #     self.mdiWindowActivated)
        self.main.ui.mdi.subWindowActivated.connect(self.mdiWindowActivated)

    # activated window action, i.e. it changes the current position
    #  of the component and datasource lists
    # \param subwindow selected subwindow
    def mdiWindowActivated(self, subwindow):
        widget = subwindow.widget() if hasattr(subwindow, "widget") else None
        if isinstance(widget, CommonDataSourceDlg):
            if widget.datasource.id is not None:
                if hasattr(self.main.sourceList.currentListElement(), "id"):
                    if self.main.sourceList.currentListElement().id \
                            != widget.datasource.id:
                        self.main.sourceList.populateElements(
                            widget.datasource.id)
        elif isinstance(widget, ComponentDlg):
            if widget.component.id is not None:
                if hasattr(self.main.componentList.currentListElement(), "id"):
                    if self.main.componentList.currentListElement().id \
                            != widget.component.id:
                        self.main.componentList.populateElements(
                            widget.component.id)

    # restores all windows
    # \brief It restores all windows in MDI
    def windowRestoreAll(self):
        for dialog in self.main.ui.mdi.subWindowList():
            dialog.showNormal()

    # minimizes all windows
    # \brief It minimizes all windows in MDI
    def windowMinimizeAll(self):
        for dialog in self.main.ui.mdi.subWindowList():
            dialog.showMinimized()

    # restores all windows
    # \brief It restores all windows in MDI
    def gotoComponentList(self):
        self.main.componentList.ui.elementListWidget.setFocus()

    # restores all windows
    # \brief It restores all windows in MDI
    def gotoDataSourceList(self):
        self.main.sourceList.ui.elementListWidget.setFocus()

    # activates the next subwindow
    def activateNextSubWindow(self):
        self.main.ui.mdi.activateNextSubWindow()

    # activates the previous subwindow
    def activatePreviousSubWindow(self):
        self.main.ui.mdi.activatePreviousSubWindow()

    # cascades the subwindows
    def cascadeSubWindows(self):
        self.main.ui.mdi.cascadeSubWindows()

    # tiles the subwindows
    def tileSubWindows(self):
        self.main.ui.mdi.tileSubWindows()

    # closes all subwindows
    def closeAllSubWindows(self):
        self.main.ui.mdi.closeAllSubWindows()

    # closes the active subwindow
    def closeActiveSubWindow(self):
        self.main.ui.mdi.closeActiveSubWindow()

    # updates the window menu
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

            # self.main.connect(action, SIGNAL("triggered()"),
            #                   self.windows["Mapper"], SLOT("map()"))
            action.triggered.connect(self.windows["Mapper"].map)
            self.windows["Mapper"].setMapping(action, dialog)
            i += 1

    # adds actions to target
    # \param target action target
    # \param actions actions to be added
    @classmethod
    def _addActions(cls, target, actions):
        if not hasattr(actions, '__iter__'):
            target.addAction(actions)
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    # closes the current window
    # \brief Is closes the current datasource window
    def dsourceClose(self):
        subwindow = self.main.ui.mdi.activeSubWindow()
        if subwindow and isinstance(subwindow.widget(), CommonDataSourceDlg) \
                and subwindow.widget().datasource:

            ds = subwindow.widget().datasource

            ds.updateForm()
            if ds.dialog:
                ds.dialog.reject()

            self.main.setActiveSubWindow(subwindow)
            self.main.ui.mdi.closeActiveSubWindow()

    # closes the current window
    # \brief Is closes the current component window
    def componentClose(self):
        subwindow = self.main.ui.mdi.activeSubWindow()
        if subwindow and isinstance(subwindow.widget(), ComponentDlg) \
                and subwindow.widget().component:
            cp = subwindow.widget().component

            if cp.dialog:
                cp.dialog.reject()

            self.main.setActiveSubWindow(subwindow)
            self.main.ui.mdi.closeActiveSubWindow()


if __name__ == "__main__":
    pass
