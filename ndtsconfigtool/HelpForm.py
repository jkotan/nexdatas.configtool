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
## \file HelpForm.py
# Detail help for Component Designer



from PyQt4.QtCore import (QUrl, Qt, SIGNAL, SLOT)
from PyQt4.QtGui import (QAction, QApplication, QDialog, QIcon,
        QKeySequence, QLabel, QTextBrowser, QToolBar, QVBoxLayout, QFrame)

from qrc import qrc_resources

## detail help
class HelpForm(QDialog):

    ## constructor
    # \param page the starting html page
    # \param parent parent widget
    def __init__(self, page, parent=None):
        super(HelpForm, self).__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)

        self._page = page
        self.createGUI()
        self.createActions()

        self.textBrowser.home()



    ##  creates GUI
    # \brief It create dialogs for help dialog
    def createGUI(self):   
        ## help tool bar
        self.toolBar = QToolBar()
        ## help text Browser
        self.textBrowser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.toolBar)
        layout.addWidget(self.textBrowser, 1)

        self.setLayout(layout)
        self.textBrowser.setSearchPaths([":/help"])
        self.textBrowser.setSource(QUrl(self._page))
        self.resize(660, 700)
        self.setWindowTitle("%s Help" % (
                QApplication.applicationName()))


    ## creates actions
    # \brief It creates actions and sets the command pool and stack
    def createActions(self):    

        backAction = QAction(QIcon(":/back.png"), "&Back", self)
        backAction.setShortcut(QKeySequence.Back)

        forwardAction = QAction(QIcon(":/forward.png"), "&Forward", self)
        forwardAction.setShortcut("Forward")

        homeAction = QAction(QIcon(":/home.png"), "&Home", self)
        homeAction.setShortcut("Home")

        ## main label of the help
        self.pageLabel = QLabel()

        self.toolBar.addAction(backAction)
        self.toolBar.addAction(forwardAction)
        self.toolBar.addAction(homeAction)
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.pageLabel)

        self.connect(
            backAction, SIGNAL("triggered()"),
            self.textBrowser, SLOT("backward()"))
        self.connect(
            forwardAction, SIGNAL("triggered()"),
            self.textBrowser, SLOT("forward()"))
        self.connect(
            homeAction, SIGNAL("triggered()"),
            self.textBrowser, SLOT("home()"))
        self.connect(
            self.textBrowser, SIGNAL("sourceChanged(QUrl)"),
            self.updatePageTitle)



    ## updates the title page
    # \brief It resets the pageLabel withg the document title
    def updatePageTitle(self):
        self.pageLabel.setText(
            "<p><b><i><font color='#0066ee' font size = 4>" +
            "&nbsp;&nbsp;" + self.textBrowser.documentTitle() 
            + "</i></b></p></br>"
            )


if __name__ == "__main__":
    import sys
    ## application instance
    app = QApplication(sys.argv)
    ## help form
    form = HelpForm("index.html")
    form.show()
    app.exec_()

