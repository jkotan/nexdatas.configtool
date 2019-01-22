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
# \file HelpForm.py
# Detail help for Component Designer

""" help widget """


from PyQt5.QtCore import (QUrl, Qt)
from PyQt5.QtGui import (QKeySequence, QIcon)
from PyQt5.QtWidgets import (
    QAction, QApplication, QDialog,
    QLabel, QTextBrowser, QToolBar, QVBoxLayout)


# detail help
class HelpForm(QDialog):

    # constructor
    # \param page the starting html page
    # \param parent parent widget
    def __init__(self, page, parent=None):
        super(HelpForm, self).__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)

        # help tool bar
        self.toolBar = None
        # help text Browser
        self.textBrowser = None
        # main label of the help
        self.pageLabel = None

        self._page = page
        self.createGUI()
        self.createActions()

    #  creates GUI
    # \brief It create dialogs for help dialog
    def createGUI(self):
        # help tool bar
        self.toolBar = QToolBar(self)
        # help text Browser
        self.textBrowser = QTextBrowser(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolBar)
        layout.addWidget(self.textBrowser, 1)

        self.setLayout(layout)
        self.textBrowser.setSearchPaths([":/help"])
        self.textBrowser.setSource(QUrl(self._page))
        self.resize(660, 700)
        self.setWindowTitle("%s Help" % (
            QApplication.applicationName()))

    # creates actions
    # \brief It creates actions and sets the command pool and stack
    def createActions(self):

        backAction = QAction(QIcon(":/back.png"), "&Back", self)
        backAction.setShortcut(QKeySequence.Back)

        forwardAction = QAction(QIcon(":/forward.png"), "&Forward", self)
        forwardAction.setShortcut("Forward")

        homeAction = QAction(QIcon(":/home.png"), "&Home", self)
        homeAction.setShortcut("Home")

        # main label of the help
        self.pageLabel = QLabel(self)

        self.toolBar.addAction(backAction)
        self.toolBar.addAction(forwardAction)
        self.toolBar.addAction(homeAction)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.pageLabel)

        try:
            backAction.triggered.disconnect(self.textBrowser.backward)
        except Exception:
            pass
        try:
            forwardAction.triggered.disconnect(self.textBrowser.forward)
        except Exception:
            pass
        try:
            homeAction.triggered.disconnect(self.textBrowser.home)
        except Exception:
            pass
        try:
            self.textBrowser.sourceChanged.disconnect(
                        self.updatePageTitle)
        except Exception:
            pass

        backAction.triggered.connect(self.textBrowser.backward)
        forwardAction.triggered.connect(self.textBrowser.forward)
        homeAction.triggered.connect(self.textBrowser.home)
        self.textBrowser.sourceChanged.connect(
                    self.updatePageTitle)

        self.updatePageTitle()

    # updates the title page
    # \brief It resets the pageLabel withg the document title
    def updatePageTitle(self):
        self.pageLabel.setText(
            "<p><b><i><font color='#0066ee' font size = 4>" +
            "&nbsp;&nbsp;" + self.textBrowser.documentTitle()
            + "</i></b></p></br>"
        )


if __name__ == "__main__":
    import sys
    # application instance
    app = QApplication(sys.argv)
    # help form
    form = HelpForm("index.html")
    form.show()
    app.exec_()
