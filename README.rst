Welcome to nxsconfigtool's documentation!
=========================================

Authors: Jan Kotanski, Eugen Wintersberger, Halil Pasic

Component Designer is a GUI configuration tool dedicated to create components
as well as datasources which constitute the XML configuration strings of
Nexus Data Writer (NXS). The created XML elements can be saved
in the extended Nexus XML format in Configuration Tango Server or in disk files.

| Source code: https://github.com/nexdatas/configtool
| Web page: https://nexdatas.github.io/configtool/
| NexDaTaS Web page: https://nexdatas.github.io

------------
Installation
------------

Install the dependencies:

|    PyQt4, PyTango (optional)

PyTango is only needed if one wants to use Configuration Server

From sources
^^^^^^^^^^^^

Download the latest NXS Configuration Tool version from

|    https://github.com/nexdatas/configtool/

and extract the sources.

One can also download the lastest version directly from the git repository by

git clone https://github.com/jkotan/nexdatas.configtool/

Next, run the installation script

.. code-block:: console

	  $ python setup.py install

and launch

.. code-block:: console

	  $ nxsdesigner

Debian packages
^^^^^^^^^^^^^^^

Debian Buster, Stretch or Ubuntu Focal, Bionic packages can be found in the HDRI repository.

To install the debian packages, add the PGP repository key

.. code-block:: console

	  $ sudo su
	  $ wget -q -O - http://repos.pni-hdri.de/debian_repo.pub.gpg | apt-key add -

and then download the corresponding source list

.. code-block:: console

	  $ cd /etc/apt/sources.list.d
	  $ wget http://repos.pni-hdri.de/buster-pni-hdri.list

Finally,

.. code-block:: console

	  $ apt-get update
	  $ apt-get install nxsconfigtool

To instal other NexDaTaS packages

.. code-block:: console

	  $ apt-get install python-nxswriter python-nxsconfigserver nxsconfigserver-db nxstools

and

.. code-block:: console

	  $ apt-get install python-nxsrecselector nxselector python-sardana-nxsrecorder

for Component Selector and Sardana related packages.

From pip
^^^^^^^^

To install it from pip you need to install pyqt5, e.g.

.. code-block:: console

   $ python3 -m venv myvenv
   $ . myvenv/bin/activate

   $ pip install pyqt5
   $ pip install nxsconfigtool

Moreover it is also good to install

.. code-block:: console

   $ pip install pytango


General overview
================


   Component Designer

.. image:: https://github.com/nexdatas/configtool/blob/develop/doc/png/designer2.png?raw=true

The **NXS Component** Designer program allows to creates *components* as well as
*datasources* which constitute the XML configuration strings of
Nexus Data Writer (NXS). The created XML elements can be saved
in the extended Nexus XML format in Configuration Tango Server or in disk files.

Collection Dock Window contains lists of the currently open components
and datasources. Selecting one of the components or datasources from
the lists causes opening either Component Window or DataSource Window.

All the most commonly used menu options are also available on Toolbar.

A short description of all actions can be found in **Help** menu.


Icons
=====

Icons fetched from http://findicons.com/pack/990/vistaico_toolbar.
