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
#

""" setup.py for NXS Component Designer """

import os
import sys
from distutils.util import get_platform
from distutils.core import setup, Command
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install_scripts import install_scripts
import shutil

#: package name
TOOL = "nxsconfigtool"
#: package instance
ITOOL = __import__(TOOL)

from sphinx.setup_command import BuildDoc

def read(fname):
    """ read the file 

    :param fname: readme file name
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#: ui directory
UIDIR = os.path.join(TOOL, "ui")
#: qrc directory
QRCDIR = os.path.join(TOOL, "qrc")
#: executable scripts
SCRIPTS = ['nxsdesigner']


class toolBuild(build):
    """ ui and qrc builder for python
    """

    @classmethod
    def makeqrc(cls, qfile, path):
        """  creates the python qrc files
        
        :param qfile: qrc file name
        :param path:  qrc file path
        """
        qrcfile = os.path.join(path, "%s.qrc" % qfile)
        pyfile = os.path.join(path, "qrc_%s.py" % qfile)

        compiled = os.system("pyrcc4 %s -o %s" % (qrcfile, pyfile))
        if compiled == 0:
            print "Built: %s -> %s" % (qrcfile, pyfile)
        else:
            print >> sys.stderr, "Error: Cannot build  %s" % (pyfile)

    @classmethod
    def makeui(cls, ufile, path):
        """ creates the python ui files

        :param ufile: ui file name
        :param path:  ui file path
        """
        uifile = os.path.join(path, "%s.ui" % ufile)
        pyfile = os.path.join(path, "ui_%s.py" % ufile)
        compiled = os.system("pyuic4 %s -o %s" % (uifile, pyfile))
        if compiled == 0:
            print "Compiled %s -> %s" % (uifile, pyfile)
        else:
            print >> sys.stderr,  "Error: Cannot build %s" % (pyfile)

    def run(self):
        """ runner

        :\brief: It is running during building
        """
        try:
            ufiles = [(ufile[:-3], UIDIR) for ufile
                      in os.listdir(UIDIR) if ufile.endswith('.ui')]
            for ui in ufiles:
                if not ui[0] in (".", ".."):
                    self.makeui(ui[0], ui[1])
        except TypeError as e:
            print >> sys.stderr, "No .ui files to build", e

        try:
            qfiles = [(qfile[:-4], QRCDIR) for qfile
                      in os.listdir(QRCDIR) if qfile.endswith('.qrc')]
            for qrc in qfiles:
                if not qrc[0] in (".", ".."):
                    self.makeqrc(qrc[0], qrc[1])
        except TypeError:
            print >> sys.stderr, "No .qrc files to build"

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                shutil.copy(script, script + ".pyw")
        build.run(self)


class toolClean(clean):
    """ cleaner for python
    """
    
    def run(self):
        """ runner
        
        :brief: It is running during cleaning
        """

        cfiles = [os.path.join(TOOL, cfile) for cfile
                  in os.listdir("%s" % TOOL) if cfile.endswith('.pyc')]
        for fl in cfiles:
            os.remove(str(fl))

        cfiles = [os.path.join(UIDIR, cfile) for cfile
                  in os.listdir(UIDIR) if cfile.endswith('.pyc') or
                  (cfile.endswith('.py')
                   and cfile.endswith('__init_.py'))]
        for fl in cfiles:
            os.remove(str(fl))

        cfiles = [os.path.join(QRCDIR, cfile) for cfile
                  in os.listdir(QRCDIR) if cfile.endswith('.pyc')
                  or (cfile.endswith('.py')
                      and cfile.endswith('__init_.py'))]
        for fl in cfiles:
            os.remove(str(fl))

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                if os.path.exists(script + ".pyw"):
                    os.remove(script + ".pyw")
        clean.run(self)


class TestCommand(Command):
    """ test command class
    """
    
    #: user options
    user_options = []

    #: initializes options
    def initialize_options(self):
        pass

    #: finalizes options
    def finalize_options(self):
        pass
    
    #: runs command
    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'test/runtest.py'])
        raise SystemExit(errno)


def get_scripts(scripts):
    """ provides windows names of python scripts

    :param scripts: list of script names
    """
    if get_platform()[:3] == 'win':
        return scripts + [sc + '.pyw' for sc in scripts]
    return scripts

release = ITOOL.__version__
version = ".".join(release.split(".")[:2])
name = "NXS Component Designer"



#: metadata for distutils
SETUPDATA = dict(
    name="nexdatas.configtool",
    version=ITOOL.__version__,
    author="Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email="jankotan@gmail.com, eugen.wintersberger@gmail.com, "
    + "halil.pasic@gmail.com",
    maintainer="Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    maintainer_email="jankotan@gmail.com, eugen.wintersberger@gmail.com, "
    "halil.pasic@gmail.com",
    description=("Configuration tool  for creating components"),
    license=read('COPYRIGHT'),
    keywords="configuration writer Tango component nexus data",
    url="https://github.com/jkotan/nexdatas/",
    platforms=("Linux", " Windows", " MacOS "),
    packages=[TOOL, UIDIR, QRCDIR],
    scripts=get_scripts(SCRIPTS),
    cmdclass={"build": toolBuild, "clean": toolClean,
              "test": TestCommand, 'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release)}},
    long_description=read('README.rst')
)


def main():
    """ the main function 

    additionally:

    find ./nxsconfigtool/help/ -iname "*.html" -type f -exec sh -c 'pandoc "${0}" -t rst -o "doc/nxs$(basename ${0%.html}.rst)"' {} \;

    """
    setup(**SETUPDATA)

if __name__ == '__main__':
    main()
