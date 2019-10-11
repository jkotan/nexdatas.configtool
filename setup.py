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
from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.command.clean import clean
from distutils.util import get_platform
import shutil

try:
    from sphinx.setup_command import BuildDoc
except Exception:
    BuildDoc = None


#: package name
TOOL = "nxsconfigtool"
#: package instance
ITOOL = __import__(TOOL)


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

needs_pytest = set(['test']).intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

install_requires = [
    'nxstools',
    # 'pyqt5',
    # 'pytango',
]


class toolBuild(build_py):
    """ ui and qrc builder for python
    """

    @classmethod
    def makeqrc(cls, qfile, path):
        """  creates the python qrc files

        :param qfile: qrc file name
        :param path:  qrc file path
        """
        qrcfile = os.path.join(path, "%s.qrc" % qfile)
        rccfile = os.path.join(path, "%s.rcc" % qfile)

        compiled = os.system("rcc %s -o %s -binary" % (qrcfile, rccfile))
        if compiled == 0:
            print("Built: %s -> %s" % (qrcfile, rccfile))
        else:
            sys.stderr.write("Error: Cannot build  %s\n" % (rccfile))
            sys.stderr.flush()

    def run(self):
        """ runner

        :\brief: It is running during building
        """
        try:
            qfiles = [(qfile[:-4], QRCDIR) for qfile
                      in os.listdir(QRCDIR) if qfile.endswith('.qrc')]
            for qrc in qfiles:
                if not qrc[0] in (".", ".."):
                    self.makeqrc(qrc[0], qrc[1])
        except TypeError:
            sys.stderr.write("No .qrc files to build\n")
            sys.stderr.flush()

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                shutil.copy(script, script + ".pyw")
        build_py.run(self)


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

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                if os.path.exists(script + ".pyw"):
                    os.remove(script + ".pyw")
        clean.run(self)


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

#: (:obj:`dict` <:obj:`str`, :obj:`list` <:obj:`str`> > ) package data
package_data = {
    'nxsconfigtool': ['ui/*.ui', 'qrc/*.rcc']
}


#: metadata for distutils
SETUPDATA = dict(
    name="nxsconfigtool",
    version=ITOOL.__version__,
    author="Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email="jankotan@gmail.com, eugen.wintersberger@gmail.com, "
    + "halil.pasic@gmail.com",
    maintainer="Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    maintainer_email="jankotan@gmail.com, eugen.wintersberger@gmail.com, "
    "halil.pasic@gmail.com",
    description=("Configuration tool  for creating components"),
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords="configuration writer Tango component nexus data",
    url="https://github.com/nexdatas/configtool/",
    install_requires=install_requires,
    platforms=("Linux", "Windows", "MacOS"),
    packages=[TOOL, QRCDIR],
    package_data=package_data,
    scripts=get_scripts(SCRIPTS),
    zip_safe=False,
    setup_requires=pytest_runner,
    tests_require=['pytest'],
    cmdclass={
        "build_py": toolBuild,
        "clean": toolClean,
        "build_sphinx": BuildDoc
    },
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release)}},
    long_description=read('README.rst')
)


def main():
    """ the main function

    """
    setup(**SETUPDATA)


if __name__ == '__main__':
    main()
